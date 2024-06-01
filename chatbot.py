import openai
from vector_database import VectorStoreHandler


def chatbot_response(query, api_key, k=50):
    vector_store_handler = VectorStoreHandler(api_key)
    docs = vector_store_handler.similarity_search(query, k=k)

    if not docs:
        return "I'm sorry, but I couldn't find any information related to your query. Please try again with different keywords."

    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = (
        f"You are an assistant for answering questions about University of Maryland classes and schedules. "
        f"Use the following information to answer the query.\n\n{context}\n\n"
        f"Query: {query}\n\n"
        f"Provide a detailed and accurate response based on the information provided."
    )

    client = openai.OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=200,
        temperature=0.5
    )

    return response.choices[0].message.content.strip()
