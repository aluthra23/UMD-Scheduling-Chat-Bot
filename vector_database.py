import threading

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document
from streamlit.runtime.scriptrunner import add_script_run_ctx
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx

import github_handling
from github_handling import update_file_on_github
import globals
from data_preprocessing import load_datasets
from datetime import datetime, timedelta
import os
from schedule_of_classes_scraper import main_soc_scraper


class VectorStoreHandler:
    """
    Create a FAISS vector store with additional properties to help load the vector store and determine
    when to update our datasets
    """

    def __init__(self, api_key):
        """
        Initializes a VectorStoreHandler which has a given api_key, stores a vector store, stores file
        paths to the timer files and vector store files, and also initializes an OpenAIEmbeddings model
        for generating text embeddings

        :param api_key: stores api_keys to all of our models and initializes an OpenAIEmbeddings model
        """
        self.api_key = api_key # Stores API key
        self.vector_store = None # Holds the FAISS vector store
        self.embeddings = OpenAIEmbeddings(api_key=api_key) # An embeddings model for generating text embeddings.
        self.vector_store_path = "umd_vector_store"  # Filepath where FAISS vector store is saved

    def load_vector_store(self):
        """
        Loads the current vector store or creates a new vector store if an update is required

        :return: a vector store with the UMD coursework data
        """

        with open("./timer.txt", "r") as file:
            last_updated = datetime.fromisoformat(file.read().strip())

        time_difference = datetime.now() - last_updated

        if (timedelta(hours=1) - time_difference).days < 0 or ((timedelta(hours=1) - time_difference).total_seconds()) < 0:
            globals.isEmbeddingsModelUpdated = False

            with open("timer.txt", "w") as file:
                current_time = datetime.now()
                updated_time = current_time.replace(minute=0, second=0, microsecond=0)

                file.write(updated_time.isoformat())

            self.vector_store = self.create_vector_store()

            globals.isEmbeddingsModelUpdated = True

        else:
            globals.isEmbeddingsModelUpdated = True

            # Loads the currently stored version of the vector store if no update needed
            self.vector_store = FAISS.load_local(folder_path=self.vector_store_path,
                                                 embeddings=self.embeddings,
                                                 allow_dangerous_deserialization=True)


    def create_vector_store(self):
        """
        Updates the current coursework data from the Schedule of Classes Website, and creates and returns
        a new vector store with the updated datasets

        :return: a vector store with the updated data
        """

        # Reads and loads the respective datasets as Pandas dataframes
        courses, catalog, prefixes, gen_eds = load_datasets()

        # Converts each dataset into a list of Document objects
        course_docs = self.create_documents(courses, "schedule")
        catalog_docs = self.create_documents(catalog, "catalog")
        prefix_docs = self.create_documents(prefixes, "prefix")
        gen_eds_docs = self.create_documents(gen_eds, "gen_ed")

        # Merges all the documents
        all_documents = course_docs + catalog_docs + prefix_docs + gen_eds_docs

        self.vector_store = FAISS.from_documents(all_documents, self.embeddings) # Builds vector store
        self.vector_store.save_local(self.vector_store_path) # Saves vector store to "./umd_vector_store"

        globals.isEmbeddingsModelUpdated = True

        return self.vector_store  # Returns the newly created vector store

    def similarity_search(self, query, k):
        """
        Performs a similarity search on the vector store to find documents similar to the query.

        :param query: string containing the prompt entered by the user
        :param k: a number to indicate we want to find the top 'k' documents similar to our query
        :return: a list of documents that are similar to the entered query
        """

        if self.vector_store is None:
            # Loads a vector store if it doesn't exist
            self.load_vector_store()
        return self.vector_store.similarity_search(query, k=k) # Finds top 'k' documents related to query


    def create_documents(self, df, source_name):
        """
        Converts a DataFrame into a list of Document objects for embedding and storage in the vector store

        :param df: refers to a dataframe
        :param source_name: a description of the data provided
        :return: a list of documents that will be used to build a vector store
        """

        documents = []  # Stores list of Documents storing the dataframe elements to be returned
        for _, row in df.iterrows():
            # Concatenate each property for each element which is appended into the list of documents
            content = " ".join([f"{col}: {row[col]}" for col in df.columns])
            documents.append(Document(page_content=content, metadata={"source": source_name}))
        return documents
