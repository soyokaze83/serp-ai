from fastapi import Request, HTTPException
from elasticsearch import Elasticsearch
from sentence_transformers import CrossEncoder


def get_es_client(request: Request) -> Elasticsearch:
    if not hasattr(request.app.state, "es_client"):
        raise HTTPException(
            status_code=503,
            detail="Elasticsearch client not available.",
        )
    return request.app.state.es_client


def get_cross_encoder_model(request: Request) -> CrossEncoder:
    if not hasattr(request.app.state, "cross_encoder_model"):
        raise HTTPException(
            status_code=503,
            detail="Cross-encoder model not available.",
        )
    return request.app.state.cross_encoder_model


def perform_elasticsearch_search(
    query: str, es_client: Elasticsearch, index_name: str = "serp-ai", size: int = 100
) -> list:
    try:
        response = es_client.search(
            index=index_name,
            size=size,
            query={
                "multi_match": {
                    "query": query,
                    "fields": "text",
                    "type": "most_fields",
                }
            },
        )
        return response["hits"]["hits"]
    except Exception as e:
        print(f"ERROR: Elasticsearch error during service search: {e}")
        raise HTTPException(status_code=500, detail=f"Search service error: {str(e)}")


def rerank_with_cross_encoder(
    query: str, search_results: list, model: CrossEncoder, k: int = 5
) -> list:
    if not search_results:
        return []

    sentence_pairs = []
    for hit in search_results:
        doc_text = hit["_source"].get("text")
        sentence_pairs.append([query, doc_text])

    if not sentence_pairs:
        return search_results

    scores = model.predict(sentence_pairs)

    for i, hit in enumerate(search_results):
        hit["cross_encoder_score"] = float(scores[i])  # Ensure score is float for JSON

    reranked_results = sorted(
        search_results, key=lambda x: x["cross_encoder_score"], reverse=True
    )
    return reranked_results[:k]
