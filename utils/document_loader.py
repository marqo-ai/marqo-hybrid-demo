from typing import Generator, List, Union, Tuple
import json
import re


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
            "main_category": document["main_category"]
            if document["main_category"]
            else "",
            "title": document["title"],
            "store": document["store"] if document["store"] else "",
            "features": document["features"],
            "description": " ".join(document["description"]),
            "categories": document["categories"],
            "average_rating": document["average_rating"],
            "rating_number": document["rating_number"],
            "price": self._coerce_price(document["price"]),
            "details": json.dumps(document["details"]),
            "product_image": document["images"][0]["large"]
            if len(document["images"]) > 0
            else None,
            "sponsored": False,
            "bid_amount": 0,
        }
        return marqo_document

    def _coerce_price(self, price: Union[None, str, int, float]) -> float:
        if price is None:
            return -1
        elif isinstance(price, str):
            try:
                return float(price)
            except ValueError:
                pass
            float_part = re.search(r"\d+\.?\d+", price)
            if float_part is None:
                return -1
            price = float_part.group().strip()
            return float(price)
        elif isinstance(price, int):
            return float(price)
        return float(price)

    def stream_from_disk(
        self, batch_size: int = 256, return_raw: bool = False
    ) -> Generator[List[Union[dict, Tuple[dict, dict]]], None, None]:
        with open(self.file_path, "r") as f:
            line_batch = []
            for line in f:
                document = json.loads(line)
                marqo_document = self._format_for_marqo(document)

                if return_raw:
                    line_batch.append((marqo_document, document))
                else:
                    line_batch.append(marqo_document)

                if len(line_batch) == batch_size:
                    yield line_batch
                    line_batch = []
