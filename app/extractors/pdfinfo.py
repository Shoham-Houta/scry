"""PDF extractor (poppler).

`pdfinfo` for document metadata (producer, dates, page count) and
`pdftotext` for body text (fed to the indicators enricher). Degrades
gracefully with a warning if poppler is not installed.
"""
from pathlib import Path
from app.core.evidence import Finding, Provenance, Category
from app.extractors.base import Extractor
from app.core.runner import run
from shutil import which


class PDFInfoExtractor(Extractor):
    name = "pdfinfo"

    def handles(self, mime: str) -> bool:
        return mime == "application/pdf"

    def available(self) -> bool:
        return which("pdfinfo") is not None

    def extract(self, path: Path, timeout: float = 10):  #-> tuple[list[Finding], Provenance]:
        result = run(["pdfinfo", str(path)], timeout=timeout)
        version = self._tool_version(timeout)
        findings = self._parse(result.stdout, timeout)
        provenance = Provenance(
            tool=self.name,
            version=version,
            argv=result.argv,
            started_at=result.started_at,
            duration_s=result.duration_s,
            return_code=result.return_code
        )
        return findings, provenance

    def _parse(self, stdout: str, timeout: float = 10) -> list[Finding]:
        findings = []
        for line in stdout.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key, value = key.strip(), value.strip()
            findings.append(Finding(key, value, self.name, category=self._categorizer(key, value), confidence=1.0))

        return findings

    def _tool_version(self, timeout: float) -> str:
        return run(["pdfinfo", "-v"], timeout=timeout).stderr.split("\n")[0].split(" ")[-1]

    def _categorizer(self, key: str, value: str) -> Category:
        if key in {"CreationDate", "ModDate"}:
            return Category.TIMESTAMP
        if key in {"Creator", "Producer"}:
            return Category.DEVICE
        if key == "Author":
            return Category.AUTHOR
        if key in {"JavaScript", "Encrypted", "Suspects"} and value == "yes":
            return Category.LEAD
        return Category.OTHER
