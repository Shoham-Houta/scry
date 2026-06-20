"""Normalized evidence model.

The common schema every extractor/enricher emits, so tool-specific output
(exiftool JSON, pdfinfo text, ...) collapses into one shape.

Suggested types:
    Provenance  -- tool name, version, exact argv, exit code, UTC timestamp
    Artifact    -- one source file: sha256, mime, list[Finding], list[Provenance]
    Finding     -- one normalized fact: key, value, source tool, confidence
"""

from dataclasses import field, dataclass
from pathlib import Path
from enum import StrEnum, auto
from typing import Any
from datetime import datetime


class Category(StrEnum):
    GPS = auto()
    TIMESTAMP = auto()
    DEVICE = auto()
    AUTHOR = auto()
    INDICATOR = auto()
    OTHER = auto()


@dataclass(frozen=True)
class Finding:
    """
    values should be JSON-serializable; 
    Findings are not reliably hashable when value is a list/dict — dedup by (key, source_tool, value) instead.
    """
    key: str  # Data label
    value: Any  # Value associated with the label
    source_tool: str  # Origin of the finding
    category: Category  # Category of the finding
    confidence: float = 1.0  # Confidence score of the finding relevancy


@dataclass(frozen=True)
class Provenance:
    tool: str  # Tool name
    version: str  # Tool version
    argv: tuple[str, ...]  # Tool arguments
    return_code: int  # Exit code of the tool
    started_at: datetime  # When the tool started
    duration_s: float  # How long the tool ran


@dataclass
class Artifact:
    path: Path  # Artifact path
    sha256: str  # Unique hash of the artifact
    size: int  # Artifact size in bytes
    mime: str  # Mime type (text/ascii,image/png, etc...)
    findings: list[Finding] = field(default_factory=list)  # Findings
    provenance: list[Provenance] = field(default_factory=list)  # Details on the artifact creation and metadata
    errors: list[str] = field(default_factory=list)  # Errors list while artifact creation
