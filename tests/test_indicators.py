"""Tests for the Indicator enricher.

Pure: the enricher regex-scans a TEXT finding's value for emails / URLs /
IPv4 / phone numbers. phonenumbers is a hard import of the module under test
(bundles its own metadata, so still offline), hence the phone tests need no
network and no skip guard.
"""
from pathlib import Path

import pytest

from app.core.evidence import Artifact, Category, Finding
from app.enrichers.indicators import (
    IndicatorEnricher,
    match_text,
    patterns,
    valid_ipv4,
)


@pytest.fixture
def enricher() -> IndicatorEnricher:
    return IndicatorEnricher()


def _artifact(text: str | None) -> Artifact:
    findings = []
    if text is not None:
        findings.append(Finding(
            key="Text", value=text,
            source_tool="pdftotext", category=Category.TEXT,
        ))
    return Artifact(
        path=Path("doc.pdf"), sha256="0" * 64, size=1,
        mime="application/pdf", findings=findings,
    )


def _by_key(findings: list[Finding]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for f in findings:
        out.setdefault(f.key, []).append(f.value)
    return out


# --- helpers (pure) --------------------------------------------------------

@pytest.mark.parametrize("ip, ok", [
    ("192.168.1.1",     True),
    ("10.0.0.0",        True),
    ("255.255.255.255", True),
    ("256.1.1.1",       False),   # octet > 255
    ("1.2.3.999",       False),
])
def test_valid_ipv4(ip, ok):
    assert valid_ipv4(ip) is ok


def test_match_text_email():
    pattern = patterns["email"][0]
    assert match_text("ping me at a.b@example.com please", pattern) == ["a.b@example.com"]


# --- applies ---------------------------------------------------------------

def test_applies_true_with_text(enricher):
    assert enricher.applies(_artifact("anything")) is True


def test_applies_false_without_text(enricher):
    assert enricher.applies(_artifact(None)) is False


# --- enrich ----------------------------------------------------------------

def test_enrich_extracts_each_type(enricher):
    text = "mail john@corp.com or visit https://corp.com from 10.20.30.40"
    out = _by_key(enricher.enrich(_artifact(text)))

    assert out["email"] == ["john@corp.com"]
    assert out["url"] == ["https://corp.com"]
    assert out["ipv4"] == ["10.20.30.40"]


def test_enrich_category_is_indicator(enricher):
    out = enricher.enrich(_artifact("x@y.com"))
    assert all(f.category == Category.INDICATOR for f in out)


def test_enrich_filters_invalid_ipv4(enricher):
    out = _by_key(enricher.enrich(_artifact("not an ip: 256.300.1.1")))
    assert "ipv4" not in out


def test_enrich_strips_trailing_punctuation_from_url(enricher):
    out = _by_key(enricher.enrich(_artifact("see https://example.com/path.")))
    assert out["url"] == ["https://example.com/path"]


def test_enrich_dedups_repeats(enricher):
    out = _by_key(enricher.enrich(_artifact("a@b.com and again a@b.com")))
    assert out["email"] == ["a@b.com"]


def test_enrich_confidence_compounds(enricher):
    """confidence = source.confidence * reliability * pattern_confidence.
    email pattern_confidence is 0.9; source and reliability are 1.0."""
    out = enricher.enrich(_artifact("a@b.com"))
    email = next(f for f in out if f.key == "email")
    assert email.confidence == pytest.approx(1.0 * enricher.reliability * 0.9)


def test_enrich_returns_empty_without_text(enricher):
    assert enricher.enrich(_artifact(None)) == []


# --- phone numbers (libphonenumber) ----------------------------------------

def test_enrich_normalizes_phone_to_e164(enricher):
    out = _by_key(enricher.enrich(_artifact("call +972-50-213-7818 today")))
    assert out["phone"] == ["+972502137818"]


def test_enrich_valid_phone_high_confidence(enricher):
    phone = next(f for f in enricher.enrich(_artifact("+972-50-213-7818")) if f.key == "phone")
    assert phone.confidence == pytest.approx(0.85)
