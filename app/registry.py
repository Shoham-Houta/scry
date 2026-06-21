"""Plugin registry.

Discovers and registers available Extractors and Enrichers so the
dispatcher can look them up by file type / applicability.
"""

from app.extractors.base import Extractor
from app.extractors.exiftool import ExiftoolExtractor
from app.extractors.pdfinfo import PDFInfoExtractor

_EXTRACTORS: list[Extractor] = [
    ExiftoolExtractor(),
    PDFInfoExtractor(),
]


def extractors_for(mime_type: str) -> list[Extractor]:
    return [e for e in _EXTRACTORS if e.handles(mime_type)]

