import marqo
import os
from dotenv import load_dotenv
from tqdm import tqdm
from utils.document_loader import AmazonDocumentLoader

load_dotenv()

MARQO_API_URL = os.getenv("MARQO_API_URL", "http://localhost:8882")
MARQO_API_KEY = os.getenv("MARQO_API_KEY", None)
INDEX_NAME = os.getenv("INDEX_NAME", "amazon-example")

MQ = marqo.Client(MARQO_API_URL, api_key=MARQO_API_KEY)

INDEX_LOG_FILE = f'{INDEX_NAME}_indexed_docs.log'
CLIENT_BATCH_SIZE = 16

def log_indexed_docs(response: dict, log_file: str):
    with open(log_file, "a") as f:
        for resp in response:
            for item in resp["items"]:
                if item["status"] == 200:
                    f.write(item['_id'] + "\n")

def main():
    data_path = os.path.join("data", "meta_Amazon_Fashion.jsonl")
    data_loader = AmazonDocumentLoader(data_path)


    for batch in tqdm(data_loader.stream_from_disk(batch_size=2), total=data_loader.batch_len(2)):
        response = MQ.index(INDEX_NAME).add_documents(batch, client_batch_size=CLIENT_BATCH_SIZE)
        log_indexed_docs(response, INDEX_LOG_FILE)
        for r in response:
            if r["errors"]:
                print(r)


if __name__ == "__main__":
    main()