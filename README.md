# scry

An OSINT / forensics tool that wraps trusted base utilities (`exiftool`,
`pdfinfo`, `pdftotext`, ...) behind a uniform extractor interface, normalizes
their output into one evidence model, and reports findings — while preserving
forensic integrity (originals never modified, everything hashed, every command
logged).

**v1 scope:** offline forensics, CLI-first, images (EXIF/GPS) and PDFs.

## Architecture

External tools are treated as plugins, not hardcoded calls:

- `app/core/` — runner (safe subprocess), integrity (hashing / read-only /
  audit log), evidence (normalized model), dispatcher (file → extractors).
- `app/extractors/` — one adapter per base tool (`exiftool`, `pdf`).
- `app/enrichers/` — derive new findings offline (`geo`, `indicators`).
- `app/report/` — canonical JSON output.
- `app/cli.py` — `scry scan <path>`.

## Setup

### Base CLI tools

`scry` shells out to these — install them with your system package manager:

| Tool | macOS | Debian/Ubuntu | Fedora/RHEL |
|---|---|---|---|
| exiftool | `brew install exiftool` | `apt install libimage-exiftool-perl` | `dnf install perl-Image-ExifTool` |
| poppler (pdfinfo, pdftotext) | `brew install poppler` | `apt install poppler-utils` | `dnf install poppler-utils` |

### Python environment

**With conda (recommended):** conda-forge pulls in `libmagic` automatically, so
nothing extra is needed.

```bash
conda env create -f environment.yml
conda activate scry
```

**Without conda (pip):** `python-magic` is a wrapper around the native
**libmagic** library, which you must install separately per platform:

| Platform | libmagic install |
|---|---|
| macOS (Homebrew) | `brew install libmagic` |
| Debian/Ubuntu | `apt install libmagic1` |
| Fedora/RHEL | `dnf install file-libs` |
| Alpine | `apk add libmagic` |
| Arch | `pacman -S file` |

```bash
# install libmagic for your platform (see table above), then:
pip install python-magic python-dotenv pytest
```

> Avoid `python-magic-bin` — it conflicts with `python-magic` and its
> Apple-Silicon build is broken.

## Usage (planned)

```bash
scry scan photo.jpg -o report.json
scry tools                          # show base tools + availability
```
