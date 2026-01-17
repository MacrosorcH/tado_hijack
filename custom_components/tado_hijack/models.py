"""Models for Tado Hijack."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RateLimit:
    """Model for API Rate Limit statistics."""

    limit: int
    remaining: int
