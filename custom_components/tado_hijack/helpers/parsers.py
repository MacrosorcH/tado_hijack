"""Parsing utilities for Tado Hijack."""

from __future__ import annotations

import re
from typing import Any

from ..models import RateLimit


def parse_ratelimit_headers(headers: dict[str, Any]) -> RateLimit | None:
    """Extract RateLimit information from Tado API headers."""
    policy = headers.get("RateLimit-Policy", "")
    limit_info = headers.get("RateLimit", "")

    try:
        limit = 0
        remaining = 0
        found = False

        if q_match := re.search(r"q=(\d+)", policy):
            limit = int(q_match[1])
            found = True

        if r_match := re.search(r"r=(\d+)", limit_info):
            remaining = int(r_match[1])
            found = True

        if found:
            return RateLimit(limit=limit, remaining=remaining)
    except (ValueError, TypeError, AttributeError):
        pass

    return None
