"""Extractor routing.

Takes the base Artifact produced by integrity.ingest (mime already detected)
and routes it: asks the registry which extractors handle artifact.mime, runs
the available ones on artifact.path, and appends their findings + provenance
back into the same Artifact. Skips unavailable tools and isolates failures
(per-extractor errors go into Artifact.errors). Does no file detection itself.
"""
