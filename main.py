import os
import pandas as pd
from dotenv import load_dotenv

from qdrant_manager import QdrantManager

load_dotenv()


collection_name = "hithere"
qdrant_manager = QdrantManager(api_key=os.getenv('API_KEY'), host=os.getenv('QDRANT_LINK'))

qdrant_manager.create_collection(collection_name=collection_name)

courses_df = pd.read_csv('./schedule_of_classes_scraper/umd_schedule_of_classes_courses.csv')
course_catalog_df = pd.read_csv('./course_catalog_scraper/umd_catalog_courses.csv')
prefixes_df = pd.read_csv('./course_prefixes_dataset_creation/umd_course_prefixes.csv')
gen_eds_df = pd.read_csv('./gen_eds/gen_eds.csv')



for df in courses_df, course_catalog_df, prefixes_df, gen_eds_df:
    for _, row in df.iterrows():
        # Concatenate each property for each element which is appended into the list of documents
        content = " ".join([f"{col}: {row[col]}" for col in df.columns])
        qdrant_manager.add_text(
            collection_name=collection_name,
            text=content
        )
        print(content)


qdrant_manager.client.close()