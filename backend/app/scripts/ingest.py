import json
import os

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
        self.client.indices.delete(index="serp-ai", ignore_unavailable=True)
        self.client.indices.create(index="serp-ai", mappings=custom_mapping)

        return self.client


if __name__ == "__main__":
    pass
