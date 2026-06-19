"""Enricher plugin interface.

Enrichers take extracted Findings and derive new ones (offline by default).
Suggested ABC:
    applies(artifact) -> bool
    enrich(artifact)  -> list[Finding]
"""
