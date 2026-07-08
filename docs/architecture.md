# Architecture

## Overview

Eutridats follows **Clean Architecture** with clear separation between domain logic, application services, infrastructure, and presentation layers.

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation                          │
│  Next.js Frontend  │  Telegram Bot  │  REST/WS API     │
├─────────────────────────────────────────────────────────┤
│                    Application                           │
│  PersonService │ SearchService │ ImportService │ Agent  │
├─────────────────────────────────────────────────────────┤
│                    Domain                                │
│  Entities │ Interfaces (Ports) │ Exceptions             │
├─────────────────────────────────────────────────────────┤
│                    Infrastructure                        │
│  Neo4j Repo │ Ollama LLM │ JWT Auth │ ETL Pipelines    │
└─────────────────────────────────────────────────────────┘
```

## Core Modules

### Backend (`backend/app/`)

| Module | Responsibility |
|--------|---------------|
| `core/domain/` | Entity definitions, value objects |
| `core/interfaces/` | Repository and service ports (ABC) |
| `infrastructure/neo4j/` | Graph database adapter |
| `infrastructure/llm/` | Ollama LLM adapter |
| `infrastructure/auth/` | JWT authentication |
| `agent/` | LangGraph workflow for Q&A |
| `etl/` | File import pipelines |
| `graph/` | Cypher safety validation |
| `connectors/` | External data source adapters |
| `scheduler/` | Background job definitions |
| `services/` | Business logic orchestration |
| `api/` | FastAPI route handlers |

### Agent Workflow (LangGraph)

```
User Question
     │
     ▼
┌──────────┐     ┌────────────────┐     ┌───────────────┐     ┌───────────┐
│ Classify │────▶│ Generate Cypher│────▶│ Execute Query │────▶│ Summarize │
└──────────┘     └────────────────┘     └───────────────┘     └───────────┘
     │                                                                    │
     ▼                                                                    ▼
┌──────────────┐                                                   Answer + Sources
│ Direct Answer│
└──────────────┘
```

### Dependency Injection

The `Container` class in `dependencies.py` wires all services:

```python
container = Container(settings)
container.graph_repo    # Neo4jGraphRepository
container.llm           # OllamaLLMService
container.agent         # KnowledgeGraphAgent
container.import_service # ImportService
```

## Data Flow

### Import Pipeline

```
File Upload → Extract → Transform → Duplicate Detection → Load/Merge → Neo4j
```

### Chat Query

```
Question → Agent Classify → Cypher Generation → Safety Check → Neo4j Read → LLM Summarize → Response
```

## Security

- JWT authentication on all protected endpoints
- Read-only Cypher validation (blocks CREATE, DELETE, SET, MERGE)
- Rate limiting via slowapi
- Input validation via Pydantic schemas
- Environment-based secrets management

## Extensibility

- **Connectors**: Implement `ConnectorInterface` for new data sources
- **ETL**: Extend `BaseETLPipeline` for new file formats
- **Node Types**: Add to `NodeLabel` enum and schema constraints
- **Agent**: Extend LangGraph workflow with new nodes
