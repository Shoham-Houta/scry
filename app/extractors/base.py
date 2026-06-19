"""Extractor plugin interface.

Each base tool is wrapped as an Extractor. Suggested ABC:
    handles(mime) -> bool      # does this extractor apply to the file type?
    available()   -> bool      # is the underlying binary installed?
    extract(path) -> Artifact  # run tool, parse output into the evidence model
"""
