from __future__ import annotations

import argparse
import sys

import requests

from term_utils import TERM_PATTERN


def term_is_available(term_id: str) -> bool:
    response = requests.get(
        f"https://umd-courses-api-aluthra-705eb647.koyeb.app/v1/class_sections/CMSC351",
        params={"term_id": term_id},
        timeout=30,
    )

    if response.status_code == 404:
        try:
            body = response.json()
        except ValueError as error:
            raise RuntimeError("Availability endpoint returned an invalid 404 response") from error
        if body == {"detail": "Course not found!"}:
            return False
        raise RuntimeError(f"Unexpected 404 response: {body!r}")

    response.raise_for_status()
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
