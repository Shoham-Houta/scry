"""exiftool extractor (images).

Runs `exiftool -j -G` (JSON output, grouped tags) and maps fields into
Findings. Handles image MIME types. GPS tags feed the geo enricher.
"""
import json
from pathlib import Path
from app.core.evidence import Finding, Provenance, Category
from app.extractors.base import Extractor
from app.core.runner import run
from shutil import which


class ExiftoolExtractor(Extractor):
    name = "exiftool"

    def handles(self, mime: str) -> bool:
        return mime.startswith("image/")

    def available(self) -> bool:
        return which("exiftool") is not None

    def extract(self, path: Path, timeout: float = 10) -> tuple[list[Finding], Provenance]:
        result = run(["exiftool", "-j", "-G", str(path)], timeout=timeout)
        findings, version = self._parse(result.stdout)
        provenance = Provenance(
            tool=self.name,
            version=version,
            argv=result.argv,
            return_code=result.return_code,
            started_at=result.started_at,
            duration_s=result.duration_s,
        )
        return findings, provenance

    def _parse(self, stdout: str):
        data = json.loads(stdout)[0]
        version = str(data.get("ExifTool:ExifToolVersion", "unknown"))
        skip = {
            "SourceFile", "ExifTool:ExifToolVersion",
            "File:FileName", "File:Directory", "File:FileSize", "File:MIMEType",
        }
        findings = []
        for key, value in data.items():
            tag = key.split(":")[-1]
            if key in skip:
                continue
            findings.append(Finding(
                key=key,
                value=value,
                source_tool=self.name,
                category=self._categorizer(tag),
                confidence=1.0
            ))
        return findings, version

    def _categorizer(self, tag: str) -> Category:
        if tag.startswith("GPS"):
            return Category.GPS

        if "Date" in tag or tag.startswith("OffsetTime"):
            return Category.TIMESTAMP
        if tag in {
            "Make", "Model", "Software", "HostComputer", "CreatorTool",
            "LensInfo", "LensMake", "LensModel", "LensID", "LensSerialNumber",
            "CameraType", "SerialNumber", "BodySerialNumber", "CameraOwnerName",
        }:
            return Category.DEVICE
        if tag in {
            "Artist", "Creator", "Author", "By-line", "Copyright",
            "Rights", "OwnerName",
        }:
            return Category.AUTHOR

        return Category.OTHER
