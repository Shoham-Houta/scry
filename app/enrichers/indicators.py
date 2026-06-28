"""Indicator extraction (offline).

Regex-scans extracted text (e.g. PDF body) for emails, URLs, IPs and
usernames, emitting them as Findings for later OSINT follow-up.
"""

from app.enrichers.base import Enricher
from app.core.evidence import Finding, Artifact, Category

import re
import phonenumbers

patterns = {
    "email": (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", 0.9),
    "url": (r"\bhttps?://[^\s<>\"')]+", 0.85),
    "ipv4": (r"\b(?:\d{1,3}\.){3}\d{1,3}\b", 0.5)
}


def match_text(text_finding: str, pattern: str):
    finding = re.compile(pattern).findall(text_finding)
    return finding


def valid_ipv4(text: str) -> bool:
    return all(o.isdigit() and 0 <= int(o) <= 255 for o in text.split("."))


class IndicatorEnricher(Enricher):
    name = "Indicator"

    def applies(self, artifact: Artifact) -> bool:
        return any(f.category == Category.TEXT for f in artifact.findings)

    def enrich(self, artifact: Artifact):
        source = next((f for f in artifact.findings if f.category == Category.TEXT), None)
        if source is None:
            return []

        findings = []
        for kind, (pattern, pat_conf) in patterns.items():       # loop the table
            for match in set(match_text(source.value, pattern)):  # set() dedups
                if kind == "ipv4" and not valid_ipv4(match):
                    continue                                       # validator hook
                if kind == "url":
                    match = match.rstrip(".,;")
                findings.append(Finding(
                    key=kind,
                    value=match,
                    source_tool=self.name,
                    category=Category.INDICATOR,
                    confidence=source.confidence * self.reliability * pat_conf,
                ))

        findings.extend(self._extract_phones(source))
        return findings

    def _extract_phones(self, source: Finding) -> list[Finding]:
        """Phone numbers via libphonenumber: wide net (POSSIBLE, region-agnostic)
        for max coverage, then grade confidence by validation strength so weak
        matches sink instead of being dropped. region=None -> international (+)
        numbers only, which keeps false positives down. Dedup on E.164."""
        seen: dict[str, Finding] = {}
        for match in phonenumbers.PhoneNumberMatcher(
            source.value, None, leniency=phonenumbers.Leniency.POSSIBLE
        ):
            number = match.number
            e164 = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
            if e164 in seen:
                continue
            if phonenumbers.is_valid_number(number):
                pat_conf = 0.85
            elif phonenumbers.is_possible_number(number):
                pat_conf = 0.55
            else:
                pat_conf = 0.3
            seen[e164] = Finding(
                key="phone",
                value=e164,
                source_tool=self.name,
                category=Category.INDICATOR,
                confidence=source.confidence * self.reliability * pat_conf,
            )
        return list(seen.values())

