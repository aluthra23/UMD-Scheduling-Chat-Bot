import os

from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    PayloadSchemaType,
    PointStruct,
    VectorParams,
)


os.environ["TOKENIZERS_PARALLELISM"] = "false"


class QdrantManager:
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSIONS = 384

    def __init__(self, qdrant_api_key: str, host: str = "localhost"):
        self.client = QdrantClient(url=host, api_key=qdrant_api_key)
        self.collections = {}
        self.model = TextEmbedding(model_name=self.EMBEDDING_MODEL)

    def create_collection(self, collection_name, recreate=False):
        if self.client.collection_exists(collection_name):
            if not recreate:
                raise ValueError(
                    f"Collection '{collection_name}' already exists. "
                    "Pass recreate=True to replace it."
                )
            self.client.delete_collection(collection_name)

        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=self.EMBEDDING_DIMENSIONS,
                distance=Distance.COSINE,
            ),
        )
        self.client.create_payload_index(
            collection_name=collection_name,
            field_name="course_number",
            field_schema=PayloadSchemaType.KEYWORD,
        )
        metadata = {"current_id": 0}
        self.collections[collection_name] = metadata
        print(f"Collection '{collection_name}' created successfully")
        return metadata

    def add_texts(self, collection_name: str, texts: list[str], payloads: list[dict]):
        if collection_name not in self.collections:
            raise ValueError(f"Collection '{collection_name}' does not exist")

        current_id = self.collections[collection_name]["current_id"]
        embeddings = self.model.embed(texts, batch_size=len(texts), parallel=None)
        points = [
            PointStruct(
                id=current_id + index,
                vector=embedding.tolist(),
                payload={"text": text, **payloads[index]},
            )
            for index, (text, embedding) in enumerate(zip(texts, embeddings))
        ]
        self.client.upsert(collection_name=collection_name, points=points)
        self.collections[collection_name]["current_id"] += len(points)
        print(f"Inserted {len(points)} points into '{collection_name}' collection.")
