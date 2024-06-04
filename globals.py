import threading

# Define a universal lock accessible from multiple modules
universal_lock = threading.Lock()
github_lock = threading.Lock()
embeddingModelBeingUpdated = threading.Lock()

isEmbeddingsModelUpdated = True
