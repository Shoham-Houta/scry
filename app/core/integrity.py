"""Forensic integrity guarantees.

Hash inputs (sha256) at ingest, enforce read-only handling of originals
(never mutate the source file), and maintain a per-case audit log of every
command run. Backbone for chain-of-custody.
"""

from datetime import datetime, timezone
import hashlib, json
from app.core.evidence import Artifact
from pathlib import Path
from magic import from_file


def hash_file(path: Path) -> str:
    with open(path, 'rb') as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def ingest(path: Path, case_dir: Path) -> Artifact:
    if not path.is_file():
        raise FileNotFoundError(f"evidence file not found: {path}")

    sha = hash_file(path)
    size = path.stat().st_size
    mime = from_file(str(path), mime=True)
    audit(case_dir, "ingest", path=str(path), sha256=sha, size=size, mime=mime)
    return Artifact(path, sha, size, mime)


def audit(case_dir: Path, event: str, **fields) -> None:
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **fields,
    }
    case_dir.mkdir(parents=True, exist_ok=True)
    with (case_dir / 'audit.log').open('a', encoding='utf-8') as f:
        f.write((json.dumps(record) + '\n'))
