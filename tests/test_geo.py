"""Tests for the GeoLocation enricher.

All pure -- the enricher is offline DMS->decimal math over Findings, so no
external tool or network is involved. We feed synthetic Artifacts whose
findings mimic exiftool's Composite:GPSPosition output.
"""
from pathlib import Path

import pytest

from app.core.evidence import Artifact, Category, Finding
from app.enrichers.geo import GeoLocationEnricher, _to_decimal


@pytest.fixture
def enricher() -> GeoLocationEnricher:
    return GeoLocationEnricher()


def _artifact(*findings: Finding) -> Artifact:
    return Artifact(
        path=Path("image.jpeg"), sha256="0" * 64, size=1,
        mime="image/jpeg", findings=list(findings),
    )


def _gps_position(value: str, confidence: float = 1.0) -> Finding:
    return Finding(
        key="Composite:GPSPosition", value=value,
        source_tool="exiftool", category=Category.GPS, confidence=confidence,
    )


# --- DMS -> decimal (pure) -------------------------------------------------

@pytest.mark.parametrize("deg, minutes, sec, ref, expected", [
    (31, 22, 45.01, "N",  31.379169),
    (34, 37, 23.26, "E",  34.623128),
    (31, 22, 45.01, "S", -31.379169),   # southern hemisphere negates
    (34, 37, 23.26, "W", -34.623128),   # western hemisphere negates
    (0,  0,  0,     "N",   0.0),
])
def test_to_decimal(deg, minutes, sec, ref, expected):
    assert _to_decimal(deg, minutes, sec, ref) == pytest.approx(expected, abs=1e-5)


# --- applies ---------------------------------------------------------------

def test_applies_true_when_gps_present(enricher):
    art = _artifact(_gps_position("31 deg 22' 45.01\" N, 34 deg 37' 23.26\" E"))
    assert enricher.applies(art) is True


def test_applies_false_without_gps(enricher):
    art = _artifact(Finding(key="Text", value="hi", source_tool="x", category=Category.TEXT))
    assert enricher.applies(art) is False


# --- enrich ----------------------------------------------------------------

def test_enrich_converts_position(enricher):
    art = _artifact(_gps_position("31 deg 22' 45.01\" N, 34 deg 37' 23.26\" E"))
    out = enricher.enrich(art)

    assert len(out) == 1
    f = out[0]
    assert f.key == "GPSDecimal"
    assert f.category == Category.GPS
    assert f.source_tool == "GeoLocation"

    lat, lng = (float(x) for x in f.value.split(","))
    assert lat == pytest.approx(31.379169, abs=1e-5)
    assert lng == pytest.approx(34.623128, abs=1e-5)


def test_enrich_propagates_confidence(enricher):
    """reliability is 1.0 for this deterministic enricher, so the derived
    finding inherits the source confidence unchanged."""
    art = _artifact(_gps_position("31 deg 22' 45.01\" N, 34 deg 37' 23.26\" E", confidence=0.8))
    out = enricher.enrich(art)
    assert out[0].confidence == pytest.approx(0.8)


def test_enrich_returns_empty_without_position(enricher):
    """A GPS-category finding that isn't Composite:GPSPosition must not crash
    the splitter -- the guard returns []."""
    art = _artifact(Finding(
        key="EXIF:GPSLatitude", value="31 deg 22' 45.01\"",
        source_tool="exiftool", category=Category.GPS,
    ))
    assert enricher.enrich(art) == []
