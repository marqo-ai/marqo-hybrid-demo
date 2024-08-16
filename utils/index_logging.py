import os
from threading import Lock


def load_indexed_docs(log_file: str) -> set:
    if not os.path.exists(log_file):
        return set()

    with open(log_file, "r") as f:
        return set(f.read().splitlines())


def log_indexed_docs(response: dict, log_file: str, lock: Lock):
    with lock:
        with open(log_file, "a") as f:
            for resp in response:
                for item in resp["items"]:
                    if item["status"] == 200:
                        f.write(item["_id"] + "\n")
