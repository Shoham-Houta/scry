"""Geolocation enricher (offline).

Converts EXIF GPS tags (degrees/minutes/seconds + refs) into decimal
coordinates. Pure math, no network. Optional reverse-geocode stays gated
behind config.network_enabled (off by default).
"""

from app.enrichers.base import Enricher
from app.core.evidence import Artifact, Category, Finding


def _to_decimal(deg, minutes, sec, ref) -> float:
    dec = int(deg) + int(minutes) / 60 + float(sec) / 3600
    return -dec if ref in ("S", "W") else dec


class GeoLocationEnricher(Enricher):
    name = "GeoLocation"

    def applies(self, artifact: Artifact) -> bool:
        return any(f.category == Category.GPS for f in artifact.findings)

    def enrich(self, artifact: Artifact) -> list[Finding]:
        source = next((f for f in artifact.findings if f.key == "Composite:GPSPosition"), None)
        if not source:
            return []

        lat, lng = source.value.split(",")
        lat_parts = lat.replace("deg", " ").replace("'", " ").replace("\"", " ").split()
        lng_parts = lng.replace("deg", " ").replace("'", " ").replace("\"", " ").split()
        lat_coords = _to_decimal(lat_parts[0], lat_parts[1], lat_parts[2], lat_parts[3])
        lng_coords = _to_decimal(lng_parts[0], lng_parts[1], lng_parts[2], lng_parts[3])

        return [
            Finding(
                key="GPSDecimal",
                value=f"{lat_coords},{lng_coords}",
                source_tool=self.name,
                category=Category.GPS,
                confidence=source.confidence*self.reliability,
            )
        ]

