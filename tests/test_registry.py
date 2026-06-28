import pytest

from app import registry
from app.extractors.exiftool import ExiftoolExtractor
from app.extractors.pdfinfo import PDFInfoExtractor


def _types(mime):
    return {type(e) for e in registry.extractors_for(mime)}


def test_pdfinfo_extractor():
    types = _types("application/pdf")
    assert ExiftoolExtractor not in types
    assert PDFInfoExtractor in types


def test_image_routes_to_exiftool():
    types = _types("image/jpeg")
    assert ExiftoolExtractor in types
    assert PDFInfoExtractor not in types


def test_unknown_mime_returns_empty():
    assert registry.extractors_for("application/zip") == []
    assert registry.extractors_for("") == []


@pytest.mark.parametrize("mime", [
    "application/pdf", "image/jpeg", "image/png", "text/plain", "application/zip",
])
def test_returned_extractors_all_handle_mime(mime):
    """Whatever comes back must actually handle the mime — registry never mis-routes."""
    assert all(e.handles(mime) for e in registry.extractors_for(mime))
