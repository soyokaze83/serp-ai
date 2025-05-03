# SERP AI

## Contributors

- Vincent Suhardi (2206082505)
- Alwin Djuliansah (2206813504)

## Overview

**English** \
SERP AI is an open-source project designed to provide a robust and efficient platform for searching and exploring academic papers. Built with **Elasticsearch** for high-performance full-text search and integrated with **Large Language Models (LLMs)** for advanced query understanding and semantic search, this project aims to empower researchers, students, and academics with a powerful tool to discover relevant scholarly content.

**Indonesian** \
SERP AI adalah proyek open-source yang dirancang untuk menyediakan platform yang kuat dan efisien untuk mencari dan menjelajahi makalah akademik. Dibangun dengan **Elasticsearch** untuk pencarian teks lengkap berkinerja tinggi dan terintegrasi dengan **Model Bahasa Besar (LLM)** untuk pemahaman kueri tingkat lanjut dan pencarian semantik, proyek ini bertujuan untuk memberdayakan peneliti, mahasiswa, dan akademisi dengan alat yang powerful untuk menemukan konten ilmiah yang relevan.

## Elastic Search Docker Setup

It is recommended to allocate 4GB of RAM in Docker Desktop. For actually setting the RAM size when running the Docker Container, we can use the `-m` flag.

```
docker network create elastic
docker pull docker.elastic.co/elasticsearch/elasticsearch:9.0.0
docker run --name es01 --net elastic -p 9200:9200 -it -m 1GB docker.elastic.co/elasticsearch/elasticsearch:9.0.0
```
