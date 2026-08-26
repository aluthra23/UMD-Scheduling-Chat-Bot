from __future__ import annotations

import os
import argparse

from dotenv import load_dotenv
from qdrant_client import QdrantClient

from term_utils import TERM_PATTERN, next_term_id


def main() -> None:
    parser = argparse.ArgumentParser(description="Find the newest uploaded term or the term after it.")
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Print the newest uploaded term instead of the next term.",
    )
    args = parser.parse_args()

    load_dotenv(os.getenv("ENV_FILE", ".env"))
    qdrant_url = os.getenv("QDRANT_LINK")
    qdrant_key = os.getenv("QDRANT_API_KEY")
    if not qdrant_url or not qdrant_key:
        raise RuntimeError("QDRANT_LINK and QDRANT_API_KEY are required")

    client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
    try:
        uploaded_terms = sorted(
            collection.name
            for collection in client.get_collections().collections
            if TERM_PATTERN.fullmatch(collection.name)
        )
    finally:
        client.close()

    if not uploaded_terms:
        raise RuntimeError("No numeric term collection exists; seed the first term manually.")

    latest_term = uploaded_terms[-1]
    print(latest_term if args.latest else next_term_id(latest_term))


if __name__ == "__main__":
    main()
