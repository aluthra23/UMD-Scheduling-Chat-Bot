import os

from dotenv import load_dotenv

from qdrant_manager import QdrantManager

load_dotenv()

qdrant_manager = QdrantManager(api_key=os.getenv('API_KEY'), host=os.getenv('QDRANT_LINK'))

qdrant_manager.create_collection(collection_name="course")

