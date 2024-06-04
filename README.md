# UMD Scheduling Chatbot

## Overview

The UMD Scheduling Chatbot is an AI-powered assistant designed to help students at the University of Maryland find detailed information about courses and schedules. This project leverages OpenAI's GPT-4o model and a custom vector store built with FAISS to provide accurate and timely responses to user queries about UMD classes. For a live demo, visit the [UMD Scheduling Chat Bot](https://umd-chat-bot.streamlit.app/).

[![Scheduling Chat Bot Demo](https://img.youtube.com/vi/KEKWtafWjeQ/0.jpg)](https://youtu.be/KEKWtafWjeQ)

## Features

- **Course Recommendations**: Get recommendations for courses and instructors based on your preferences.
- **Dynamic Data Updates**: The vector store updates automatically with the latest scheduling information to ensure the chatbot provides accurate answers.
- **Efficient Information Retrieval**: Utilizes a vector store for fast and efficient similarity searches.

## Technologies Used

- **Python**: The core programming language used for developing the project.
- **Streamlit**: A web application framework used to create the chatbot interface. Streamlit allows for easy deployment and interaction with machine learning models.
- **OpenAI API**: The OpenAI API, particularly the GPT-40 model, is the backbone of the chatbot's natural language understanding and generation capabilities. It processes user queries and generates relevant, context-aware responses. Using this API incurs costs based on usage, which can be found on [OpenAI's pricing page](https://openai.com/pricing).
- **LangChain**: LangChain is a framework designed to streamline the development of language model applications. It provides tools and utilities for integrating various language model functionalities, making it easier to build complex conversational AI systems like the UMD Scheduling Chatbot.
- **FAISS (Facebook AI Similarity Search)**: FAISS is a library developed by Facebook AI Research for efficient similarity search and clustering of dense vectors. In the UMD Scheduling Chatbot, FAISS was used to build and manage the vector store for efficient information retrieval. FAISS enables fast similarity searches, ensuring the chatbot can quickly find relevant course information. We chose to implement a vector store because it offers a scalable and efficient way to store and retrieve course information. By encoding course details into dense vectors, we can perform similarity searches quickly and accurately, providing users with relevant information in real-time.

## Project Structure

- **app.py**: The main application file that sets up the Streamlit interface and handles user interactions.
- **chatbot.py**: Contains the logic for generating responses using the OpenAI API and the vector store. This file orchestrates the conversation flow and ensures seamless interaction with users.
- **vector_store.py**: Manages the creation, loading, and updating of the vector store. This component ensures that the chatbot has access to the latest scheduling information and can provide accurate responses. FAISS is used extensively within this module to build and manage the vector store efficiently.
- **data_preprocessing.py**: Handles the loading and preprocessing of the datasets used to create the vector store. This file ensures that the data is formatted and indexed correctly for efficient searching.
- **timer.txt**: A file used to track the last update time of the vector store. This ensures that the vector store is regularly updated with the latest scheduling information.

## Costs

- **OpenAI API Costs**: Using the OpenAI API incurs costs based on the number of requests and the amount of data processed. The pricing varies depending on the specific model used and the volume of API calls. Refer to [OpenAI's pricing page](https://openai.com/pricing) for detailed information.
- **Infrastructure Costs**: Running the application on a server (e.g., AWS, Google Cloud, Azure) will incur costs based on the server's specifications and usage. These costs include compute resources, storage, and network bandwidth. Additionally, while hosting a public repository on GitHub is free, using private repositories or additional GitHub Actions minutes may incur charges. Refer to [GitHub's pricing page](https://github.com/pricing) for more details.

## Usage

Once the application is running, you can interact with the chatbot via the Streamlit interface. Enter your query in the chat input, and the chatbot will respond with detailed information about UMD courses and schedules.

## Contributions

Contributions are welcome! Please fork the repository and submit a pull request with your changes. Ensure your code follows the project's coding standards and includes appropriate tests.

## License

This project is licensed under the [MIT License](LICENSE). See the LICENSE file for details.
