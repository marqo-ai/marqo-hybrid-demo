from utils.document_loader import AmazonDocumentLoader
import os
import json
from tqdm import tqdm

data_path = os.path.join("data", "meta_Amazon_Fashion.jsonl")

rows = []

data = AmazonDocumentLoader(data_path)
for batch in tqdm(data.stream_from_disk(batch_size=256), total=data.batch_len(256)):
    for md, d in batch:
        if md["price"] >= 0 and md["product_image"]:
            rows.append(d)

with open("amazon_fashion_clean.jsonl", "w") as f:
    for row in rows:
        f.write(json.dumps(row) + "\n")
