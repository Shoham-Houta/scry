"""Extractor routing.

Takes the base Artifact produced by integrity.ingest (mime already detected)
and routes it: asks the registry which extractors handle artifact.mime, runs
the available ones on artifact.path, and appends their findings + provenance
back into the same Artifact. Skips unavailable tools and isolates failures
(per-extractor errors go into Artifact.errors). Does no file detection itself.
"""

from app.core.evidence import Artifact
from app.registry import extractors_for


def dispatch(artifact: Artifact) -> Artifact:
    for extractor in extractors_for(artifact.mime):
        if not extractor.available():
            artifact.errors.append(f"{extractor.name}: tool is not available")
            continue
        try:
            findings, provenance = extractor.extract(artifact.path)
            artifact.findings.extend(findings)
            artifact.provenance.append(provenance)
        except Exception as e:
            artifact.errors.append(f"{extractor.name}: {e}")
    return artifact
