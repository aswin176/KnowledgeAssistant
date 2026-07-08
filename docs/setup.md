# Setup Guide

## System Requirements

- **OS**: macOS, Linux, or Windows with WSL2
- **RAM**: 8 GB minimum (16 GB recommended for Ollama)
- **Disk**: 10 GB free space
- **Docker**: 24.0+ with Compose V2

## Step 1: Clone and Configure

```bash
git clone <repo-url> Eutridats
cd Eutridats
cp backend/.env.example backend/.env
```

Edit `backend/.env` to set secure passwords:

```env
SECRET_KEY=<generate-with-openssl-rand-hex-32>
JWT_SECRET_KEY=<generate-with-openssl-rand-hex-32>
NEO4J_PASSWORD=your-secure-password
ADMIN_PASSWORD=your-admin-password
```

## Step 2: Start Services

```bash
docker compose up -d
```

Wait for all services to be healthy:

```bash
docker compose ps
```

## Step 3: Pull LLM Model

```bash
docker exec eutridats-ollama ollama pull qwen3
```

Alternative models: `llama3.2`, `mistral`, `qwen2.5`. Update `OLLAMA_MODEL` in `.env`.

## Step 4: Initialize Data

```bash
docker exec eutridats-backend python scripts/seed_data.py
```

## Step 5: Access the Application

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | admin / admin123 |
| API Docs | http://localhost:8000/docs | Bearer token |
| Neo4j Browser | http://localhost:7474 | neo4j / eutridats_password |

## Local Development (Without Docker)

### Neo4j

Install Neo4j Desktop or run via Docker:

```bash
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/eutridats_password \
  neo4j:5.26-community
```

### Ollama

```bash
# macOS
brew install ollama
ollama serve &
ollama pull qwen3
```

### Backend

```bash
cd backend
poetry install
cp .env.example .env
poetry run uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Running Tests

```bash
cd backend
poetry run pytest tests/ -v
poetry run pytest tests/ --cov=app --cov-report=term-missing
```

## Importing Your Data

1. Prepare a CSV with columns: `name`, `email`, `company`, `city`, `skills`, `title`
2. Go to Import Data page or use the API:

```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@contacts.csv"
```

Supported formats: `.csv`, `.xlsx`, `.json`, `.md`, `.pdf`, `.docx`

## Telegram Bot Setup

1. Create a bot via [@BotFather](https://t.me/BotFather)
2. Configure:

```bash
cp telegram/.env.example telegram/.env
# Set TELEGRAM_BOT_TOKEN
```

3. Run:

```bash
docker compose -f docker-compose.prod.yml --profile telegram up -d telegram
```
