"""Plugin registry.

Discovers and registers available Extractors and Enrichers so the
dispatcher can look them up by file type / applicability.
"""
from app.core.evidence import Artifact
from app.enrichers.base import Enricher
from app.enrichers.geo import GeoLocationEnricher
from app.enrichers.indicators import IndicatorEnricher
from app.extractors.base import Extractor
from app.extractors.exiftool import ExiftoolExtractor
from app.extractors.pdf2text import PDF2TextExtractor
from app.extractors.pdfinfo import PDFInfoExtractor

_EXTRACTORS: list[Extractor] = [
    ExiftoolExtractor(),
    PDFInfoExtractor(),
    PDF2TextExtractor(),
]
_ENRICHERS: list[Enricher] = [
    GeoLocationEnricher(),
    IndicatorEnricher()
]


def extractors_for(mime_type: str) -> list[Extractor]:
    return [e for e in _EXTRACTORS if e.handles(mime_type)]


def enrichers_for(artifact: Artifact) -> list[Enricher]:
    return [e for e in _ENRICHERS if e.applies(artifact)]
