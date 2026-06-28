"""Enricher plugin interface.

Enrichers take extracted Findings and derive new ones (offline by default).
Suggested ABC:
    applies(artifact) -> bool
    enrich(artifact)  -> list[Finding]
"""
from abc import ABC, abstractmethod
from app.core.evidence import Artifact, Finding

class Enricher(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        """ Tool identity - used for Finding.source_tool and error messages."""

    reliability: float = 1.0

    @abstractmethod
    def applies(self, artifact: Artifact) -> bool:
        """ True if this enricher applies to the given artifact findings.category"""

    @abstractmethod
    def enrich(self, artifact: Artifact) -> list[Finding]:
        """Return a new findings derived from the original"""
