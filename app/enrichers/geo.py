"""Geolocation enricher (offline).

Converts EXIF GPS tags (degrees/minutes/seconds + refs) into decimal
coordinates. Pure math, no network. Optional reverse-geocode stays gated
behind config.network_enabled (off by default).
"""
