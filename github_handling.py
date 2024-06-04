from github import Github
# Authentication is defined via github.Auth
from github import Auth
import time
import streamlit as st

# using an access token
auth = Auth.Token("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")
# auth = Auth.Token(GITHUB_TOKEN)


def update_file_on_github(filepath):
    # filepath = "umd_vector_store/index.faiss"
    with open(filepath, "rb") as file:
        file_content = file.read()

        start_time_read = time.time()

        g = Github(auth=auth, timeout=120)
        repo = g.get_repo("aluthra23/UMD-Scheduling-Chat-Bot")

        contents = repo.get_contents(filepath)

        repo.update_file(filepath, "commit", file_content, contents.sha, branch='main')

        end_time_read = time.time()
        print(f"Time taken to upload the file: {end_time_read - start_time_read} seconds")

        # To close connections after use
        g.close()
