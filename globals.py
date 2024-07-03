import threading

github_lock = threading.Lock()

isEmbeddingsModelUpdated = False