import openai
import streamlit as st
import chatbot
from datetime import datetime, timedelta
import os
import globals
from schedule_of_classes_scraper import main_soc_scraper
import time
import threading
from streamlit.runtime.scriptrunner import add_script_run_ctx
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx
from github_handling import update_file_on_github



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
            spinner_text = "Updating our datasets (1-2 minutes) and Getting response..."

        with st.spinner(spinner_text):
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.chat_message("user").write(user_input)
            try:
                response = chatbot.chatbot_response(user_input, openai_api_key)
            except openai.AuthenticationError:
                response = "Invalid OpenAI API key. Please enter a valid key."
            except Exception as e:
                response = f"An error occurred. Try again."

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)


# Function to check if an hour has passed since the last update
def check_update_needed():
    while True:
        with open("./timer.txt", "r") as file:
            last_updated = datetime.fromisoformat(file.read().strip())


        time_difference = datetime.now() - last_updated
        try:
            if (timedelta(hours=1) - time_difference).days < 0:
                time_to_sleep = 0.0
            else:
                time_to_sleep = max(0.0, (timedelta(hours=1) - time_difference).total_seconds())
        except:
            time_to_sleep = 0.0

        time.sleep(time_to_sleep)  # Sleep for the remaining time until the next hour

        # Writes the current time to the timer.txt file
        with open("timer.txt", "w") as file:
            current_time = datetime.now()
            updated_time = current_time.replace(minute=0, second=0, microsecond=0)

            file.write(updated_time.isoformat())

        with globals.universal_lock:
            globals.isEmbeddingsModelUpdated = False
            main_soc_scraper.update_current_semester_coursework_data(
                file_path=f"{os.getcwd()}/schedule_of_classes_scraper/umd_schedule_of_classes_courses.csv",
                course_prefixes_path=f"{os.getcwd()}/course_prefixes_dataset_creation/umd_course_prefixes.csv"
            )

            # update_file_on_github("timer.txt")
            # update_file_on_github("schedule_of_classes_scraper/umd_schedule_of_classes_courses.csv")


# Start a separate thread to check for updates in the background
update_thread = threading.Thread(target=check_update_needed, daemon=True)
ctx = get_script_run_ctx()
add_script_run_ctx(thread=update_thread, ctx=ctx)
update_thread.start()