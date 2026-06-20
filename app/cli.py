"""scry command-line entry point.

Primary interface. Planned commands:
    scry scan <path> [-o report.json]   # run extractors + enrichers on a file/dir
    scry tools                          # list base tools and availability

Implementation left to you.
"""
import argparse, re
from datetime import datetime, timezone
from pathlib import Path
import yaml

from app.core.evidence import Artifact
from app.core.integrity import ingest, audit
from app.core.dispatcher import dispatch
from app.report.json_report import write_report


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_config():
    return yaml.safe_load((PROJECT_ROOT / "config" / "config.yaml").read_text())


def resolve_case_name(case_name: str | None) -> str:
    case_name = case_name or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    if case_name in {".", ".."} or not re.fullmatch(r"[A-Za-z0-9._-]+", case_name):
        raise SystemExit(f"Invalid case name: {case_name!r}")
    return case_name


def scan(paths: list[Path], case_dir: Path) -> list[Artifact]:
    artifacts = []
    for path in paths:
        try:
            artifact = ingest(path, case_dir)
        except (FileNotFoundError, PermissionError) as e:
            audit(case_dir, "ingest_failed", path=str(path), error=str(e))
            print(f"Skip {path}: {e}")
            continue
        artifacts.append(dispatch(artifact))
    return artifacts


def main():
    ap = argparse.ArgumentParser(prog="scry")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sc = sub.add_parser("scan", help="scan a directory of artifacts")
    sc.add_argument("paths", nargs="+", type=Path)
    sc.add_argument("-o", "--output", default="report.json", type=Path)
    sc.add_argument("-c", "--case-name", default=None, type=str)
    args = ap.parse_args()

    cfg = load_config()
    base = Path(cfg["output"]["dir"])
    if not base.is_absolute():
        base = PROJECT_ROOT / base                 # anchor relative dir
    case = resolve_case_name(args.case_name)
    case_dir = (base / case).resolve()
    case_dir.mkdir(parents=True, exist_ok=True)

    artifacts = scan(args.paths, case_dir)
    write_report(artifacts, case_dir / args.output, case)
    print(f"scanned {len(artifacts)} file(s) → {case_dir / args.output}")


if __name__ == "__main__":
    main()
