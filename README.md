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

## Contributions

Contributions are welcome! Please fork the repository and submit a pull request with your changes. Ensure your code follows the project's coding standards and includes appropriate tests.

## License

This project is licensed under the [MIT License](LICENSE). See the LICENSE file for details.
