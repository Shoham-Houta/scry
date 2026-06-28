from pathlib import Path
from shutil import which

import pytest
from app.core.evidence import Category, Finding
from app.extractors.exiftool import ExiftoolExtractor


@pytest.fixture
def extractor() -> ExiftoolExtractor:
    return ExiftoolExtractor()


# --- routing ---------------------------------------------------------------

def test_handles_only_images(extractor: ExiftoolExtractor) -> None:
    assert extractor.handles("image/png") is True
    assert extractor.handles("image/jpeg") is True
    assert extractor.handles("image/gif") is True
    assert extractor.handles("image/tiff") is True
    assert extractor.handles("application/pdf") is False
    assert extractor.handles("text/plain") is False


# --- categorizer (pure) ----------------------------------------------------

@pytest.mark.parametrize("key, expected", [
    ("CreationDate",      Category.TIMESTAMP),
    ("GPSPosition",       Category.GPS),
    ("LensModel",         Category.DEVICE),
    ("FOV",               Category.OTHER),
])
def test_categorizer(extractor, key, expected):
    assert extractor._categorizer(key) == expected


# --- parse (pure: str -> list[findings]) --------------------------------------

def test_parse_build_findings(extractor: ExiftoolExtractor, exiftool_clean) -> None:
    findings = extractor._parse(exiftool_clean)
    assert findings[0], "expected at least one finding"
    assert all(isinstance(f, Finding) for f in findings[0])
    assert all(f.source_tool == "exiftool" for f in findings[0])

def test_parse_skip_file_metadata(extractor: ExiftoolExtractor, exiftool_clean) -> None:
    keys = {f.key for f in extractor._parse(exiftool_clean)[0]}
    skip = {
        "SourceFile", "ExifTool:ExifToolVersion",
        "File:FileName", "File:Directory", "File:FileSize", "File:MIMEType",
    }
    assert keys.isdisjoint(skip)  # none of the skip keys survived


def test_version_extract(extractor: ExiftoolExtractor, exiftool_clean) -> None:
    _, version = extractor._parse(exiftool_clean)
    assert version == "13.55"


# --- Integration (need exiftool) ------------------------------------------------------------
@pytest.mark.integration
@pytest.mark.skipif(which("exiftool") is None, reason="exiftool not installed")
def test_extract_real_image(extractor: ExiftoolExtractor) -> None:
    img = Path(__file__).parent / "fixtures" / "image.jpeg"
    if not img.is_file():
        pytest.skip("no image")
    findings, prov = extractor.extract(img)
    assert prov.tool == "exiftool"
    assert prov.return_code == 0
    assert prov.version and prov.version != "Unknown"
    assert "EXIF:Model" in {f.key for f in findings}
