"""Tests for the canonical JSON report.

Pure (no tools): build an Artifact in memory, serialize, and assert the
shape round-trips. The tricky bits are the custom `_encode` hook -- datetime
and Path are not JSON-native, and anything else must raise -- plus that
write_report lands valid JSON on disk.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.core.evidence import Artifact, Category, Finding, Provenance
from app.report.json_report import _encode, to_json, write_report


@pytest.fixture
def artifact() -> Artifact:
    """One fully-populated Artifact (finding + provenance with a datetime)."""
    prov = Provenance(
        tool="exiftool", version="13.55", argv=("exiftool", "-j"),
        return_code=0, started_at=datetime(2026, 6, 22, 12, 0, tzinfo=timezone.utc),
        duration_s=0.12,
    )
    finding = Finding("EXIF:Model", "iPhone 16 Plus", "exiftool", Category.DEVICE, 1.0)
    return Artifact(
        path=Path("/cases/IMG_9367.jpeg"), sha256="0" * 64, size=42,
        mime="image/jpeg", findings=[finding], provenance=[prov],
    )


# --- _encode (custom JSON hook) --------------------------------------------

def test_encode_datetime_to_isoformat():
    dt = datetime(2026, 6, 22, 12, 0, tzinfo=timezone.utc)
    assert _encode(dt) == dt.isoformat()


def test_encode_path_to_str():
    assert _encode(Path("/a/b.jpg")) == "/a/b.jpg"


def test_encode_unknown_type_raises():
    with pytest.raises(TypeError):
        _encode(object())


# --- to_json ---------------------------------------------------------------

def test_to_json_is_valid_and_has_envelope(artifact):
    report = json.loads(to_json([artifact], case="case-001"))
    assert report["case"] == "case-001"
    assert report["tool"] == "scry"
    assert report["artifact_count"] == 1
    assert "generated_at" in report
    assert len(report["artifacts"]) == 1


def test_to_json_serializes_nested_datetime_and_path(artifact):
    """The Provenance datetime and the Path must survive via _encode."""
    art = json.loads(to_json([artifact], case="c"))["artifacts"][0]
    assert art["path"] == "/cases/IMG_9367.jpeg"
    assert art["provenance"][0]["started_at"] == "2026-06-22T12:00:00+00:00"
    assert art["findings"][0]["key"] == "EXIF:Model"


def test_to_json_artifact_count_matches(artifact):
    report = json.loads(to_json([artifact, artifact], case="c"))
    assert report["artifact_count"] == 2
    assert len(report["artifacts"]) == 2


def test_to_json_empty_list():
    report = json.loads(to_json([], case="empty"))
    assert report["artifact_count"] == 0
    assert report["artifacts"] == []


# --- write_report ----------------------------------------------------------

def test_write_report_writes_valid_json(tmp_path, artifact):
    out = tmp_path / "out" / "report.json"  # parent does not exist yet
    write_report([artifact], out, case="case-001")
    assert out.is_file()
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["case"] == "case-001"
    assert report["artifacts"][0]["sha256"] == "0" * 64


def test_write_report_delegates_to_to_json(tmp_path, artifact):
    """File content equals to_json output, ignoring the wall-clock timestamp."""
    out = tmp_path / "report.json"
    write_report([artifact], out, case="c")
    written = json.loads(out.read_text(encoding="utf-8"))
    expected = json.loads(to_json([artifact], case="c"))
    written.pop("generated_at"), expected.pop("generated_at")
    assert written == expected
