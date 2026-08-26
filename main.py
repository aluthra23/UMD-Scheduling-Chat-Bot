import argparse
import hashlib
import os
import uuid

import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

from qdrant_manager import QdrantManager


load_dotenv(os.getenv("ENV_FILE", ".env"))
parser = argparse.ArgumentParser(description="Incrementally synchronize scraped UMD data to Qdrant.")
parser.add_argument("--collection", default=os.getenv("QDRANT_COLLECTION", "202608"))
parser.add_argument("--batch-size", type=int, default=100)
parser.add_argument("--recreate", action="store_true", help="Force a one-time full rebuild.")
parser.add_argument("--dataset", choices=("all", "gen-eds"), default="all")
args = parser.parse_args()

if not os.getenv("QDRANT_API_KEY") or not os.getenv("QDRANT_LINK"):
    raise RuntimeError("QDRANT_API_KEY and QDRANT_LINK are required")

manager = QdrantManager(os.environ["QDRANT_API_KEY"], os.environ["QDRANT_LINK"])
datasets = [("gen_ed", pd.read_csv("./gen_eds/gen_eds.csv"))] if args.dataset == "gen-eds" else [
    ("schedule", pd.read_csv("./schedule_of_classes_scraper/umd_schedule_of_classes_courses.csv")),
    ("catalog", pd.read_csv("./course_catalog_scraper/umd_catalog_courses.csv")),
    ("prefix", pd.read_csv("./course_prefixes_dataset_creation/umd_course_prefixes.csv")),
    ("gen_ed", pd.read_csv("./gen_eds/gen_eds.csv")),
]


def key_for(source: str, row: pd.Series) -> str:
    if source == "schedule":
        identity = f"{row.get('COURSE NUMBER')}:{row.get('SECTION ID')}"
    elif source == "catalog":
        identity = row.get("COURSE NUMBER")
    elif source == "prefix":
        identity = row.get("COURSE PREFIX")
    else:
        identity = row.get("GENERAL EDUCATION ACRONYM")
    return f"{source}:{str(identity).upper()}"


documents = {}
for source, dataframe in datasets:
    for _, row in dataframe.iterrows():
        text = " ".join(f"{column}: {row[column]}" for column in dataframe.columns if pd.notna(row[column]) and row[column] != "")
        key = key_for(source, row)
        if key in documents:
            raise ValueError(f"Duplicate document key: {key}")
        course_number = row.get("COURSE NUMBER")
        documents[key] = {
            "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"umd:{args.collection}:{key}")),
            "text": text,
            "payload": {
                "text": text,
                "source": source,
                "course_number": str(course_number).upper() if pd.notna(course_number) else None,
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
stale_ids = [metadata["id"] for key, metadata in existing.items() if key not in documents]
print(f"Upserting {len(changed)} changed/new documents; deleting {len(stale_ids)} stale documents")
for start in tqdm(range(0, len(changed), args.batch_size), desc="Upserting batches", unit="batch"):
    manager.upsert_documents(args.collection, changed[start:start + args.batch_size])
manager.delete_points(args.collection, stale_ids)
print(f"Incremental sync complete for '{args.collection}'")
manager.client.close()
