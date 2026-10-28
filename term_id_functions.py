import os
from datetime import datetime


def default_term_id(now=None):
    """The current or upcoming UMD term: spring through Feb 20, fall through September, then next spring."""
    now = now or datetime.now()
    if now.month == 1 or (now.month == 2 and now.day <= 20):
        return f"{now.year}01"
    if now.month <= 9:
        return f"{now.year}08"
    return f"{now.year + 1}01"


def update_term_id():
    """The term to scrape: UMD_TERM_ID when set, otherwise the date-based default."""
    configured_term_id = os.getenv("UMD_TERM_ID")
    if configured_term_id:
        return configured_term_id.strip()
    return default_term_id()
