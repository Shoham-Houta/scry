"""Extractor plugin interface.

Each base tool is wrapped as an Extractor. It does NOT build or mutate the
Artifact (integrity.ingest owns that) — it only returns its contribution,
which the dispatcher appends to the existing Artifact. Suggested ABC:
    name                 -> str                            # tool name (for Provenance / errors)
    handles(mime)        -> bool                           # does this extractor apply to the file type?
    available()          -> bool                           # is the underlying binary installed?
    extract(path)        -> tuple[list[Finding], Provenance]  # run tool, parse output into the evidence model
"""

from abc import ABC, abstractmethod
from pathlib import Path
from app.core.evidence import Finding, Provenance

class Extractor(ABC):
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool identity — used for Provenance.tool and error messages."""
    
    @abstractmethod
    def handles(self,mime: str) -> bool:
        """True if this extractor applies to the given MIME type."""

    @abstractmethod
    def available(self) -> bool:
        """True if the underlying binary is installed (e.g shutil.which)."""

    @abstractmethod
    def extract(self, path: Path) -> tuple[list[Finding], Provenance]:
        """Run the tool and return its findings + provenance."""

