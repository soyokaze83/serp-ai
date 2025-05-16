import json
import os

from argparse import ArgumentParser
from typing import List, Dict
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from dotenv import load_dotenv

load_dotenv()
username = os.environ.get("ELASTIC_USERNAME")
password = os.environ.get("ELASTIC_PASSWORD")


class ESIngest:
    """
    Ingests document data into Elasticsearch index.
    """

    def __init__(self):
        self.client = None  # Initiate the client

    def ndjson_to_ls(self, ndjson_filepath: str):
        """Convert document information in NDJSON to ingestable list."""
        results = []

        with open(ndjson_filepath, "r") as file:
            doc = []
            for line in file:
                line = line.strip()
                load_doc = json.loads(line)
                doc.append(load_doc)

                if len(doc) % 2 == 0:
                    root_properties = doc[0]["index"]
                    root_properties["_source"] = doc[1]
                    doc = []
                    results.append(root_properties)

        return results

    def es_connect(
        self, hosts: List[str], cert_path: str, username: str, password: str
    ):
        """Connect to Elasticsearch and return client."""
        es_client = Elasticsearch(
            hosts=hosts, ca_certs=cert_path, basic_auth=(username, password)
        )

        if not es_client.ping():
            raise ValueError("Failed to connect to Elasticsearch client.")

        self.client = es_client
        return self.client

    def create_index(self, custom_mapping: Dict, index_name: str = "serp-ai"):
        """Rewrite index creation with index_name."""
        self.client.indices.delete(index=index_name, ignore_unavailable=True)
        self.client.indices.create(index=index_name, mappings=custom_mapping)

        return self.client

    def data_ingest(self, doc_ls: List[Dict]):
        """Bulk data ingestion of documents into Elasticsearch index."""
        if not self.client:
            raise ValueError("Client not yet set, please connect to a client.")

        try:
            success_count, errors = bulk(
                client=es_client,
                actions=doc_ls,
                # refresh="wait_for", # Optional: makes docs immediately searchable, use for testing, not high-load prod
                # chunk_size=500,     # Optional: Number of docs to send in a single request (default 500)
                # request_timeout=30  # Optional: Timeout for each chunk request (default 10s)
            )
            print(f"Successfully indexed {success_count} documents.")
            if errors:
                print(f"Encountered {len(errors)} errors:")
                for i, error_info in enumerate(errors):
                    print(f"Error {i+1}: {error_info}")

        except Exception as e:
            print(f"An exception occurred during bulk indexing: {e}")


if __name__ == "__main__":

    hosts = ["https://localhost:9200"]

    argparse = ArgumentParser()
    argparse.add_argument("--ndjson")
    argparse.add_argument("--ca_cert")
    args = argparse.parse_args()

    es_ingestor = ESIngest()
    es_client = es_ingestor.es_connect(
        hosts=hosts, cert_path=args.ca_cert, username=username, password=password
    )

    # Recreate the index
    custom_mapping = {
        "properties": {
            "citekey": {"type": "keyword"},
            "entry_type": {"type": "keyword"},
            "title": {"type": "text"},
            "abstract": {"type": "text"},
            "text": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "year": {"type": "integer"},
            "month": {"type": "keyword"},
            "address": {"type": "keyword"},
            "publisher": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "url": {"type": "keyword"},
            "authors": {"type": "keyword", "fields": {"text": {"type": "text"}}},
            "editors": {"type": "keyword", "fields": {"text": {"type": "text"}}},
            "booktitle": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "pages": {"type": "keyword"},
        }
    }

    es_client = es_ingestor.create_index(custom_mapping, index_name="serp-ai")
    doc_ls = es_ingestor.ndjson_to_ls(args.ndjson)

    # Ingest list of documents to index
    es_ingestor.data_ingest(doc_ls=doc_ls)
