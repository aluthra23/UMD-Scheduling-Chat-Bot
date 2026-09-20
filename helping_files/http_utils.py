import time

import requests


RETRYABLE_STATUSES = {408, 425, 429, 500, 502, 503, 504}
DEFAULT_TIMEOUT = (10, 60)


def fetch(url, *, allow_not_found=False, attempts=4, timeout=DEFAULT_TIMEOUT, sleep=time.sleep):
    """GET a URL, retrying transient failures, and raise if it never succeeds.

    Returns None only for a 404 when allow_not_found is set. Any other failure raises so a
    flaky response can never be mistaken for "this page has no data".
    """
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            response = requests.get(url, timeout=timeout)
        except (requests.ConnectionError, requests.Timeout) as error:
            last_error = error
        else:
            if response.status_code == 404 and allow_not_found:
                return None
            if response.status_code < 400:
                return response
            if response.status_code not in RETRYABLE_STATUSES:
                response.raise_for_status()
            last_error = requests.HTTPError(f"{response.status_code} error for {url}", response=response)

        if attempt < attempts:
            sleep(min(5 * 2 ** (attempt - 1), 30))

    raise last_error
