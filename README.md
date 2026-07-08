# Eutridats

A production-quality personal knowledge graph AI assistant for managing lifelong knowledge about classmates, colleagues, friends, family, projects, and more.

## Features

- **Knowledge Graph** — Neo4j-powered graph with 25+ node types and 19 relationship types
- **Natural Language Q&A** — LangGraph agent with Ollama (Qwen 3) for questions like "Who works at Google?"
- **Multi-format Import** — CSV, Excel, JSON, Markdown, PDF, DOCX with duplicate detection and merge
- **Modern Dashboard** — Next.js frontend with chat, graph explorer, search, and entity detail pages
- **Telegram Bot** — Search, person lookup, and chat mode via Telegram
- **Clean Architecture** — Modular, testable, dependency-injected backend

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for local frontend dev)
- Python 3.12 + Poetry (for local backend dev)

### Docker (Recommended)

```bash
# Clone and start all services
cp backend/.env.example backend/.env
docker compose up -d

# Pull Ollama model
docker exec eutridats-ollama ollama pull qwen3

# Seed sample data
docker exec eutridats-backend python scripts/seed_data.py
```

Access:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474

Default login: `admin` / `admin123`

### Local Development

```bash
# Backend
cd backend
cp .env.example .env
poetry install
poetry run uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Seed data (requires Neo4j running)
cd backend && poetry run python scripts/seed_data.py
```

## Project Structure

```
Eutridats/
├── backend/           # FastAPI backend (Clean Architecture)
│   ├── app/
│   │   ├── api/       # REST & WebSocket routes
│   │   ├── agent/     # LangGraph AI agent
│   │   ├── core/      # Domain entities & interfaces
│   │   ├── etl/       # Import pipelines
│   │   ├── graph/     # Cypher validation
│   │   ├── infrastructure/  # Neo4j, LLM, Auth
│   │   ├── services/  # Business logic
│   │   ├── connectors/ # External data connectors
│   │   └── scheduler/ # Background jobs
│   └── tests/
├── frontend/          # Next.js dashboard
├── telegram/          # Telegram bot
├── docs/              # Documentation
└── docker-compose.yml
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/login` | POST | JWT authentication |
| `/api/v1/chat` | POST | Natural language Q&A |
| `/api/v1/chat/ws` | WS | Streaming chat |
| `/api/v1/search` | POST | Hybrid search |
| `/api/v1/person` | GET/POST | Person CRUD |
| `/api/v1/company` | GET/POST | Company CRUD |
| `/api/v1/graph/explore` | POST | Subgraph exploration |
| `/api/v1/upload` | POST | File import |
| `/api/v1/jobs` | GET | Background jobs |
| `/api/v1/health` | GET | Health check |

## Documentation

- [Architecture](docs/architecture.md)
- [Setup Guide](docs/setup.md)
- [Deployment Guide](docs/deployment.md)
- [Schema Documentation](docs/schema.md)
- [Connector Guide](docs/connectors.md)
- [Developer Guide](docs/developer.md)
- [API Reference](docs/api-reference.md)

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, Poetry |
| Database | Neo4j Community Edition |
| AI | Ollama (Qwen 3), LangGraph |
| Frontend | Next.js, TypeScript, TailwindCSS |
| Auth | JWT |
| Bot | python-telegram-bot |

## License

MIT
