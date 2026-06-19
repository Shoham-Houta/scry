# scry — build order

Foundations first; prove one vertical slice before adding breadth.

## 1. Foundations

- [x] `core/evidence.py` — Provenance / Artifact / Finding dataclasses
- [ ] `core/runner.py` — safe subprocess (no shell, timeout, capture, exit code)
- [ ] `core/integrity.py` — sha256 ingest, read-only guard, audit log

## 2. Vertical slice (images, end-to-end)

- [ ] `extractors/base.py` — Extractor ABC
- [ ] `extractors/exiftool.py` — `exiftool -j -G` → Findings
- [ ] `core/dispatcher.py` — MIME detect → route
- [ ] `registry.py` — register extractors
- [ ] `report/json_report.py` — serialize Artifact
- [ ] `cli.py` — `scry scan <image>`

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
