import openai
import streamlit as st
import chatbot
import os
from dotenv import load_dotenv
from qdrant_manager import QdrantManager

load_dotenv()

qdrant_manager = QdrantManager(api_key=st.secrets['API_KEY'], host=st.secrets['QDRANT_LINK'])
# Streamlit UI
with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"

st.title("UMD Scheduling Chatbot")
st.write("Ask me anything about UMD coursework and the courses that are being offered in the upcoming semester! "
         "Because the Schedule of Classes website is constantly being updated, our datasets need to be constantly "
         "updated as well, so there might be a slight delay the first time you ask something!")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if user_input := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    elif user_input:
        spinner_text = "Getting response..."

        with st.spinner(spinner_text):
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.chat_message("user").write(user_input)
            try:
                results = qdrant_manager.search_similar(
                    collection_name="course",
                    prompt=user_input,
                    limit=100,
                    similarity_threshold=0.2
                )
                response = chatbot.chatbot_response(user_input, openai_api_key, results)
            except openai.AuthenticationError:
                response = "Invalid OpenAI API key. Please enter a valid key."
            except:
                response = f"An error occurred. Try again."

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)