# Hybrid E-Commerce Search with Marqo

In this repo we provide a basic implementation for e-commerce product search with Marqo using hybrid search and real e-commerce data from Amazon.

# Setup
To set up your environment, you can use the following commands:

## python
```python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Marqo
A GPU is highly recommended for this demo, running without a GPU will be very slow for this model and dataset.

You can then run Marqo on CPU with:
```bash
docker run --name marqo -it -e MARQO_MODELS_TO_PRELOAD="[]" -p 8882:8882 marqoai/marqo:2.11
```
Or if you have GPU:
You can then run Marqo on CPU with:
```bash
docker run --gpus all --name marqo -it -e MARQO_MODELS_TO_PRELOAD="[]" -p 8882:8882 marqoai/marqo:2.11
```

### Marqo Cloud
Alternatively, you can use [Marqo Cloud](https://cloud.marqo.ai) to use Marqo cloud for this demo. See the [Running with Marqo Cloud](#running-with-marqo-cloud) section for more details.

# Step 1: Get the Data

## Use our cleaned dataset (recommended)
We made a cleaned dataset ready to go which you can use to get started quickly. This dataset contains 500,000 products from the following categories: `All_Beauty`, `Amazon Fashion`, `Appliances`, `Baby_Products`, `Beauty_and_Personal_Care`, and `Clothing_Shoes_and_Jewelry`.

Download the dataset:
```bash
mkdir data
wget https://marqo-public-demo-data.s3.amazonaws.com/amazon_products-500k.jsonl -O data/amazon_products.jsonl -q --show-progress
```

## Create your own dataset (optional)

If you want to experiment with other categories you can make your own dataset.

```bash
mkdir data_raw
```
To do so, download whichever categories you want from the [Amazon Reviews Dataset](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/tree/main/raw/meta_categories) and place them in the `data_raw` folder.

Then run the following command to create a single cleaned dataset:

```bash
python 1.prepare_data.py
```

# Step 2: Create an Index

We will use a structured index for this demo, you can refer to the script `2. create_index.py` to see the schema.

To create the index, run the following command:

```bash
python 2.create_index.py
```

In this index we use the `bfloat16` data type to save on space, this comes at a small cost to search latency.

# Step 3: Index the Data

We highly recommend using a machine with a GPU for indexing, CPU will be very slow. You can either use [Marqo Cloud](https://cloud.marqo.ai), a local GPU, or a cloud machine (e.g. a `g4dn.xlarge` instance on AWS).

To run indexing you can use the following command, if you have a GPU you can use the `--device "gpu"` flag to parallelize the indexing process:
```bash
python 3.index_data.py --device "cpu"
```

If you see the script printing out errors like the following:
```
'error': "Could not find image found at `https://m.media-amazon.com/images/I/31x9M1zwKoL._AC_.jpg`. \nReason: Marqo encountered an error when downloading the image url https://m.media-amazon.com/images/I/31x9M1zwKoL._AC_.jpg. The original error is: (28, 'Operation timed out after 3000 milliseconds with 0 bytes received')"
```

This is expected as the data contains numerous broken image links. You can ignore these errors as they will not affect the indexing process.

# Step 4: Search

Once indexing is running you can start searching right away, though it may be slowed down by the indexing process. We recommend waiting for a few thousand products to be indexed before starting to search so that there are more relevant results.

To run the UI and start interacting with the search engine, run the following command:
```bash
python app.py
```

# Step 5: Incorporate Sponsored Products

To incorporate a demo of sponsored search into the UI we provide a script to randomly sponsor products to simulate a real application. Sponsored products are identified with a filter and get given slots using an auction. 

To randomly sponsor products, run the following command:
```bash
python 4.randomly_sponsor_items.py
```

This script uses the partial update API in Marqo to update the sponsored products in real-time without touching the HNSW index.


# Running with Marqo Cloud

To run this demo on Marqo Cloud simply set the following environment variables:
```bash
export MARQO_API_KEY="your_api_key"
export MARQO_API_URL="https://api.marqo.ai"
```

The `2.create_index.py` script will automatically use Marqo Cloud if these environment variables are set and will create an index with GPU inference and a basic storage shard. This index will cost $1.0310 per hour. When you are done with the index you can delete it with the following code:

```python
import marqo
import os

mq = marqo.Client("https://api.marqo.ai", os.getenv("MARQO_API_KEY"))
mq.delete_index(os.getenv("INDEX_NAME", "amazon-example"))
```

If you do not delete your index you will continue to be charged for it.