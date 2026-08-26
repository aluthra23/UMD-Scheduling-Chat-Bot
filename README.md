# UMD Scheduling Chatbot

## Overview

The UMD Scheduling Chatbot is an AI-powered assistant designed to help students at the University of Maryland find detailed information about courses and schedules. This project leverages Gemini for response generation and embeddings, and Qdrant Cloud for the vector database to provide accurate and timely responses to user queries about UMD classes. For a live demo, visit <a href="https://umd-chat-bot.streamlit.app/" target="_blank" rel="noopener noreferrer">UMD Chat Bot<a>

[![Scheduling Chat Bot Demo](https://img.youtube.com/vi/KEKWtafWjeQ/0.jpg)](https://youtu.be/KEKWtafWjeQ)

## Features

- **Course Recommendations**: Get recommendations for courses and instructors based on your preferences.
- **Dynamic Data Updates**: The vector store updates automatically with the latest scheduling information to ensure the chatbot provides accurate answers.
- **Efficient Information Retrieval**: Utilizes a vector store for fast and efficient similarity searches.

## Technologies Used

- **Python**: The core programming language used for developing the project.
- **Streamlit**: Streamlit is a web application framework used to create the chatbot interface. It allows for rapid development and deployment of web applications with interactive widgets. We used Streamlit to build the user interface of the chatbot, providing an easy-to-use chat interface for users to interact with the AI. Streamlit also facilitates real-time updates and seamless interaction with the underlying machine learning models. Our application is deployed on Streamlit's cloud platform, ensuring easy access and scalability.
- **Gemini**: Gemini is used for both response generation and embeddings in this project. Gemini powers the chatbot's natural language understanding and generation capabilities, processing user queries and generating contextually relevant responses. It also creates embeddings for course data that are used for similarity searches.
- **Qdrant Cloud**: Qdrant Cloud is used as the vector database to store and manage embeddings. It enables efficient similarity searches, ensuring the chatbot can quickly find relevant course information. The vector store is periodically updated with the latest course information, allowing the chatbot to perform fast and accurate searches.

## Usage

Once the application is running, you can interact with the chatbot via the Streamlit interface. Enter your query in the chat input, and the chatbot will respond with detailed information about UMD courses and schedules.

## Vector Compatibility

The uploader uses the FP32 `sentence-transformers/all-MiniLM-L6-v2` model through FastEmbed. It creates normalized, 384-dimensional vectors for Qdrant. The JavaScript UI must use the matching model configuration when embedding queries.

If the model or its numeric precision is changed—for example, to an INT8 quantized build—the existing Qdrant vectors must not be reused. Recreate the collection and re-embed all source data so document and query vectors remain compatible. See the UI README for the quantization tradeoffs and migration checklist.

## Automated term refresh workflow

`.github/workflows/upload-next-term.yml` runs at minute `00` of every hour (UTC). It requires the GitHub Actions secrets `QDRANT_API_KEY` and `QDRANT_LINK`.

The workflow considers only Qdrant collections named as UMD term IDs (`YYYY01` for spring and `YYYY08` for fall):

1. Find the newest existing term collection and calculate the next term.
2. Check `CMSC351` using the UMD Courses API for that next term.
3. If the next term is published, scrape and synchronize that new term. A new collection receives a full initial upload.
4. If it is not published (`404` with `Course not found!`), scrape and synchronize the newest existing term instead. API/network failures fail the workflow rather than being treated as an unavailable term.

Each scrape includes open and closed sections. The uploader assigns deterministic UUIDs and hashes to every schedule, catalog, prefix, and GenEd document. On later runs it embeds and upserts only changed/new documents, and deletes only records that disappeared from the scrape. This avoids deleting the current term collection during ordinary hourly refreshes.

Existing legacy collections without `document_key` and `content_hash` metadata receive one full rebuild on their first incremental refresh. After that migration, unchanged data causes no embedding or Qdrant write.

To run it manually, open the workflow in the repository's **Actions** tab and use **Run workflow**. Leave the optional term blank to use the automatic new-term-or-latest-refresh decision; provide a term ID only to force a refresh of that specific term.

Important files for maintenance:

- `scripts/next_term.py` — newest/next term selection from Qdrant.
- `scripts/check_term.py` — next-term publication check.
- `scripts/scrape_and_upload.py` — orchestrates the three scrapers and upload.
- `main.py` and `qdrant_manager.py` — stable IDs, content hashes, and incremental Qdrant synchronization.

## Contributions

Contributions are welcome! Please fork the repository and submit a pull request with your changes. Ensure your code follows the project's coding standards and includes appropriate tests.

## License

This project is licensed under the [MIT License](LICENSE). See the LICENSE file for details.
