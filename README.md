# Hybrid E-Commerce Search with Marqo

In this repo we provide a basic implementation for e-commerce product search with Marqo using hybrid search and real e-commerce data from Amazon.

# Setup
To set up your environment, you can use the following commands:

```python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

# Step 1: Get the Data

## Use our cleaned dataset (recommended)
We made a cleaned dataset ready to go which you can use to get started quickly. This dataset contains 20 million products from the following categories: `All_Beauty`, `Amazon Fashion`, `Appliances`, `Baby_Products`, `Beauty_and_Personal_Care`, and `Clothing_Shoes_and_Jewelry`.

Download the dataset:
```bash

```

## Create your own dataset (optional)

If you want to experiment with other categories you can make your own dataset.

To do so, download whichever categories you want from the [Amazon Reviews Dataset](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/tree/main/raw/meta_categories) and place them in the `data_raw` folder.

Then run the following command to create a single cleaned dataset:

```bash
python 1.\ prepare_data.py
```

# Step 2: Create an Index

We will use a structured index for this demo, you can refer to the script `2. create_index.py` to see the schema.

To create the index, run the following command:

```bash
python 2.\ create_index.py
```

In this index we use the `bfloat16` data type to save on space, this comes at a small cost to search latency.

# Step 3: Index the Data

We highly recommend using a machine with a GPU for indexing, CPU will be very slow. You can either use [Marqo Cloud](https://cloud.marqo.ai), a local GPU, or a cloud machine (e.g. a `g4dn.xlarge` instance on AWS).

To run indexing you can use the following command:
```bash
python 3.\ index_data.py
```

# Step 4: Search

Once indexing is running you can start searching right away, though it may be slowed down by the indexing process. We recommend waiting for a few thousand products to be indexed before starting to search so that there are more relevant results.

To run the UI and start interacting with the search engine, run the following command:
```bash
python 4.\ search.py
```

# Step 5: Incorporate Sponsored Products

To incorporate a demo of sponsored search into the UI we provide a script to randomly sponsor products to simulate a real application. Sponsored products are identified with a filter and get given slots using an auction. 

To randomly sponsor products, run the following command:
```bash
python 5.\ sponsor_products.py
```

This script uses the partial update API in Marqo to update the sponsored products in real-time without touching the HNSW index.