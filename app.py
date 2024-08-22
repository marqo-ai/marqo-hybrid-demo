import flask
from flask_cors import CORS
import marqo
import os
from utils.helpers import RETRIEVAL_METHOD_TO_RANK, get_modifiers, parse_body
from utils.auction import auction_spots_with_score
from dotenv import load_dotenv

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


@app.route("/number_of_documents", methods=["GET"])
def number_of_documents():
    stats = MQ.index(INDEX_NAME).get_stats()
    return stats


@app.route("/search", methods=["POST"])
def search():
    data = flask.request.json
    query, search_type, modifiers, hybrid_parameters = parse_body(data)
    results = MQ.index(INDEX_NAME).search(
        q=query,
        search_method=search_type,
        limit=200,
        hybrid_parameters=hybrid_parameters,
        score_modifiers=modifiers if hybrid_parameters is None else None,
    )
    return results


@app.route("/sponsored_search", methods=["POST"])
def sponsored_search():
    data = flask.request.json

    spots = data["auctionSpots"]

    query, search_type, _, hybrid_parameters = parse_body(data)

    results = MQ.index(INDEX_NAME).search(
        q=query,
        search_method=search_type,
        limit=200,
        hybrid_parameters=hybrid_parameters,
        filter_string="sponsored:true",
    )
    if not results["hits"]:
        return results

    results["hits"] = auction_spots_with_score(results["hits"], spots)
    return results


if __name__ == "__main__":
    app.run(port=5000)
