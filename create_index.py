import marqo
import os
from dotenv import load_dotenv

load_dotenv()

MARQO_API_URL = os.getenv("MARQO_API_URL", "http://localhost:8882")
MARQO_API_KEY = os.getenv("MARQO_API_KEY", None)
INDEX_NAME = os.getenv("INDEX_NAME", "amazon-example")

MODEL = "open_clip/ViT-B-16-SigLIP-384/webli"
VECTOR_NUMERIC_TYPE = "bfloat16"


def main():
    mq = marqo.Client(MARQO_API_URL, api_key=MARQO_API_KEY)

    # check if the index already exists
    indexes = mq.get_indexes()
    for index in indexes["results"]:
        if index["indexName"] == INDEX_NAME:
            choice = input(
                f"Index {INDEX_NAME} already exists. Do you want to delete it? (y/n): "
            )
            while choice not in ["y", "n"]:
                choice = input("Please enter 'y' or 'n': ")
            if choice == "y":
                mq.delete_index(INDEX_NAME)
                print("Index deleted successfully!")
            else:
                print("Exiting...")
                return

    index_settings = {
        "type": "structured",
        "model": MODEL,
        "normalizeEmbeddings": True,
        "vectorNumericType": VECTOR_NUMERIC_TYPE,
        "annParameters": {
            "spaceType": "prenormalized-angular",
            "parameters": {"efConstruction": 512, "m": 16},
        },
        "allFields": [
            {"name": "main_category", "type": "text", "features": ["filter"]},
            {"name": "title", "type": "text", "features": ["lexical_search"]},
            {"name": "store", "type": "text", "features": ["lexical_search", "filter"]},
            {"name": "features", "type": "array<text>", "features": ["lexical_search"]},
            {"name": "description", "type": "text", "features": ["lexical_search"]},
            {"name": "categories", "type": "array<text>", "features": ["filter"]},
            {"name": "average_rating", "type": "float", "features": ["score_modifier"]},
            {"name": "rating_number", "type": "float", "features": ["score_modifier"]},
            {"name": "price", "type": "float", "features": ["score_modifier"]},
            {"name": "details", "type": "text", "features": ["lexical_search"]},
            {"name": "product_image", "type": "image_pointer"},
            {
                "name": "multimodal_image_title",
                "type": "multimodal_combination",
                "dependentFields": {"product_image": 0.9, "title": 0.1},
            },
        ],
        "tensorFields": ["multimodal_image_title"],
    }

    mq.create_index(INDEX_NAME, settings_dict=index_settings)
    print("Index created successfully!")

    # this triggers marqo to download the model
    # not needed with Marqo Cloud
    print("Warming the model...")
    mq.index(INDEX_NAME).search("")
    print("Model warmed up!")


if __name__ == "__main__":
    main()
