import google.generativeai as genai


def chatbot_response(query: str, api_key: str, results, conversation_history: list):
    """
    Generates and returns a response based on the user-inputted query using Google's Gemini model
    referenced using a user-inputted API key

    :param query: user-inputted query
    :param api_key: user-inputted Google API key
    :param results: most similar results from Vector DB
    :return: a response generated by Gemini to the user-inputted query
    """

    if not results:
        return "No relevant context found!"

    # Joins the content of the documents into a single string, separated by double newlines
    context = ""
    for result in results:
        context += result.payload['text'] + "\n\n"

    # Configure the Gemini API
    genai.configure(api_key=api_key)

    # Create the model instance
    model = genai.GenerativeModel('gemini-1.0-pro')

    history_context = "\n".join(conversation_history[-6:]) if conversation_history else ""

    # Construct the prompt
    prompt = (
        f"Use the following information to answer the query.\n\n{context}\n\n"
        f"Conversation History: {history_context}"
        f"Query: {query}\n\n"
        f"Provide a detailed and accurate response based on the information provided."
    )

    try:
        # Generate content using Gemini
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                # max_output_tokens=1000,
                temperature=0.1,
            )

        )

        return response.text.strip()
    except Exception as e:
        return f"An error occurred. Please try again."