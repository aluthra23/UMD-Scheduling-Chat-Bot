import os
from datetime import datetime


def update_term_id():
    """
    Updates the term_id for the current semester
    """
    configured_term_id = os.getenv("UMD_TERM_ID")
    if configured_term_id:
        return configured_term_id.strip()

    now_time = datetime.now()
    current_day = now_time.day
    current_month = now_time.month
    current_year = now_time.year


    if current_month <= 2 and current_day <= 20:
        term_id = f"{current_year}01"
    elif current_month <= 9:
        term_id = f"{current_year}08"
    else:
        term_id = f"{current_year + 1}01"


    return term_id.strip()
