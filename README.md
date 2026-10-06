# Academic Discovery India (ADI)

**Graph-Based Faculty Collaboration Recommendation Framework (GRAFT-FCR)**

ADI is a full-stack platform for discovering faculty members across premier Indian engineering institutions and getting explainable research collaboration recommendations. It combines semantic search, scholarly data enrichment, knowledge graph analysis and a multi-factor recommendation engine.

Developed as a training project at Defence Electronics Applications Laboratory (DEAL), DRDO, Dehradun.

## Features

* Semantic faculty search using Sentence Transformer embeddings and FAISS
* Faculty profiles enriched with publication data from OpenAlex
* Collaboration recommendations (Top-8) using the GRAFT-FCR framework
* Explainable scores: semantic similarity, graph score, temporal relevance, complementarity, novelty
* Knowledge graph visualization of academic relationships
* Institute and department explorer
* Coverage and analytics dashboards
* REST APIs with Swagger documentation

## GRAFT-FCR Overview

Candidates are first retrieved using FAISS semantic search, then re-ranked using a weighted combination of:

* Semantic similarity
* Graph relationship score (co-authorship, interests, department, institute)
* Rare connection score
* Temporal relevance
* Research complementarity
* Novelty bonus and degree penalty (to reduce popularity bias)

## Tech Stack

* **Frontend:** React, Tailwind CSS
* **Backend:** Python, FastAPI
* **Database:** PostgreSQL
* **ML / Search:** Sentence Transformers, FAISS
* **Graph:** NetworkX
* **Data Source:** OpenAlex API

## Project Structure

* `frontend/` : React user interface
* `backend/` : FastAPI backend, recommendation engine and APIs
* `database/` : PostgreSQL database dump

## Run Locally

### 1. Database

Create a PostgreSQL database and restore the dump from the `database/` folder.

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

API docs will be available at `http://localhost:8000/docs`.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

## Main API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/search` | Semantic faculty search |
| GET | `/faculty/{id}` | Faculty profile |
| GET | `/faculty/{id}/recommendations` | Collaboration recommendations |
| GET | `/institutes` | Institute information |
| GET | `/departments` | Department information |
| GET | `/analytics/summary` | Analytics data |

## Future Improvements

* More scholarly sources (Scopus, Semantic Scholar, ORCID)
* Graph Neural Network based recommendation
* Real-time data synchronization
* Coverage beyond engineering institutions

## Author

Srishti Singh
B.Tech Information Technology, Banasthali Vidyapith
Mentor: Mr. Nikhil Mittal, DEAL, DRDO
