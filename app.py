import openai
import streamlit as st
import chatbot
import globals


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

        if not globals.isEmbeddingsModelUpdated:
            spinner_text = "Updating our datasets (3-5 minutes) and Getting response..."

        with st.spinner(spinner_text):
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.chat_message("user").write(user_input)
            try:
                response = chatbot.chatbot_response(user_input, openai_api_key)
            except openai.AuthenticationError:
                response = "Invalid OpenAI API key. Please enter a valid key."
            except:
                response = f"An error occurred. Try again."

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)