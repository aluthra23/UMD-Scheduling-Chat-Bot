from __future__ import annotations

import os

from dotenv import load_dotenv
from qdrant_client import QdrantClient

from term_utils import TERM_PATTERN, next_term_id


def main() -> None:
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

    print(next_term_id(uploaded_terms[-1]))


if __name__ == "__main__":
    main()
