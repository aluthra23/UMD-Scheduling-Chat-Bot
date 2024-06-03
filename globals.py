import threading

# Define a universal lock accessible from multiple modules
universal_lock = threading.Lock()
isEmbeddingsModelUpdated = True