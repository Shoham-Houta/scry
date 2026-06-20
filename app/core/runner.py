"""Safe execution of external base tools.

Wraps subprocess calls to exiftool / pdfinfo / etc. with: no shell, explicit
argv, per-tool timeout, captured stdout+stderr, and a recorded exit code.
Returns enough detail for Provenance (argv, version, duration, return code).
"""

from dataclasses import dataclass
from datetime import datetime, timezone

import subprocess as sp
import time

@dataclass(frozen=True)
class RunResult:
    argv:           tuple[str, ...]     # Execution arguments (i.e. tool,flags,etc...)
    return_code:    int                 # Process exit code
    stdout:         str                 # Standard output stream
    stderr:         str                 # Standard error stream
    duration_s:     float               # Total run time in seconds
    started_at:     datetime            # UTC timestamp when the process started


def run(argv: list[str], *, timeout: float) -> RunResult:
    started_at: datetime = datetime.now(tz=timezone.utc)
    t0: float = time.monotonic()
    try:
        process: sp.CompletedProcess[str] = sp.run(
                args=argv,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                check=False         # nonzero exit code is data, not an exception
                )
        return_code, stdout, stderr = process.returncode, process.stdout, process.stderr
    except sp.TimeoutExpired as e:
        # child already killed by subprocess, e holds whatever was captured
        return_code = -1
        stdout = e.stdout
        note = f"scry timed out after {timeout}s"
        captured = _as_text(e.stderr)
        stderr = f"{captured}\n{note}" if captured else note
    except (FileNotFoundError, PermissionError) as e:
        return_code = -2
        stdout = ""
        stderr = f"scry: cannot run executable {argv[0]!r}: {e}"
    return RunResult(
            argv=tuple(argv),
            return_code=return_code,
            stdout=_as_text(stdout),
            stderr=_as_text(stderr),
            started_at=started_at,
            duration_s=time.monotonic()-t0
            )

def _as_text(x: str | bytes | None) -> str:
    if x is None:
        return ""
    return x if isinstance(x, str) else x.decode("utf-8", "replace")
