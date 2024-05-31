import streamlit as st
import chatbot

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"

st.title("UMD Class Schedule Chatbot")
st.write("Ask me anything about UMD classes and schedules!")

user_input = st.text_input("Your Question:")

if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.")
elif user_input:
    with st.spinner("Getting response..."):
        response = chatbot.chatbot_response(user_input, openai_api_key)
    st.write("Answer:")
    st.write(response)
