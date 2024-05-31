from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document
from data_preprocessing import load_datasets

def create_documents(df, source_name):
    documents = []
    for _, row in df.iterrows():
        content = " ".join([f"{col}: {row[col]}" for col in df.columns])
        documents.append(Document(page_content=content, metadata={"source": source_name}))
    return documents

def create_vector_store(api_key):
    courses, catalog, prefixes, gen_eds = load_datasets()
    course_docs = create_documents(courses, "schedule")
    catalog_docs = create_documents(catalog, "catalog")
    prefix_docs = create_documents(prefixes, "prefix")
    gen_eds_docs = create_documents(gen_eds, "gen_ed")
    all_documents = course_docs + catalog_docs + prefix_docs + gen_eds_docs
    embeddings = OpenAIEmbeddings(api_key=api_key)
    vector_store = FAISS.from_documents(all_documents, embeddings)
    vector_store.save_local("umd_vector_store")
    return vector_store
