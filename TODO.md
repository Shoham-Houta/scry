# scry — build order

Foundations first; prove one vertical slice before adding breadth.

## 1. Foundations

- [x] `core/evidence.py` — Provenance / Artifact / Finding dataclasses
- [x] `core/runner.py` — safe subprocess (no shell, timeout, capture, exit code)
- [x] `core/integrity.py` — sha256 ingest, read-only guard, audit log

## 2. Vertical slice (images, end-to-end)

- [x] `extractors/base.py` — Extractor ABC
- [x] `extractors/exiftool.py` — `exiftool -j -G` → Findings
- [x] `core/dispatcher.py` — MIME detect → route
- [x] `registry.py` — register extractors
- [x] `report/json_report.py` — serialize Artifact
- [x] `cli.py` — `scry scan <image>`

## 3. Breadth

- [ ] `extractors/pdf.py` — pdfinfo + pdftotext (graceful if poppler missing)

## 4. Enrichment (offline)

- [ ] `enrichers/base.py` — Enricher ABC
- [ ] `enrichers/geo.py` — EXIF GPS → decimal coords
- [ ] `enrichers/indicators.py` — emails/URLs/IPs from text

## 5. Tests

- [ ] fixtures: jpg with known GPS, pdf with known metadata
- [ ] tests for runner, integrity, each extractor/enricher

## Later (out of v1 scope)

- [ ] HTML report + cross-artifact timeline
- [ ] network OSINT enrichers (whois/dns/reverse-geocode) behind config flag
- [ ] more extractors: strings, binwalk, office docs
