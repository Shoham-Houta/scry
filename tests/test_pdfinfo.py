"""Tests for the pdfinfo PDF extractor.

PATTERN-SETTER for the rest of the suite. Two tiers:
  * pure tests (categorizer/parser) -- deterministic, need no external tool
  * integration test (extract) -- skipped when poppler is not installed

NOTE: the `_parse` tests assume `_parse(stdout) -> list[Finding]` is pure
(version moved into `extract()`). If `_parse` still shells out for the
version, these tests transitively need poppler -- apply that small refactor
to drop the hidden dependency.
"""
from pathlib import Path
from shutil import which

import pytest

from app.core.evidence import Category, Finding
from app.extractors.pdfinfo import PDFInfoExtractor


@pytest.fixture
def extractor() -> PDFInfoExtractor:
    return PDFInfoExtractor()


# --- routing ---------------------------------------------------------------

def test_handles_only_pdf(extractor):
    assert extractor.handles("application/pdf") is True
    assert extractor.handles("image/jpeg") is False
    assert extractor.handles("text/plain") is False


# --- categorizer (pure) ----------------------------------------------------

@pytest.mark.parametrize("key, value, expected", [
    ("CreationDate", "2026:03:22 14:48:02", Category.TIMESTAMP),
    ("ModDate",      "2026:03:22 14:48:02", Category.TIMESTAMP),
    ("Author",       "Shoham Houta",    Category.AUTHOR),
    ("Creator",      "Canva",           Category.DEVICE),    # software, not a person
    ("Producer",     "Skia/PDF",        Category.DEVICE),
    ("JavaScript",   "yes",             Category.LEAD),
    ("Encrypted",    "yes",             Category.LEAD),
    ("Suspects",     "yes",             Category.LEAD),
    ("JavaScript",   "no",              Category.OTHER),     # value-filter: not a lead
    ("Encrypted",    "no",              Category.OTHER),
    ("Suspects",     "no",              Category.OTHER),
    ("Title",        "Invoice",         Category.OTHER),
    ("Pages",        "3",               Category.OTHER),
])
def test_categorizer(extractor, key, value, expected):
    assert extractor._categorizer(key, value) == expected


# --- parse (pure: str -> list[Finding]) ------------------------------------

def test_parse_builds_findings(extractor, pdfinfo_clean):
    findings = extractor._parse(pdfinfo_clean)
    assert findings, "expected at least one finding"
    assert all(isinstance(f, Finding) for f in findings)
    assert all(f.source_tool == "pdfinfo" for f in findings)


def test_parse_preserves_colon_in_value(extractor, pdfinfo_clean):
    """maxsplit=1: a timestamp's internal colons must survive intact."""
    values = {f.key: f.value for f in extractor._parse(pdfinfo_clean)}
    assert values["CreationDate"] == "Thu Apr 23 12:40:27 2026 IDT"


def test_parse_skips_colonless_lines(extractor):
    stdout = "Author: alice\nthis line has no colon\nPages: 2\n"
    values = {f.key: f.value for f in extractor._parse(stdout)}
    assert values == {"Author": "alice", "Pages": "2"}


def test_parse_lead_findings(extractor, pdfinfo_lead):
    leads = {f.key for f in extractor._parse(pdfinfo_lead) if f.category == Category.LEAD}
    assert leads == {"JavaScript", "Encrypted", "Suspects"}


# --- integration (needs poppler) -------------------------------------------

@pytest.mark.integration
@pytest.mark.skipif(which("pdfinfo") is None, reason="poppler not installed")
def test_extract_real_pdf(extractor):
    pdf = Path(__file__).parent / "fixtures" / "file.pdf"
    if not pdf.is_file():
        pytest.skip("sample PDF not present")
    findings, prov = extractor.extract(pdf)
    assert prov.tool == "pdfinfo"
    assert prov.return_code == 0
    assert prov.version and prov.version != "Unknown"
    assert "Producer" in {f.key for f in findings}
