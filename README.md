# SERP AI

## Contributors

- Vincent Suhardi (2206082505)
- Alwin Djuliansah (2206813504)
- Austin Susanto (2206025060)

## Overview

**English** \
SERP AI is an open-source project designed to provide a robust and efficient platform for searching and exploring academic papers. Built with **Elasticsearch** for high-performance full-text search and integrated with **Large Language Models (LLMs)** for advanced query understanding and semantic search, this project aims to empower researchers, students, and academics with a powerful tool to discover relevant scholarly content.

**Indonesian** \
SERP AI adalah proyek open-source yang dirancang untuk menyediakan platform yang kuat dan efisien untuk mencari dan menjelajahi makalah akademik. Dibangun dengan **Elasticsearch** untuk pencarian teks lengkap berkinerja tinggi dan terintegrasi dengan **Model Bahasa Besar (LLM)** untuk pemahaman kueri tingkat lanjut dan pencarian semantik, proyek ini bertujuan untuk memberdayakan peneliti, mahasiswa, dan akademisi dengan alat yang powerful untuk menemukan konten ilmiah yang relevan.

## Initial Setup

We use FastAPI and NextJS as frameworks for both backend and frontend respectively, where due to this being a small scale application and to optimize search speed, we'll be applying a monolithic structure to our system. Here are the following commands to first setup and then run each stack:

```bash
# FastAPI Python Setup (with default python)
cd backend/
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt

# FastAPI Python Setup (with uv)
cd backend/
uv venv
.venv/Scripts/activate
uv sync

# NextJS Setup
cd frontend/
npm install .
```

## Elastic Search Local Development (For Developers)

We setup the Elastic Search index (without Kibana) for local development through the docker tutorial provided in this specific [section](https://www.elastic.co/docs/deploy-manage/deploy/self-managed/install-elasticsearch-docker-basic#_start_a_single_node_cluster) of the Elastic Search documentation. Here's how we set it up based on the documentation:

```bash
# Setup Docker Container
docker network create elastic
docker pull docker.elastic.co/elasticsearch/elasticsearch:9.0.0
docker run --name es01 --net elastic -p 9200:9200 -it -m 1GB docker.elastic.co/elasticsearch/elasticsearch:9.0.0

# Test cURL Command
export ELASTIC_PASSWORD="your_password"
docker cp es01:/usr/share/elasticsearch/config/certs/http_ca.crt .
curl --cacert http_ca.crt -u elastic:$ELASTIC_PASSWORD https://localhost:9200
```

## Elastic Search Hosted Deployment (For Developers)

We have deployed our productoin Elastic Search index on [Bonsai](https://bonsai.io/). To try and request data from the API, you can simply cURL the URL therefore you need to provide the deployed production URL for the index.

```
export ELASTIC_URL="ES_PROJECT_URL"
curl $ELASTIC_URL
```

Note that this means you would need to set the environment variables for `ELASTIC_URL`.
