from github import Github
# Authentication is defined via github.Auth
from github import Auth
import time
import streamlit as st
from globals import github_lock

# using an access token
# GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
# auth = Auth.Token(GITHUB_TOKEN)
auth = Auth.Token(" ")


def update_file_on_github(filepath):
    g = Github(auth=auth, timeout=300)
    repo = g.get_repo("aluthra23/UMD-Scheduling-Chat-Bot")

    with github_lock:
        try:
            repo.get_contents("logging")
            return
        except:
            try:
                repo.create_file("logging", "Create logging file", "Process started.", branch='main')
            except:
                return

        with open(filepath, "rb") as file:
            file_content = file.read()

            try:
                g = Github(auth=auth, timeout=300)
                repo = g.get_repo("aluthra23/UMD-Scheduling-Chat-Bot")

                contents = repo.get_contents(filepath)

                repo.update_file(path=filepath, message=str(repr(f"Updated {filepath}")), content=file_content,
                                 sha=contents.sha, branch='main')

                g.close()
            except:
                pass
            finally:
                try:
                    logging_file = repo.get_contents("logging")
                    repo.delete_file("logging", "Delete logging file", logging_file.sha, branch='main')
                except:
                    pass
