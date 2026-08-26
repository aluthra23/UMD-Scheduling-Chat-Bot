import os

from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    PayloadSchemaType,
    PointIdsList,
    PointStruct,
    VectorParams,
)


os.environ["TOKENIZERS_PARALLELISM"] = "false"


class QdrantManager:
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSIONS = 384

    def __init__(self, qdrant_api_key: str, host: str = "localhost"):
        self.client = QdrantClient(url=host, api_key=qdrant_api_key)
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
        print(f"Collection '{collection_name}' created successfully")

    def existing_documents(self, collection_name: str):
        documents = {}
        offset = None
        while True:
            points, offset = self.client.scroll(collection_name, limit=256, offset=offset, with_payload=["document_key", "content_hash"], with_vectors=False)
            for point in points:
                payload = point.payload or {}
                if not payload.get("document_key") or not payload.get("content_hash"):
                    return None
                documents[payload["document_key"]] = {"id": point.id, "content_hash": payload["content_hash"]}
            if offset is None:
                return documents

    def upsert_documents(self, collection_name: str, documents: list[dict]):
        if not documents:
            return
        embeddings = self.model.embed([document["text"] for document in documents], batch_size=len(documents), parallel=None)
        self.client.upsert(collection_name=collection_name, points=[
            PointStruct(id=document["id"], vector=embedding.tolist(), payload=document["payload"])
            for document, embedding in zip(documents, embeddings)
        ])

    def delete_points(self, collection_name: str, point_ids: list[str]):
        if point_ids:
            self.client.delete(collection_name=collection_name, points_selector=PointIdsList(points=point_ids))

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
