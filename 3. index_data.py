import marqo
import os
from dotenv import load_dotenv
from tqdm import tqdm
from workercontext import parallelise
from utils.document_loader import AmazonDocumentLoader
from threading import Lock
import argparse

from typing import List

marqo.set_log_level("WARN")

load_dotenv()

MARQO_API_URL = os.getenv("MARQO_API_URL", "http://localhost:8882")
MARQO_API_KEY = os.getenv("MARQO_API_KEY", None)
INDEX_NAME = os.getenv("INDEX_NAME", "amazon-example")

MQ = marqo.Client(MARQO_API_URL, api_key=MARQO_API_KEY)

INDEX_LOG_FILE = f"{INDEX_NAME}_indexed_docs.log"
DISK_STREAM_BATCH_SIZE = 512
CLIENT_BATCH_SIZE = 16
N_PROCESSES = 1


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


def index_batch(batch: List[dict]):
    lock = Lock()
    response = MQ.index(INDEX_NAME).add_documents(
        batch, client_batch_size=CLIENT_BATCH_SIZE
    )
    log_indexed_docs(response, INDEX_LOG_FILE, lock)
    for r in response:
        if r["errors"]:
            print(r)


def main():
    parser = argparse.ArgumentParser(
        prog='3. Index_data',
        description='Indexes amazon products data into Marqo'
    )
    parser.add_argument('--device', type=str, default='cpu', help='Device that is avaliable to Marqo')

    args = parser.parse_args()

    if args.device == 'gpu':
        global CLIENT_BATCH_SIZE
        CLIENT_BATCH_SIZE = 32
        global N_PROCESSES
        N_PROCESSES = 6

    data_path = os.path.join("data", "amazon_products.jsonl")
    data_loader = AmazonDocumentLoader(data_path)

    done = load_indexed_docs(INDEX_LOG_FILE)

    for batch in tqdm(
        data_loader.stream_from_disk(batch_size=DISK_STREAM_BATCH_SIZE),
        total=data_loader.batch_len(DISK_STREAM_BATCH_SIZE),
    ):
        batch = [d for d in batch if d["_id"] not in done]
        if not batch:
            continue
        parallelise(index_batch, n_processes=N_PROCESSES)(batch)


if __name__ == "__main__":
    main()
