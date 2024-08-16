from utils.document_loader import AmazonDocumentLoader
import os
import json
import random
from tqdm import tqdm

os.makedirs("data", exist_ok=True)

data_files = os.listdir("data_raw")

rows = []
for f in data_files:
    fp = os.path.join("data_raw", f)

    data = AmazonDocumentLoader(fp)
    for batch in tqdm(
        data.stream_from_disk(batch_size=512, return_raw=True),
        total=data.batch_len(512),
    ):
        for md, d in batch:
            if md["price"] >= 0 and md["product_image"]:
                rows.append(d)

random.shuffle(rows)

with open(os.path.join("data", "amazon_products.jsonl"), "w") as f:
    for row in tqdm(rows, desc="Writing dataset"):
        f.write(json.dumps(row) + "\n")
