"""Forensic integrity guarantees.

Hash inputs (sha256) at ingest, enforce read-only handling of originals
(never mutate the source file), and maintain a per-case audit log of every
command run. Backbone for chain-of-custody.
"""
