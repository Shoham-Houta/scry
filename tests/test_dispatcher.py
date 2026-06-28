"""Tests for the dispatcher's routing + failure isolation.

The dispatcher's whole job is orchestration, so we test it with FAKE
extractors instead of real tools -- no exiftool/poppler needed, fully
deterministic. Each fake subclasses the Extractor ABC and simulates one
behavior (works / unavailable / raises).

The dispatcher looks routing up via `extractors_for(artifact.mime)`. We don't
want the real registry here, so we monkeypatch the name *as imported into the
dispatcher module* (app.core.dispatcher.extractors_for) to return our fakes.
"""
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.core import dispatcher
from app.core.dispatcher import dispatch
from app.core.evidence import Artifact, Category, Finding, Provenance


# --- fakes -----------------------------------------------------------------

def _provenance(name: str) -> Provenance:
    return Provenance(
        tool=name, version="1.0", argv=(name,), return_code=0,
        started_at=datetime.now(timezone.utc), duration_s=0.0,
    )


class WorkingExtractor:
    """Available, returns one finding + provenance."""
    name = "working"

    def handles(self, mime: str) -> bool:
        return True

    def available(self) -> bool:
        return True

    def extract(self, path: Path, timeout: float = 10):
        finding = Finding("k", "v", self.name, Category.OTHER, 1.0)
        return [finding], _provenance(self.name)


class UnavailableExtractor(WorkingExtractor):
    """Binary not installed -> dispatcher records an error, must not call extract."""
    name = "missing"

    def available(self) -> bool:
        return False

    def extract(self, path: Path, timeout: float = 10):
        raise AssertionError("extract must not be called when unavailable")


class RaisingExtractor(WorkingExtractor):
    """Available but blows up mid-extract -> failure must be isolated."""
    name = "boom"

    def extract(self, path: Path, timeout: float = 10):
        raise RuntimeError("parse exploded")


# --- helpers ---------------------------------------------------------------

@pytest.fixture
def artifact() -> Artifact:
    return Artifact(path=Path("sample.bin"), sha256="0" * 64, size=1, mime="application/x-test")


@pytest.fixture
def route(monkeypatch):
    """Return a setter that makes the dispatcher route to the given fakes."""
    def _set(*extractors):
        monkeypatch.setattr(dispatcher, "extractors_for", lambda mime: list(extractors))
    return _set


# --- tests -----------------------------------------------------------------

def test_working_extractor_contributes(artifact, route):
    route(WorkingExtractor())
    result = dispatch(artifact)
    assert [f.value for f in result.findings] == ["v"]
    assert [p.tool for p in result.provenance] == ["working"]
    assert result.errors == []


def test_unavailable_extractor_records_error(artifact, route):
    route(UnavailableExtractor())
    result = dispatch(artifact)
    assert result.findings == []
    assert "missing: tool is not available" in result.errors


def test_raising_extractor_is_isolated(artifact, route):
    route(RaisingExtractor())
    result = dispatch(artifact)
    assert "boom: parse exploded" in result.errors
    assert result.provenance == []


def test_failure_extractor_does_not_stop_later_extractor(artifact, route):
    route(RaisingExtractor(), WorkingExtractor())
    result = dispatch(artifact)
    assert [f.value for f in result.findings] == ["v"]
    assert "boom: parse exploded" in result.errors
