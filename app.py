import flask
from flask_cors import CORS
import marqo
import os
from utils.constants import RETRIEVAL_METHOD_TO_RANK
from dotenv import load_dotenv


from typing import Literal, List, Union

app = flask.Flask(__name__)
CORS(app)

load_dotenv()

MARQO_API_URL = os.getenv("MARQO_API_URL", "http://localhost:8882")
MARQO_API_KEY = os.getenv("MARQO_API_KEY", None)
INDEX_NAME = os.getenv("INDEX_NAME", "amazon-example")

MQ = marqo.Client(MARQO_API_URL, api_key=MARQO_API_KEY)

@app.route("/health")
def health():
    return "Backend is healthy"


@app.route("/")
def index():
    return flask.send_from_directory("static", "index.html")


def get_modifiers(
    order_by: Literal[
        None,
        "asc_average_rating",
        "desc_average_rating",
        "asc_rating_number",
        "desc_rating_number",
        "asc_price",
        "desc_price",
    ]
) -> List[str]:
    if order_by is None:
        return None

    order, by = order_by.split("_", 1)

    if order == "asc":
        weight = -0.1
    else:
        weight = 0.1

    return {
        "add_to_score": [{"field_name": by, "weight": weight}],
    }


@app.route("/search", methods=["POST"])
def search():
    data = flask.request.json
    query = data["query"]
    search_type: Literal["tensor", "lexical", "hybrid"] = data["search_type"]
    retrieval_method: Literal[None, "lexical", "tensor", "disjunction"] = data.get(
        "retrieval_method"
    )

    ranking_method = RETRIEVAL_METHOD_TO_RANK[retrieval_method]
    lexical_searchable_attributes: Union[None, List[
        Literal["title", "store", "features", "description", "categories", "details"]
    ]] = data.get("lexical_searchable_attributes")
    order_by: Literal[None, "average_rating", "rating_number", "price"] = data.get(
        "order_by"
    )
    alpha: float = data.get("alpha", 0.5)

    modifiers = get_modifiers(order_by)

    searchable_attributes = None
    if search_type != "tensor":
        searchable_attributes = lexical_searchable_attributes

    hybrid_parameters = None
    if search_type == "hybrid":
        hybrid_parameters = {
            "retrievalMethod": retrieval_method,
            "rankingMethod": ranking_method,
            "searchableAttributesLexical": searchable_attributes,
            "scoreModifiersTensor": modifiers,
            "scoreModifiersLexical": modifiers,
        }
        if ranking_method == "rrf":
            hybrid_parameters["alpha"] = alpha
            hybrid_parameters["rrfK"] = 60

    results = MQ.index(INDEX_NAME).search(
        q=query,
        search_method=search_type,
        limit=100,
        hybrid_parameters=hybrid_parameters,
        score_modifiers=modifiers if hybrid_parameters is None else None,
    )
    print(results)

    return results


if __name__ == "__main__":
    app.run(port=5000)
