from fastapi import FastAPI, HTTPException, Depends
from app.services.services import (
    get_es_client,
    get_cross_encoder_model,
    perform_elasticsearch_search,
    rerank_with_cross_encoder,
)
from elasticsearch import Elasticsearch
from sentence_transformers import CrossEncoder
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


CROSS_ENCODER_MODEL_NAME = os.environ.get(
    "CROSS_ENCODER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Attempting to connect to Elasticsearch...")
    try:
        app.state.es_client = Elasticsearch(
            hosts=ES_HOSTS,
            ca_certs=ES_CERT_PATH,
            basic_auth=(ES_USERNAME, ES_PASSWORD),
        )
        if not app.state.es_client.ping():
            raise ValueError("Initial Elasticsearch ping failed.")
        print("Successfully connected to Elasticsearch.")
    except Exception as e:
        print(f"ERROR: Failed to connect to Elasticsearch during startup: {e}")
        raise

    print(f"Loading cross-encoder model: {CROSS_ENCODER_MODEL_NAME}...")
    try:
        app.state.cross_encoder_model = CrossEncoder(CROSS_ENCODER_MODEL_NAME)
        print("Cross-encoder model loaded successfully.")
    except Exception as e:
        print(f"ERROR: Failed to load cross-encoder model: {e}")
        raise

    yield

    print("Closing Elasticsearch connection...")
    if hasattr(app.state, "es_client"):
        try:
            app.state.es_client.close()
            print("Elasticsearch connection closed.")
        except Exception as e:
            print(f"ERROR: Failed to close Elasticsearch connection gracefully: {e}")

    if hasattr(app.state, "cross_encoder_model"):
        del app.state.cross_encoder_model
        print("Cross-encoder model released.")


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/search/{query}")
async def search_documents(
    query: str,
    es_client: Elasticsearch = Depends(get_es_client),
    cross_encoder_model: CrossEncoder = Depends(get_cross_encoder_model),
):
    try:
        initial_es_hits = perform_elasticsearch_search(query=query, es_client=es_client)

        if not initial_es_hits:
            return {"query": query, "initial_hits_count": 0, "reranked_hits": []}

        reranked_hits = rerank_with_cross_encoder(
            query=query, search_results=initial_es_hits, model=cross_encoder_model
        )

        return {
            "query": query,
            "initial_hits_count": len(initial_es_hits),
            "reranked_hits": reranked_hits,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Unhandled error in search_documents endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Search service error: {str(e)}")
