"""exiftool extractor (images).

Runs `exiftool -j -G` (JSON output, grouped tags) and maps fields into
Findings. Handles image MIME types. GPS tags feed the geo enricher.
"""
