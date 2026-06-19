"""PDF extractor (poppler).

`pdfinfo` for document metadata (producer, dates, page count) and
`pdftotext` for body text (fed to the indicators enricher). Degrades
gracefully with a warning if poppler is not installed.
"""
