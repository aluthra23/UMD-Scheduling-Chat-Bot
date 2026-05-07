import pandas as pd
from dotenv import load_dotenv

from qdrant_manager import QdrantManager
import streamlit as st
from tqdm import tqdm

load_dotenv()

# raise Exception

collection_name = "Fall-2025-Courses"
qdrant_manager = QdrantManager(qdrant_api_key=st.secrets['QDRANT_API_KEY'], google_api_key= st.secrets['GOOGLE_API_KEY'], host=st.secrets['QDRANT_LINK'])

qdrant_manager.create_collection(collection_name=collection_name)

courses_df = pd.read_csv('./schedule_of_classes_scraper/umd_schedule_of_classes_courses.csv')
course_catalog_df = pd.read_csv('./course_catalog_scraper/umd_catalog_courses.csv')
prefixes_df = pd.read_csv('./course_prefixes_dataset_creation/umd_course_prefixes.csv')
gen_eds_df = pd.read_csv('./gen_eds/gen_eds.csv')



all_texts = []

for df in [courses_df, course_catalog_df, prefixes_df, gen_eds_df]:
    for _, row in df.iterrows():
        content = " ".join(
            f"{col}: {row[col]}" for col in df.columns if pd.notna(row[col]) and row[col] != ""
        )
        all_texts.append(content)

# print("Done adding all texts!")

# Batch processing with tqdm progress bar
batch_size = 1
for i in tqdm(range(0, len(all_texts), batch_size), desc="Inserting batches", unit="batch"):
    batch = all_texts[i:i + batch_size]
    qdrant_manager.add_texts(collection_name=collection_name, texts=batch)

print(f"Inserted {len(all_texts)} items")

qdrant_manager.client.close()
