"""Tests for forensic integrity: hashing, ingest, and the audit log.

All pure/filesystem -- no external tools. `case_dir` (from conftest) gives
each test an isolated directory so the audit log never leaks between tests.
sha256 is checked against a known NIST vector so the test doesn't just
re-implement the function it's verifying.
"""
import json
from pathlib import Path

import pytest

from app.core.evidence import Artifact
from app.core.integrity import audit, hash_file, ingest


# NIST test vector: sha256(b"abc")
ABC_SHA256 = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


# --- hash_file (pure) ------------------------------------------------------

def test_hash_file_known_digest(tmp_path):
    f = tmp_path / "abc.txt"
    f.write_bytes(b"abc")
    assert hash_file(f) == ABC_SHA256


def test_hash_file_is_stable(tmp_path):
    f = tmp_path / "blob.bin"
    f.write_bytes(b"forensic evidence")
    assert hash_file(f) == hash_file(f)


# --- ingest ----------------------------------------------------------------

def test_ingest_missing_file_raises(tmp_path, case_dir):
    missing = tmp_path / "ghost.jpg"
    with pytest.raises(FileNotFoundError):
        ingest(missing, case_dir)


def test_ingest_no_audit_when_file_missing(tmp_path, case_dir):
    """A failed ingest must not leave a custody record."""
    with pytest.raises(FileNotFoundError):
        ingest(tmp_path / "ghost.jpg", case_dir)
    assert not (case_dir / "audit.log").exists()


def test_ingest_builds_artifact(tmp_path, case_dir):
    f = tmp_path / "abc.txt"
    f.write_bytes(b"abc")
    art = ingest(f, case_dir)
    assert isinstance(art, Artifact)
    assert art.path == f
    assert art.sha256 == ABC_SHA256
    assert art.size == 3
    assert "/" in art.mime  # libmagic returned a real mime type
    assert art.findings == [] and art.provenance == [] and art.errors == []


def test_ingest_writes_audit_record(tmp_path, case_dir):
    f = tmp_path / "abc.txt"
    f.write_bytes(b"abc")
    ingest(f, case_dir)
    lines = (case_dir / "audit.log").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec["event"] == "ingest"
    assert rec["sha256"] == ABC_SHA256
    assert rec["size"] == 3
    assert rec["path"] == str(f)


# --- audit (append-only JSONL) ---------------------------------------------

def test_audit_creates_case_dir(tmp_path):
    case = tmp_path / "nested" / "case"  # does not exist yet
    audit(case, "test")
    assert (case / "audit.log").is_file()


def test_audit_appends_one_json_object_per_line(case_dir):
    audit(case_dir, "first", n=1)
    audit(case_dir, "second", n=2)
    lines = (case_dir / "audit.log").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    events = [json.loads(line) for line in lines]
    assert [e["event"] for e in events] == ["first", "second"]
    assert [e["n"] for e in events] == [1, 2]
    assert all("ts" in e for e in events)
