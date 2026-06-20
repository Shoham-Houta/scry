"""Canonical JSON report.

Serializes Artifacts (findings + provenance + hashes) to machine-readable
JSON. The primary v1 output; HTML/timeline reporting comes later.
"""
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from app.core.evidence import Artifact


def _encode(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Path):
        return str(obj)
    raise TypeError(f"Not JSON serializable: {type(obj).__name__}")


def to_json(artifacts: list[Artifact], case: str, indent: int = 2) -> str:
    report = {
        "case": case,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tool": "scry",
        "artifact_count": len(artifacts),
        "artifacts": [asdict(a) for a in artifacts],
    }
    return json.dumps(report, default=_encode, indent=indent)


def write_report(artifacts: list[Artifact], out_path: Path, case: str, indent: int = 2) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(to_json(artifacts, case, indent),encoding="utf-8")
