# Knowledge Assistant

This project is a person knowledge-graph assistant built around a Gemini-powered LangGraph workflow. The intended architecture is:

- Telegram or UI → Next.js frontend
- Next.js UI → FastAPI backend
- FastAPI → LangGraph agent
- LangGraph agent → Gemini 2.5 Flash API
- Gemini/agent layer → Neo4j knowledge graph

It is designed to ingest person Excel data, build a graph schema, and then answer natural-language questions about people, classes, careers, cities, spouses, and employment history.

## What changed in this version

- Replaced the old local LLM wiring with a Gemini-compatible service.
- Added a person-focused graph model for people, classes, companies, cities, addresses, family members, and spouse relationships.
- Added an Excel import path that maps your provided columns into Neo4j nodes and relationships.
- Added a backend script to load Excel files into Neo4j before starting the app.
- Kept the existing FastAPI + Next.js structure intact so the UI can continue to work with the new backend.

## Supported Excel columns

The importer is configured for the following person columns:

- Roll Number
- Name
- Class
- Father Name
- DOB
- Address
- Hometown
- Mobile
- Email
- 7th Semester Employment
- 10th Semester Employment
- Current employment
- Relationship Status
- Marraige Date
- Kids
- Spouse Roll Number (if present in same data)
- Spouse name
- Linkedin URL
- Current City

The importer creates graph data using these concepts:

- Person node for each record
- Class node via BELONGS_TO_CLASS
- Company nodes for employment history via WORKED_AT / WORKS_AT
- City nodes for hometown and current city via LIVES_IN
- Address node via LIVES_AT
- Family member node via HAS_FATHER
- Spouse relationship via MARRIED_TO
- LinkedIn profile relationship via HAS_PROFILE

## Recommended setup

### 1. Configure backend settings

Copy the example environment file and update the values:

```bash
cd backend
copy .env.example .env
```

Update the following values in the backend environment:

- GEMINI_API_KEY
- NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD / NEO4J_DATABASE
- CORS_ORIGINS if needed

### 2. Load Excel data into Neo4j

Run the import script first so the graph schema and nodes exist before starting the application:

```bash
cd backend
python scripts/load_excel_to_neo4j.py path/to/persons.xlsx
```

If your workbook has multiple sheets, use:

```bash
python scripts/load_excel_to_neo4j.py path/to/persons.xlsx --sheet 0
```

### 3. Start the backend

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

## Access points

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474

Default login: admin / admin123

## Project structure

```text
KnowledgeAssistant/
├── backend/            # FastAPI backend with Gemini + LangGraph + Neo4j
│   ├── app/
│   │   ├── agent/      # LangGraph agent
│   │   ├── api/        # API routes
│   │   ├── etl/        # Excel/CSV import pipelines
│   │   ├── infrastructure/  # Neo4j, Gemini, auth
│   │   └── services/   # Business logic
│   └── scripts/        # Data-loading scripts
├── frontend/           # Next.js UI
├── telegram/           # Telegram bot entry point
└── docs/               # Project docs
```

## Technology stack

- Backend: Python 3.12, FastAPI, LangGraph
- Database: Neo4j
- AI: Gemini 2.5 Flash API
- Frontend: Next.js, TypeScript, Tailwind CSS
- Auth: JWT
