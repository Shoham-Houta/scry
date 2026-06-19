"""File-type routing.

Detect a file's MIME/magic type, then ask the registry which extractors
declare they handle it and run those. Aggregates results into one Artifact.
"""
