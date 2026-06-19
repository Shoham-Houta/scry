"""Safe execution of external base tools.

Wraps subprocess calls to exiftool / pdfinfo / etc. with: no shell, explicit
argv, per-tool timeout, captured stdout+stderr, and a recorded exit code.
Returns enough detail for Provenance (argv, version, duration, return code).
"""
