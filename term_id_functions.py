from datetime import datetime


def update_term_id():
    """
    Updates the term_id for the current semester
    """
    current_month = datetime.now().month
    current_year = datetime.now().year


    if current_month <= 2:
        term_id = f"{current_year}01"
    elif current_month <= 9:
        term_id = f"{current_year}08"
    else:
        term_id = f"{current_year + 1}01"


    return term_id.strip()