from pathlib import Path

from app.extractors.base import Extractor
from app.core.evidence import Finding, Provenance, Category
from app.core.runner import run
from shutil import which


class PDF2TextExtractor(Extractor):
    name = 'pdftotext'

    def handles(self, mime: str) -> bool:
        return mime.startswith('application/pdf')

    def available(self) -> bool:
        return which('pdftotext') is not None

    def extract(self, path: Path, timeout: float = 10) -> tuple[list[Finding], Provenance]:
        result = run(["pdftotext", "-layout", str(path), "-"], timeout=timeout)
        if result.return_code != 0:
            raise RuntimeError(result.stderr or "pdftotext failed")
        findings = [Finding(
            key="Text",
            value=result.stdout,
            source_tool=self.name,
            category=Category.TEXT
        )]
        provenance = Provenance(
            tool=self.name,
            version=self._tool_version(timeout),
            argv=result.argv,
            started_at=result.started_at,
            duration_s=result.duration_s,
            return_code=result.return_code
        )
        return findings, provenance

    def _tool_version(self, timeout: float) -> str:
        return run(["pdftotext", "-v"], timeout=timeout).stderr.split("\n")[0].split(" ")[-1]
