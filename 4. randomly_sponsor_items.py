import marqo
import os
from dotenv import load_dotenv
from tqdm import tqdm
from workercontext import parallelise
import random
from utils.document_loader import AmazonDocumentLoader
from threading import Lock

from typing import List

marqo.set_log_level("WARN")

load_dotenv()

MARQO_API_URL = os.getenv("MARQO_API_URL", "http://localhost:8882")
MARQO_API_KEY = os.getenv("MARQO_API_KEY", None)
INDEX_NAME = os.getenv("INDEX_NAME", "amazon-example")

MQ = marqo.Client(MARQO_API_URL, api_key=MARQO_API_KEY)

INDEX_LOG_FILE = f"{INDEX_NAME}_indexed_docs.log"
SPONSOR_LOG_FILE = f"{INDEX_NAME}_sponsored_docs.log"
DISK_STREAM_BATCH_SIZE = 4096
CLIENT_BATCH_SIZE = 32
N_PROCESSES = 6
SPONSOR_RATE = 0.05

def load_logs(log_file: str) -> set:
    if not os.path.exists(log_file):
        return set()

    with open(log_file, "r") as f:
        return set(f.read().splitlines())

def log_sponsored_docs(response: dict, log_file: str, lock: Lock):
    with lock:
        with open(log_file, "a") as f:
            for item in response["items"]:
                if item["status"] == 200:
                    f.write(item["_id"] + "\n")


def update_batch(batch: List[str], sponsored: bool = False):
    lock = Lock()
    response = MQ.index(INDEX_NAME).update_documents(
        [{"_id": _id, "sponsored": sponsored, "bid_amount": random.random()} for _id in batch],
    )
    if sponsored:
        log_sponsored_docs(response, SPONSOR_LOG_FILE, lock)
    if response["errors"]:
        print(response)



def main():
    data_path = os.path.join("data", "amazon_products.jsonl")
    data_loader = AmazonDocumentLoader(data_path)

    sponsored = load_logs(SPONSOR_LOG_FILE)
    done = load_logs(INDEX_LOG_FILE)

    # reset all documents to not sponsored
    for batch in tqdm(
        data_loader.stream_from_disk(batch_size=DISK_STREAM_BATCH_SIZE),
        total=data_loader.batch_len(DISK_STREAM_BATCH_SIZE),
    ):
        batch = [doc["_id"] for doc in batch if doc["_id"] in sponsored]
        if not batch:
            continue
        parallelise(update_batch, n_processes=N_PROCESSES)(batch, False)

    # sponsor a random subset of documents
    to_sponsor = set(random.sample(list(done), int(len(done) * SPONSOR_RATE)))

    for batch in tqdm(
        data_loader.stream_from_disk(batch_size=DISK_STREAM_BATCH_SIZE),
        total=data_loader.batch_len(DISK_STREAM_BATCH_SIZE),
    ):
        batch = [doc["_id"] for doc in batch if doc["_id"] in to_sponsor]
        if not batch:
            continue
        parallelise(update_batch, n_processes=N_PROCESSES)(batch, True)


if __name__ == "__main__":
    main()
