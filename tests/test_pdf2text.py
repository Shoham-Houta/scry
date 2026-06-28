"""Tests for the pdftotext PDF body-text extractor.

Two tiers:
  * pure tests (extract with `run` monkeypatched) -- deterministic, no poppler
  * integration test (extract) -- skipped when poppler is not installed

The pure tests also guard the forensic invariant that bit us once: the argv
MUST end in ``-`` so pdftotext writes to stdout instead of dropping a .txt
file next to the (read-only) evidence.
"""
from datetime import datetime, timezone
from pathlib import Path
from shutil import which

import pytest

from app.core.evidence import Category, Finding
from app.core.runner import RunResult
from app.extractors.pdf2text import PDF2TextExtractor


@pytest.fixture
def extractor() -> PDF2TextExtractor:
    return PDF2TextExtractor()


def _fake_run(stdout: str = "", stderr: str = "", rc: int = 0):
    """Stand-in for runner.run. extract() shells out twice (text + -v probe),
    so branch on argv: the version probe returns a version banner on stderr,
    the real call returns the supplied stdout/return code."""
    def _run(argv, *, timeout):
        if "-v" in argv:
            return RunResult(
                argv=tuple(argv), return_code=0,
                stdout="", stderr="pdftotext version 24.04.0\n",
                started_at=datetime.now(timezone.utc), duration_s=0.01,
            )
        return RunResult(
            argv=tuple(argv), return_code=rc,
            stdout=stdout, stderr=stderr,
            started_at=datetime.now(timezone.utc), duration_s=0.01,
        )
    return _run


# --- routing ---------------------------------------------------------------

def test_handles_only_pdf(extractor):
    assert extractor.handles("application/pdf") is True
    assert extractor.handles("image/jpeg") is False
    assert extractor.handles("text/plain") is False


# --- extract (pure: run monkeypatched) -------------------------------------

def test_extract_builds_text_finding(extractor, monkeypatch):
    monkeypatch.setattr("app.extractors.pdf2text.run", _fake_run(stdout="hello world"))
    findings, prov = extractor.extract(Path("evidence.pdf"))

    assert len(findings) == 1
    f = findings[0]
    assert isinstance(f, Finding)
    assert f.key == "Text"
    assert f.value == "hello world"
    assert f.category == Category.TEXT
    assert f.source_tool == "pdftotext"


def test_extract_provenance(extractor, monkeypatch):
    monkeypatch.setattr("app.extractors.pdf2text.run", _fake_run(stdout="x"))
    _, prov = extractor.extract(Path("evidence.pdf"))

    assert prov.tool == "pdftotext"
    assert prov.return_code == 0
    assert prov.version == "24.04.0"


def test_extract_writes_to_stdout_not_disk(extractor, monkeypatch):
    """Forensic guard: argv must pass '-' so poppler streams to stdout instead
    of writing a .txt beside the original evidence file."""
    monkeypatch.setattr("app.extractors.pdf2text.run", _fake_run(stdout="x"))
    _, prov = extractor.extract(Path("evidence.pdf"))

    assert prov.argv[-1] == "-"
    assert "-layout" in prov.argv


def test_extract_raises_on_nonzero_exit(extractor, monkeypatch):
    monkeypatch.setattr("app.extractors.pdf2text.run", _fake_run(stderr="boom", rc=1))
    with pytest.raises(RuntimeError, match="boom"):
        extractor.extract(Path("evidence.pdf"))


def test_extract_tolerates_stderr_warnings(extractor, monkeypatch):
    """poppler emits Syntax Warnings on stderr with rc 0 -- those are NOT
    failures; only a nonzero exit code is."""
    monkeypatch.setattr(
        "app.extractors.pdf2text.run",
        _fake_run(stdout="body", stderr="Syntax Warning: ...", rc=0),
    )
    findings, _ = extractor.extract(Path("evidence.pdf"))
    assert findings[0].value == "body"


# --- integration (needs poppler) -------------------------------------------

@pytest.mark.integration
@pytest.mark.skipif(which("pdftotext") is None, reason="poppler not installed")
def test_extract_real_pdf(extractor):
    pdf = Path(__file__).parent / "fixtures" / "file.pdf"
    if not pdf.is_file():
        pytest.skip("sample PDF not present")
    findings, prov = extractor.extract(pdf)
    assert prov.tool == "pdftotext"
    assert prov.return_code == 0
    assert prov.version and prov.version != "Unknown"
    assert findings and findings[0].key == "Text"
