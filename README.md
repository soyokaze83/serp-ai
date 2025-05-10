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

```
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

## Elastic Search Hosted Deployment

We have deployed our search index named `serp-ai-index` using Elastic Cloud services. To try and request data from the REST API, you can use the following cURL syntax run through a Linux distro or a Windows Subsystem for Linux (WSL):

```
export ELASTIC_PASSWORD="YOUR_PASSWORD"
export ELASTIC_URL="YOUR_URL"
curl -u elastic:$ELASTIC_PASSWORD $ELASTIC_URL
```

Note that this means you would need to set the environment variables for `ELASTIC_PASSWORD` and `ELASTIC_URL` which can be done through the setup in Elastic Cloud.
