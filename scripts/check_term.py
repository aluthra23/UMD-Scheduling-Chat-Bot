from __future__ import annotations

import argparse
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from helping_files import http_utils  # noqa: E402
from term_utils import TERM_PATTERN  # noqa: E402

API_URL = "https://umd-courses-api-aluthra-705eb647.koyeb.app/v1/class_sections/CMSC351"
# The API runs on Koyeb's free tier, which can take a while to wake up.
API_TIMEOUT = (10, 90)


def term_is_available(term_id: str, fetch=http_utils.fetch) -> bool:
    try:
        response = fetch(f"{API_URL}?term_id={term_id}", timeout=API_TIMEOUT)
    except requests.HTTPError as error:
        response = error.response
        if response is None or response.status_code != 404:
            raise
        try:
            body = response.json()
        except ValueError as parse_error:
            raise RuntimeError("Availability endpoint returned an invalid 404 response") from parse_error
        if body == {"detail": "Course not found!"}:
            return False
        raise RuntimeError(f"Unexpected 404 response: {body!r}") from error

    data = response.json()
    if not isinstance(data, list) or not data:
        raise RuntimeError(f"Availability endpoint returned no sections for {term_id}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether a UMD term is published.")
    parser.add_argument("term_id")
    args = parser.parse_args()

    if not TERM_PATTERN.fullmatch(args.term_id):
        parser.error("term_id must have the format YYYY01 or YYYY08")

    if term_is_available(args.term_id):
        print(f"{args.term_id} is available")
        return 0

    print(f"{args.term_id} is not available yet")
    return 10


if __name__ == "__main__":
    sys.exit(main())
