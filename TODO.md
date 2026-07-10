# scry v1 — build order

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

- [x] `extractors/pdf.py` — pdfinfo + pdftotext (graceful if poppler missing)

## 4. Enrichment (offline)

- [x] `enrichers/base.py` — Enricher ABC
- [x] `enrichers/geo.py` — EXIF GPS → decimal coords
- [x] `enrichers/indicators.py` — emails/URLs/IPs/PhoneNumber from text

## 5. Tests

- [x] fixtures: jpg with known GPS, pdf with known metadata
- [x] tests for runner, integrity, each extractor/enricher

---

# scry v2 — identity & correlation

Same rule as v1: prove one offline vertical slice (identity) before breadth,
and keep network strictly opt-in (default OFF).

## 6. Identity vertical slice (offline)

- [ ] `extractors/pdflinks.py` — `pdftohtml -i -noframes -stdout` → recover
  
      embedded hyperlink URIs that `pdftotext` silently drops. Emit as
      INDICATOR/`url`; the embedded-vs-visible distinction lives in
      `source_tool`/provenance, NOT a new category.
- [ ] `enrichers/username.py` — map known host → handle (linkedin.com/in/<h>,
  
      github.com/<h>, …) from `url` findings. Deterministic → reliability 1.0.
      Emit LEAD/`username` (LEAD widened from "suspicious PDF feature" to
      "actionable pivot/follow-up").
- [ ] `enrichers/entities.py` — spaCy NER (PERSON/GPE/LOC) → names/locations.
  
      Inferential → reliability ≈ 0.7. New `ENTITY` category, key ∈ {name,
      location, org}. GATED: requires taking the spaCy dependency + offline model.
- [ ] tests for each new extractor/enricher

## 7. Breadth — more extractors

- [ ] strings, binwalk, office docs, videos (graceful if tool missing)
- [ ] fixtures + tests for each

## 8. Network OSINT (opt-in, default OFF)

- [ ] `config.network_enabled` flag (default false) gates everything below
- [ ] defang IOCs on report output (keep canonical/fanged value in the model so downstream enrichers can still match/query)
- [ ] enrichers: whois, dns, reverse-geocode, url/ip reputation

## 9. Reporting & correlation

- [ ] HTML report
- [ ] cross-artifact timeline (correlate findings across artifacts)
