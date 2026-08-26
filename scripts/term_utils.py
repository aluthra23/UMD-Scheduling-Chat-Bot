from __future__ import annotations

import re


TERM_PATTERN = re.compile(r"^(?P<year>20\d{2})(?P<season>01|08)$")


def next_term_id(term_id: str) -> str:
    """Return the semester immediately after a UMD term ID."""
    match = TERM_PATTERN.fullmatch(term_id)
    if not match:
        raise ValueError(f"Invalid UMD term ID: {term_id!r}")

    year = int(match.group("year"))
    return f"{year}08" if match.group("season") == "01" else f"{year + 1}01"


def term_label(term_id: str) -> str:
    match = TERM_PATTERN.fullmatch(term_id)
    if not match:
        raise ValueError(f"Invalid UMD term ID: {term_id!r}")

    season = "Spring" if match.group("season") == "01" else "Fall"
    return f"{season} {match.group('year')}"
