from fastapi import Request, HTTPException
from elasticsearch import Elasticsearch
from sentence_transformers import CrossEncoder
from together import Together
from typing import List, Dict, AsyncGenerator


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


def get_together_client(request: Request) -> Together:
    if not hasattr(request.app.state, "together_client"):
        raise HTTPException(
            status_code=503,
            detail="TogetherAI client not available.",
        )
    return request.app.state.together_client


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
    valid_hits_for_reranking = []

    for hit in search_results:
        doc_text = hit["_source"].get("text")
        if isinstance(doc_text, str) and doc_text.strip():
            sentence_pairs.append([query, doc_text])
            valid_hits_for_reranking.append(hit)
        else:
            print(
                f"Warning: Document {hit.get('_id', 'N/A')} missing 'text' field, not a string, or empty. Skipping for reranking."
            )

    if not sentence_pairs:
        return []

    scores = model.predict(sentence_pairs)

    for i, hit in enumerate(valid_hits_for_reranking):
        hit["cross_encoder_score"] = float(scores[i])

    reranked_results = sorted(
        valid_hits_for_reranking, key=lambda x: x["cross_encoder_score"], reverse=True
    )
    return reranked_results[:k]


async def stream_rag_response(
    query: str,
    documents: List[Dict],
    together_client: Together,
    model_name: str,
    max_context_tokens: int = 3000,
) -> AsyncGenerator[str, None]:
    """
    Generates a summary from TogetherAI based on retrieved documents.
    Streams the response token by token.
    The 'query' parameter here is the original user query that fetched these documents.
    """
    if not documents:
        yield "No documents were provided to summarize."
        return

    context_parts = []
    current_token_count = 0

    for i, doc in enumerate(documents):
        doc_text = doc["_source"].get("text", "")
        if not isinstance(doc_text, str) or not doc_text.strip():
            continue

        doc_tokens = doc_text.split()
        if current_token_count + len(doc_tokens) > max_context_tokens:
            remaining_tokens = max_context_tokens - current_token_count
            if remaining_tokens > 20:
                context_parts.append(
                    f"Document {i+1} (truncated): {' '.join(doc_tokens[:remaining_tokens])}"
                )
            break
        context_parts.append(f"Document {i+1}:\n{doc_text}")
        current_token_count += len(doc_tokens)

    if not context_parts:
        yield "No valid content found in the provided documents to summarize."
        return

    context_str = "\n\n---\n\n".join(context_parts)

    messages = [
        {
            "role": "system",
            "content": "You are an expert summarization AI. Your task is to read the following documents "
            "and provide a concise, neutral, and informative summary of their combined content. "
            "Focus on the main points and key information presented in the documents. "
            "Do not add any information not present in the provided texts. "
            "The summary should be well-structured and easy to understand.",
        },
        {
            "role": "user",
            "content": f'Please summarize the following documents. The original query that led to these documents was about: "{query}".\n\nDocuments:\n{context_str}\n\nComprehensive Summary:',
        },
    ]

    try:
        response_stream = together_client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True,
            max_tokens=5000,
        )
        for chunk in response_stream:
            if hasattr(chunk, "choices") and chunk.choices:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
    except Exception as e:
        print(f"ERROR: TogetherAI API error during summarization: {e}")
        yield f"Error communicating with the AI model for summarization: {str(e)}"
