from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document
from data_preprocessing import load_datasets
from datetime import datetime, timedelta
import os


class VectorStoreHandler:
    def __init__(self, api_key):
        self.api_key = api_key
        self.vector_store = None
        self.embeddings = OpenAIEmbeddings(api_key=api_key)
        self.timer_file = "timer.txt"
        self.vector_store_path = "umd_vector_store"

    def load_vector_store(self):
        if not self.vector_store_needs_update():
            self.vector_store = FAISS.load_local(self.vector_store_path, self.embeddings,
                                                 allow_dangerous_deserialization=True)
        else:
            self.vector_store = self.create_vector_store()

    def vector_store_needs_update(self):
        if not os.path.exists(self.timer_file):
            return True

        with open(self.timer_file, "r") as file:
            last_updated = datetime.fromisoformat(file.read().strip())

        return datetime.now() - last_updated > timedelta(hours=1)

    def create_documents(self, df, source_name):
        documents = []
        for _, row in df.iterrows():
            content = " ".join([f"{col}: {row[col]}" for col in df.columns])
            documents.append(Document(page_content=content, metadata={"source": source_name}))
        return documents

    def create_vector_store(self):
        courses, catalog, prefixes, gen_eds = load_datasets()
        course_docs = self.create_documents(courses, "schedule")
        catalog_docs = self.create_documents(catalog, "catalog")
        prefix_docs = self.create_documents(prefixes, "prefix")
        gen_eds_docs = self.create_documents(gen_eds, "gen_ed")
        all_documents = course_docs + catalog_docs + prefix_docs + gen_eds_docs

        self.vector_store = FAISS.from_documents(all_documents, self.embeddings)
        self.vector_store.save_local(self.vector_store_path)

        with open(self.timer_file, "w") as file:
            file.write(datetime.now().isoformat())

        return self.vector_store

    def similarity_search(self, query, k=5):
        if self.vector_store is None:
            self.load_vector_store()
        return self.vector_store.similarity_search(query, k=k)
