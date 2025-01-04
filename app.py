import openai
import streamlit as st
import chatbot
import os
from dotenv import load_dotenv
from qdrant_manager import QdrantManager

load_dotenv()

qdrant_manager = QdrantManager(qdrant_api_key=st.secrets['QDRANT_API_KEY'], google_api_key= st.secrets['GOOGLE_API_KEY'], host=st.secrets['QDRANT_LINK'])
collection_name="gemini_courses"


st.title("UMD Scheduling Chatbot")
st.write("Ask me anything about UMD coursework and the courses that are being offered in the upcoming semester! ")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

if "conversation_history" not in st.session_state:
    st.session_state["conversation_history"] = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if user_input := st.chat_input():
    if user_input:
        spinner_text = "Getting response..."

        with st.spinner(spinner_text):
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.chat_message("user").write(user_input)
            try:
                results = qdrant_manager.search_similar(
                    collection_name=collection_name,
                    prompt=user_input,
                    limit=30,
                    similarity_threshold=0.5
                )

                response = chatbot.chatbot_response(
                    query=user_input,
                    api_key=st.secrets['GOOGLE_API_KEY'],
                    results=results,
                    conversation_history=st.session_state["conversation_history"]
                )
                st.session_state["conversation_history"].append(f"User: {user_input}")
                st.session_state["conversation_history"].append(f"Bot: {response}")


                if len(st.session_state["conversation_history"]) > 2:
                    st.session_state["conversation_history"] = st.session_state["conversation_history"][-2:]
            except openai.AuthenticationError:
                response = "Invalid OpenAI API key. Please enter a valid key."
            except Exception as e:
                print(e)
                response = f"An error occurred. Try again."

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)