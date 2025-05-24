from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from app.services.services import (
    get_es_client,
    get_cross_encoder_model,
    perform_elasticsearch_search,
    rerank_with_cross_encoder,
    get_together_client,
    stream_rag_response,
)
from elasticsearch import Elasticsearch
from sentence_transformers import CrossEncoder
from together import Together
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import List, Dict, Optional, Any  # For type hinting
import json  # For JSONDecodeError

# Import Pydantic BaseModel
from pydantic import BaseModel, Field

load_dotenv()
ES_HOSTS = os.environ.get("ELASTIC_URL_PROD")
ES_API_KEY = os.environ.get("API_KEY")

TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY")
TOGETHER_DEFAULT_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
TOGETHER_MODEL_NAME = os.environ.get("TOGETHER_MODEL_NAME", TOGETHER_DEFAULT_MODEL)

CROSS_ENCODER_MODEL_NAME = os.environ.get(
    "CROSS_ENCODER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


class DocumentSourceModel(BaseModel):
    text: str
    title: Optional[str] = None
    citekey: Optional[str] = None
    abstract: Optional[str] = None
    year: Optional[int] = None
    authors: Optional[List[str]] = None
    url: Optional[str] = None

    class Config:
        extra = "allow"


class RerankedDocumentModel(BaseModel):
    _index: Optional[str] = None
    _id: Optional[str] = None
    _score: Optional[float] = None
    _source: DocumentSourceModel
    cross_encoder_score: Optional[float] = None


class SummarizationRequestModel(BaseModel):
    query: str
    documents: List[RerankedDocumentModel]


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Attempting to connect to Elasticsearch...")
    try:
        app.state.es_client = Elasticsearch(hosts=ES_HOSTS, api_key=ES_API_KEY)
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

    print(f"Initializing TogetherAI client with model: {TOGETHER_MODEL_NAME}...")
    if not TOGETHER_API_KEY:
        print("ERROR: TOGETHER_API_KEY not found in environment variables.")
        raise ValueError("TOGETHER_API_KEY is required but not set.")
    try:
        app.state.together_client = Together(api_key=TOGETHER_API_KEY)
        print("TogetherAI client initialized successfully.")
    except Exception as e:
        print(f"ERROR: Failed to initialize TogetherAI client: {e}")
        raise

    yield

    print("Closing Elasticsearch connection...")
    if hasattr(app.state, "es_client") and app.state.es_client:
        try:
            await app.state.es_client.close()
            print("Elasticsearch connection closed.")
        except Exception as e:
            print(f"ERROR: Failed to close Elasticsearch connection gracefully: {e}")

    if hasattr(app.state, "cross_encoder_model"):
        del app.state.cross_encoder_model
        print("Cross-encoder model released.")

    if hasattr(app.state, "together_client"):
        del app.state.together_client
        print("TogetherAI client released.")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        initial_es_hits = perform_elasticsearch_search(
            query=query, es_client=es_client, size=20
        )

        if not initial_es_hits:
            return {"query": query, "initial_hits_count": 0, "reranked_hits": []}

        reranked_hits = rerank_with_cross_encoder(
            query=query,
            search_results=initial_es_hits,
            model=cross_encoder_model,
            k=5,
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


@app.get("/rag_chat_legacy/{query}")
async def generative_search_stream_legacy(
    query: str,
    es_client: Elasticsearch = Depends(get_es_client),
    cross_encoder_model: CrossEncoder = Depends(get_cross_encoder_model),
    together_client: Together = Depends(get_together_client),
):
    try:
        initial_es_hits = perform_elasticsearch_search(
            query=query, es_client=es_client, size=20
        )
        if not initial_es_hits:

            async def empty_stream():
                yield "No documents found to answer the query."

            return StreamingResponse(empty_stream(), media_type="text/event-stream")

        reranked_top_5_hits = rerank_with_cross_encoder(
            query=query, search_results=initial_es_hits, model=cross_encoder_model, k=5
        )
        if not reranked_top_5_hits:

            async def no_relevant_docs_stream():
                yield "Found some documents, but none seemed highly relevant after reranking."

            return StreamingResponse(
                no_relevant_docs_stream(), media_type="text/event-stream"
            )

        response_generator = stream_rag_response(
            query=query,
            documents=reranked_top_5_hits,
            together_client=together_client,
            model_name=TOGETHER_MODEL_NAME,
        )
        return StreamingResponse(response_generator, media_type="text/event-stream")
    except HTTPException as e:

        async def error_stream():
            yield f"Service Error: {e.detail}"

        return StreamingResponse(
            error_stream(), media_type="text/event-stream", status_code=e.status_code
        )
    except Exception as e:
        print(
            f"ERROR: Unhandled error in generative_search_stream_legacy endpoint: {e}"
        )

        async def critical_error_stream():
            yield "An unexpected error occurred."

        return StreamingResponse(
            critical_error_stream(), media_type="text/event-stream", status_code=500
        )


@app.post("/summarize_documents_stream")
async def summarize_documents_stream(
    http_request: Request,
    together_client: Together = Depends(get_together_client),
):
    try:
        request_payload_dict = await http_request.json()
    except json.JSONDecodeError:  # Catch if JSON is malformed

        async def malformed_json_stream():
            yield "Invalid JSON format in request body."

        return StreamingResponse(
            malformed_json_stream(), media_type="text/event-stream", status_code=400
        )

    try:
        user_query = request_payload_dict.get("query")
        input_documents = request_payload_dict.get("documents")

        if not user_query or not isinstance(user_query, str):

            async def bad_query_stream():
                yield "Invalid or missing 'query' field in request body."

            return StreamingResponse(
                bad_query_stream(), media_type="text/event-stream", status_code=400
            )

        if not isinstance(input_documents, list):

            async def bad_documents_stream():
                yield "Missing 'documents' field in request body, or it is not a list."

            return StreamingResponse(
                bad_documents_stream(), media_type="text/event-stream", status_code=400
            )

        if not input_documents:

            async def empty_docs_stream():
                yield "No documents provided for summarization."

            return StreamingResponse(
                empty_docs_stream(), media_type="text/event-stream"
            )

        response_generator = stream_rag_response(
            query=user_query,
            documents=input_documents,
            together_client=together_client,
            model_name=TOGETHER_MODEL_NAME,
        )
        return StreamingResponse(response_generator, media_type="text/event-stream")

    except HTTPException as e:

        async def error_stream():
            yield f"Service Error: {e.detail}"

        return StreamingResponse(
            error_stream(), media_type="text/event-stream", status_code=e.status_code
        )
    except Exception as e:
        print(f"ERROR: Unhandled error in summarize_documents_stream endpoint: {e}")
        import traceback

        traceback.print_exc()

        async def critical_error_stream():
            yield "An unexpected error occurred while processing your summarization request."

        return StreamingResponse(
            critical_error_stream(), media_type="text/event-stream", status_code=500
        )
