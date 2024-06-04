# UMD Scheduling Chatbot

## Overview

The UMD Scheduling Chatbot is an AI-powered assistant designed to help students at the University of Maryland find detailed information about courses and schedules. This project leverages OpenAI's GPT-40 model and a custom vector store built with FAISS to provide accurate and timely responses to user queries about UMD classes. For a live demo, visit [UMD Chat Bot](https://umd-chat-bot.streamlit.app/).

[![Scheduling Chat Bot Demo](https://img.youtube.com/vi/KEKWtafWjeQ/0.jpg)](https://youtu.be/KEKWtafWjeQ)

## Features

- **Course Recommendations**: Get recommendations for courses and instructors based on your preferences.
- **Dynamic Data Updates**: The vector store updates automatically with the latest scheduling information to ensure the chatbot provides accurate answers.
- **Efficient Information Retrieval**: Utilizes a vector store for fast and efficient similarity searches.

## Technologies Used

- **Python**: The core programming language used for developing the project.
- **Streamlit**: Streamlit is a web application framework used to create the chatbot interface. It allows for rapid development and deployment of web applications with interactive widgets. We used Streamlit to build the user interface of the chatbot, providing an easy-to-use chat interface for users to interact with the AI. Streamlit also facilitates real-time updates and seamless interaction with the underlying machine learning models. Our application is deployed on Streamlit's cloud platform, ensuring easy access and scalability.
- **OpenAI API**: The OpenAI API, particularly the GPT-40 model, is the backbone of the chatbot's natural language understanding and generation capabilities. It processes user queries and generates relevant, context-aware responses. Using this API incurs costs based on usage, which can be found on [OpenAI's pricing page](https://openai.com/pricing). The GPT-40 model is integrated using the OpenAI API to understand and generate human-like responses.
- **LangChain**: LangChain is a framework designed to streamline the development of language model applications. It enhances the chatbot's natural language processing capabilities, enabling it to understand complex queries and provide accurate responses. LangChain facilitates the creation of text embeddings, which are vector representations of text data. These embeddings are crucial for understanding the semantic meaning of user queries and the course information stored in the vector database. LangChain also helps create a vector database by converting course data into Document objects, which are then embedded into vectors. These vectors are stored in the FAISS index, enabling efficient similarity searches.
- **FAISS (Facebook AI Similarity Search)**: FAISS is a library developed by Facebook AI Research for efficient similarity search and clustering of dense vectors. In the UMD Scheduling Chatbot, FAISS is used to build and manage the vector store for efficient information retrieval. It enables fast similarity searches, ensuring the chatbot can quickly find relevant course information. The vector store is periodically updated with the latest course information, allowing the chatbot to perform fast and accurate searches.
- **Threading**: Threading is used to handle background updates to ensure that the vector store is always up-to-date with the latest course information. A separate thread is created to periodically check if an update is needed and perform the update without blocking the main application. This approach allows the chatbot to remain responsive while maintaining up-to-date data.

## Integration of Technologies

The integration of Streamlit, LangChain, FAISS, and the OpenAI API is crucial to the functionality of the UMD Scheduling Chatbot. Here's how these technologies work together:

1. **Data Preparation**: The `data_preprocessing.py` script handles the loading and preprocessing of datasets. This data is then converted into a list of Document objects using LangChain.
   
2. **Embedding and Storing Data**: These Document objects are embedded into vectors using the OpenAIEmbeddings model provided by LangChain. The embedded vectors are then stored in a FAISS index for efficient similarity search.

3. **Vector Store Management**: The `VectorStoreHandler` class in `vector_database.py` manages the creation, loading, and updating of the vector store. It uses FAISS for building and storing the vector database and LangChain for generating embeddings.

4. **Similarity Search**: When a user query is received, the chatbot uses the FAISS index to perform a similarity search on the vector store to find the most relevant documents. This process is managed by the `similarity_search` method in the `VectorStoreHandler` class.

5. **Response Generation**: The relevant documents are then used to generate a context for the query. The query and context are sent to the OpenAI API, which generates a detailed and contextually relevant response using the GPT-40 model.

6. **User Interface**: The Streamlit framework is used to create the user interface of the chatbot. Users interact with the chatbot through a simple and intuitive chat interface provided by Streamlit. Streamlit handles real-time interactions and updates, making the chatbot responsive and user-friendly.

7. **Background Updates**: To ensure the data is always up-to-date, threading is used to periodically update the vector store with the latest course information. This is managed by a separate thread that checks if an update is needed and performs the update without blocking the main application.

## Project Structure

- **app.py**: The main application file that sets up the Streamlit interface and handles user interactions.
- **chatbot.py**: Contains the logic for generating responses using the OpenAI API and the vector store. This file orchestrates the conversation flow and ensures seamless interaction with users.
- **vector_database.py**: Manages the creation, loading, and updating of the vector store. This component ensures that the chatbot has access to the latest scheduling information and can provide accurate responses. FAISS is used extensively within this module to build and manage the vector store efficiently.
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
