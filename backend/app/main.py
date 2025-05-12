from fastapi import FastAPI, Request, HTTPException, Depends
from elasticsearch import Elasticsearch
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

load_dotenv()
ES_HOSTS = ["https://localhost:9200"]
ES_CERT_PATH = (
    "http_ca.crt"  # Ensure this path is correct relative to where you run the app
)
ES_USERNAME = os.environ.get("ELASTIC_USERNAME")
ES_PASSWORD = os.environ.get("ELASTIC_PASSWORD")
SEARCH_FIELDS = ["title", "abstract"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Attempting to connect to Elasticsearch...")
    try:
        app.state.es_client = Elasticsearch(
            hosts=ES_HOSTS,
            ca_certs=ES_CERT_PATH,
            basic_auth=(ES_USERNAME, ES_PASSWORD),
            # Optional: Add timeouts or retry logic
            # request_timeout=30,
            # max_retries=3,
            # retry_on_timeout=True,
        )
        if not app.state.es_client.ping():
            raise ValueError("Initial Elasticsearch ping failed.")
        print("Successfully connected to Elasticsearch.")
    except ConnectionError as e:
        print(f"ERROR: Failed to connect to Elasticsearch during startup: {e}")
        raise ValueError(f"Failed to connect to Elasticsearch: {e}") from e
    except Exception as e:
        print(f"ERROR: An unexpected error occurred during Elasticsearch setup: {e}")
        raise

    yield

    print("Closing Elasticsearch connection...")
    if hasattr(app.state, "es_client"):
        try:
            app.state.es_client.close()
            print("Elasticsearch connection closed.")
        except Exception as e:
            print(f"ERROR: Failed to close Elasticsearch connection gracefully: {e}")
    else:
        print("No Elasticsearch client found on app.state to close.")


app = FastAPI(lifespan=lifespan)


def get_es_client(request: Request) -> Elasticsearch:
    if not hasattr(request.app.state, "es_client"):
        raise HTTPException(
            status_code=503,
            detail="Elasticsearch client not available.",
        )
    return request.app.state.es_client


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/search/{query}")
def search_and_rerank(query: str, es_client: Elasticsearch = Depends(get_es_client)):
    try:
        response = es_client.search(
            index="serp-ai",
            size=100,
            query={
                "multi_match": {
                    "query": "architecture",
                    "fields": SEARCH_FIELDS,
                    "type": "most_fields",
                }
            },
        )

        results = response["hits"]["hits"]

        return {"query": query, "results": results}
    except Exception as e:
        print(f"ERROR: Elasticsearch error during search: {e}")
        raise HTTPException(status_code=500, detail=f"Search service error: {e}")
