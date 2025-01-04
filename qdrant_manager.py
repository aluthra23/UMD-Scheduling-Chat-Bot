from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, PointStruct, Distance
from sentence_transformers import SentenceTransformer
import os
import ollama

# Environment setup
os.environ["TOKENIZERS_PARALLELISM"] = "false"


class QdrantManager:
    def __init__(self, api_key: str, host="localhost", port=6333):
        """
        Initialize Qdrant client with support for multiple collections

        :param host: Qdrant server host
        :param port: Qdrant server port
        """
        self.client = QdrantClient(url=host, port=port, api_key=api_key)

        # Store collections with their metadata
        self.collections = {}

        # Shared embedding model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def create_collection(self, collection_name, vector_size=384):
        """
        Create a new collection with specific parameters

        :param collection_name: Unique name for the collection
        :param vector_size: Dimension of embedding vectors
        :return: Collection metadata dictionary
        """
        try:
            # Delete existing collection if it exists
            self.client.delete_collection(collection_name)
        except:
            pass

        # Create new collection
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )

        # Initialize collection metadata
        collection_metadata = {
            'current_id': 0,
        }

        self.collections[collection_name] = collection_metadata

        print(f"Collection '{collection_name}' created successfully")
        return collection_metadata

    def delete_collection(self, collection_name):
        if collection_name not in self.collections:
            raise ValueError(f"Collection '{collection_name}' does not exist")

        self.client.delete_collection(collection_name)
        self.collections.pop(collection_name)

    def add_text(self, collection_name: str, text: str, company: str):
        """
        Add text to a specific collection

        :param collection_name: Name of the collection
        :param text: Text to be added
        :param company: company
        """
        # Ensure collection exists
        if collection_name not in self.collections:
            raise ValueError(f"Collection '{collection_name}' does not exist")

        # Get collection metadata
        collection_metadata = self.collections[collection_name]

        # Encode text
        embedding = self.model.encode(text)

        metadata = {
            "text": text,
            "company": company
        }

        self.client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=collection_metadata['current_id'],
                    vector=embedding.tolist(),
                    payload=metadata
                )
            ]
        )

        # Increment ID
        collection_metadata['current_id'] += 1

    def search_similar(self, collection_name, prompt, limit: int = 30, similarity_threshold: float = 0.2):
        """
        Search for similar texts in a specific collection

        :param collection_name: Name of the collection to search
        :param prompt: Search query
        :param limit: Maximum number of results
        :param similarity_threshold: Minimum similarity score
        :return: Filtered search results
        """
        # Ensure collection exists
        # if collection_name not in self.collections:
        #     raise ValueError(f"Collection '{collection_name}' does not exist")

        embedding = self.model.encode(prompt)
        results = self.client.search(
            collection_name=collection_name,
            query_vector=embedding.tolist(),
            limit=limit,
            with_payload=True
        )

        filtered_results = []

        for result in results:
            # if result.score >= similarity_threshold:
            #     filtered_results.append(result)
            #     print(f"Document: {result.payload['text']}")
            #     print(f"Score: {result.score}")
            filtered_results.append(result)

        return filtered_results
