from github import Github
# Authentication is defined via github.Auth
from github import Auth
import time
import streamlit as st
from globals import github_lock

# using an access token
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
auth = Auth.Token(GITHUB_TOKEN)


def update_file_on_github(filepath):
    with github_lock:
        with open(filepath, "rb") as file:
            file_content = file.read()

            try:
                g = Github(auth=auth, timeout=300)
                repo = g.get_repo("aluthra23/UMD-Scheduling-Chat-Bot")

                contents = repo.get_contents(filepath)

                repo.update_file(filepath, "commit", file_content, contents.sha, branch='main')

                g.close()
            except:
                pass