import os
from openai import OpenAI
from langchain.vectorstores import FAISS
from vector_database import create_vector_store
from langchain.embeddings import OpenAIEmbeddings

vector_store = None


def load_vector_store(api_key):
    global vector_store
    if vector_store is None:
        embeddings = OpenAIEmbeddings(api_key=api_key)
        try:
            vector_store = FAISS.load_local("umd_vector_store", embeddings, allow_dangerous_deserialization=True)
        except FileNotFoundError:
            vector_store = create_vector_store(api_key)


def chatbot_response(query, api_key, k=3):
    load_vector_store(api_key)

    # Perform similarity search
    docs = vector_store.similarity_search(query, k=k)
    context = "\n\n".join([doc.page_content for doc in docs])
    print(context)
    prompt = f"Use the following information to answer the query.\n\n{context}\n\nQuery: {query}\n\nAnswer:"

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=200,
        temperature=0.5
    )
    return response.choices[0].message.content.strip()
