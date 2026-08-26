import argparse
import os

import pandas as pd
from dotenv import load_dotenv

from qdrant_manager import QdrantManager
from tqdm import tqdm

load_dotenv(os.getenv("ENV_FILE", ".env"))

parser = argparse.ArgumentParser(description="Embed scraped UMD data and upload it to Qdrant.")
parser.add_argument("--collection", default=os.getenv("QDRANT_COLLECTION", "Fall-2026-Courses"))
parser.add_argument("--batch-size", type=int, default=100)
parser.add_argument("--recreate", action="store_true")
parser.add_argument("--resume", action="store_true")
parser.add_argument(
    "--dataset",
    choices=("all", "gen-eds"),
    default="all",
    help="Upload every dataset or only the small GenEd dataset for a smoke test.",
)
args = parser.parse_args()

required_env = ["QDRANT_API_KEY", "QDRANT_LINK"]
missing_env = [name for name in required_env if not os.getenv(name)]
if missing_env:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing_env)}")

qdrant_manager = QdrantManager(
    qdrant_api_key=os.environ["QDRANT_API_KEY"],
    host=os.environ["QDRANT_LINK"],
)

if args.resume:
    collection_info = qdrant_manager.client.get_collection(args.collection)
    start_index = collection_info.points_count or 0
    qdrant_manager.collections[args.collection] = {'current_id': start_index}
    print(f"Resuming '{args.collection}' after {start_index} existing points")
else:
    qdrant_manager.create_collection(collection_name=args.collection, recreate=args.recreate)
    start_index = 0

courses_df = pd.read_csv('./schedule_of_classes_scraper/umd_schedule_of_classes_courses.csv')
course_catalog_df = pd.read_csv('./course_catalog_scraper/umd_catalog_courses.csv')
prefixes_df = pd.read_csv('./course_prefixes_dataset_creation/umd_course_prefixes.csv')
gen_eds_df = pd.read_csv('./gen_eds/gen_eds.csv')



all_texts = []
all_payloads = []

dataframes = [("gen_ed", gen_eds_df)] if args.dataset == "gen-eds" else [
    ("schedule", courses_df),
    ("catalog", course_catalog_df),
    ("prefix", prefixes_df),
    ("gen_ed", gen_eds_df),
]
for source, df in dataframes:
    for _, row in df.iterrows():
        content = " ".join(
            f"{col}: {row[col]}" for col in df.columns if pd.notna(row[col]) and row[col] != ""
        )
        all_texts.append(content)
        course_number = row.get("COURSE NUMBER")
        all_payloads.append({
            "source": source,
            "course_number": str(course_number).upper() if pd.notna(course_number) else None,
        })

print(f"Prepared {len(all_texts)} retrieval documents from all source rows")

# print("Done adding all texts!")

# Batch processing with tqdm progress bar
batch_size = args.batch_size
for i in tqdm(range(start_index, len(all_texts), batch_size), desc="Inserting batches", unit="batch"):
    batch = all_texts[i:i + batch_size]
    payload_batch = all_payloads[i:i + batch_size]
    qdrant_manager.add_texts(
        collection_name=args.collection,
        texts=batch,
        payloads=payload_batch,
    )

print(f"Inserted {len(all_texts)} items into '{args.collection}'")

qdrant_manager.client.close()
