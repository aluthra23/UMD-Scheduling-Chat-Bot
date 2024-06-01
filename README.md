# UMD Class Schedule Chatbot

## Overview

The UMD Class Schedule Chatbot is an AI-powered assistant designed to help students at the University of Maryland find detailed information about courses and schedules. This project leverages OpenAI's GPT-4o model and a custom vector store built with FAISS to provide accurate and timely responses to user queries about UMD classes.

[![Scheduling Chat Bot Demo](https://img.youtube.com/vi/KEKWtafWjeQ/0.jpg)](https://youtu.be/KEKWtafWjeQ)

## Features

- **Course Recommendations**: Get recommendations for courses and instructors based on your preferences.
- **Dynamic Data Updates**: The vector store updates automatically with the latest scheduling information to ensure the chatbot provides accurate answers.
- **Efficient Information Retrieval**: Utilizes a vector store for fast and efficient similarity searches.

## Technologies Used

- **Python**: The core programming language used for developing the project.
- **Streamlit**: A web application framework used to create the chatbot interface.
- **OpenAI API**: Provides the AI capabilities for understanding and responding to user queries.
- **LangChain**: A library for building language model applications.
- **FAISS (Facebook AI Similarity Search)**: Used to build and manage the vector store for efficient information retrieval.

## Project Structure

- **app.py**: The main application file that sets up the Streamlit interface and handles user interactions.
- **chatbot.py**: Contains the logic for generating responses using the OpenAI API and the vector store.
- **vector_store.py**: Manages the creation, loading, and updating of the vector store.
- **data_preprocessing.py**: Handles the loading and preprocessing of the datasets used to create the vector store.
- **timer.txt**: A file used to track the last update time of the vector store.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/umd-class-schedule-chatbot.git
   cd umd-class-schedule-chatbot
