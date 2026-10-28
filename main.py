import argparse
import hashlib
import os
import uuid

import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

from qdrant_manager import QdrantManager
from sync_utils import document_key, document_text, stale_document_ids


load_dotenv(os.getenv("ENV_FILE", ".env"))
parser = argparse.ArgumentParser(description="Incrementally synchronize scraped UMD data to Qdrant.")
parser.add_argument("--collection", required=True, help="Term collection to sync, e.g. 202701.")
parser.add_argument("--batch-size", type=int, default=100)
parser.add_argument("--recreate", action="store_true", help="Force a one-time full rebuild.")
parser.add_argument("--dataset", choices=("all", "gen-eds"), default="all")
parser.add_argument("--allow-mass-delete", action="store_true", help="Skip the safety check that aborts when a scrape lost most of its documents.")
args = parser.parse_args()

if not os.getenv("QDRANT_API_KEY") or not os.getenv("QDRANT_LINK"):
    raise RuntimeError("QDRANT_API_KEY and QDRANT_LINK are required")


def read_csv(path):
    # Read everything as text so IDs like section "0101" never get turned into numbers.
    return pd.read_csv(path, dtype=str, keep_default_na=False)


manager = QdrantManager(os.environ["QDRANT_API_KEY"], os.environ["QDRANT_LINK"])
datasets = [("gen_ed", read_csv("./gen_eds/gen_eds.csv"))] if args.dataset == "gen-eds" else [
    ("schedule", read_csv("./schedule_of_classes_scraper/umd_schedule_of_classes_courses.csv")),
    ("catalog", read_csv("./course_catalog_scraper/umd_catalog_courses.csv")),
    ("prefix", read_csv("./course_prefixes_dataset_creation/umd_course_prefixes.csv")),
    ("gen_ed", read_csv("./gen_eds/gen_eds.csv")),
]

documents = {}
for source, dataframe in datasets:
    columns = list(dataframe.columns)
    for row in dataframe.to_dict("records"):
        text = document_text(source, row, columns)
        key = document_key(source, row)
        if key in documents:
            raise ValueError(f"Duplicate document key: {key}")
        course_number = row.get("COURSE NUMBER", "").strip()
        documents[key] = {
            "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"umd:{args.collection}:{key}")),
            "text": text,
            "payload": {
                "text": text,
                "source": source,
                "course_number": course_number.upper() or None,
                "document_key": key,
                "content_hash": hashlib.sha256(text.encode()).hexdigest(),
            },
        }

print(f"Prepared {len(documents)} retrieval documents")
exists = manager.client.collection_exists(args.collection)
existing = None if args.recreate or not exists else manager.existing_documents(args.collection)
if existing is None:
    manager.create_collection(args.collection, recreate=exists)
    existing = {}
    print("Full rebuild: collection has no incremental metadata")

changed = [document for key, document in documents.items() if existing.get(key, {}).get("content_hash") != document["payload"]["content_hash"]]
stale_ids = stale_document_ids(existing, documents, {source for source, _ in datasets}, args.allow_mass_delete)
print(f"Upserting {len(changed)} changed/new documents; deleting {len(stale_ids)} stale documents")
for start in tqdm(range(0, len(changed), args.batch_size), desc="Upserting batches", unit="batch"):
    manager.upsert_documents(args.collection, changed[start:start + args.batch_size])
manager.delete_points(args.collection, stale_ids)
manager.record_sync(args.collection, documents=len(documents), upserted=len(changed), deleted=len(stale_ids))
print(f"Incremental sync complete for '{args.collection}'")
manager.client.close()
