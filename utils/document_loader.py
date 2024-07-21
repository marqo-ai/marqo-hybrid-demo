from typing import Generator, List
import json


class AmazonDocumentLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        with open(self.file_path, "rb") as f:
            self.num_lines = sum(1 for _ in f)

    def __len__(self):
        return self.num_lines

    def batch_len(self, batch_size: int) -> int:
        return self.num_lines // batch_size

    def _format_for_marqo(self, document: dict) -> dict:
        marqo_document = {
            "_id": document["parent_asin"],
            "main_category": document["main_category"],
            "title": document["title"],
            "store": document["store"],
            "features": document["features"],
            "description": " ".join(document["description"]),
            "categories": document["categories"],
            "average_rating": document["average_rating"],
            "rating_number": document["rating_number"],
            "price": document["price"] if document["price"] is not None else -1,
            "details": json.dumps(document["details"]),
            "product_image": document["images"][0]["large"]
            if len(document["images"]) > 0
            else None,
        }
        return marqo_document

    def stream_from_disk(
        self, batch_size: int = 256
    ) -> Generator[List[dict], None, None]:
        with open(self.file_path, "r") as f:
            line_batch = []
            for line in f:
                document = json.loads(line)
                marqo_document = self._format_for_marqo(document)
                # line_batch.append((marqo_document, document))
                line_batch.append(marqo_document)
                if len(line_batch) == batch_size:
                    yield line_batch
                    line_batch = []
