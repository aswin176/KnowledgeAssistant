"""Dependency injection container."""

from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.agent.graph_agent import KnowledgeGraphAgent
from app.config import Settings, get_settings
from app.core.exceptions import AuthenticationError
from app.etl.registry import ImportService
from app.infrastructure.auth.jwt import AuthService
from app.infrastructure.llm.ollama import OllamaLLMService
from app.infrastructure.neo4j.connection import Neo4jConnection
from app.infrastructure.neo4j.repository import Neo4jGraphRepository
from app.services.person_service import (
    CompanyService,
    ConversationMemory,
    NoteService,
    PersonService,
    SearchService,
)

security = HTTPBearer(auto_error=False)


class Container:
    """Application DI container."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.neo4j = Neo4jConnection(self.settings)
        self.graph_repo = Neo4jGraphRepository(self.neo4j)
        self.llm = OllamaLLMService(self.settings)
        self.auth = AuthService(self.settings)
        self.agent = KnowledgeGraphAgent(self.llm, self.graph_repo)
        self.import_service = ImportService(self.graph_repo)
        self.person_service = PersonService(self.graph_repo)
        self.company_service = CompanyService(self.graph_repo)
        self.search_service = SearchService(self.graph_repo)
        self.note_service = NoteService(self.graph_repo)
        self.memory = ConversationMemory()

    async def startup(self) -> None:
        await self.neo4j.connect()
        await self.graph_repo.initialize_schema()

    async def shutdown(self) -> None:
        await self.neo4j.close()


_container: Container | None = None


def get_container() -> Container:
    global _container
    if _container is None:
        _container = Container()
    return _container


def override_container(container: Container) -> None:
    global _container
    _container = container


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    container: Container = Depends(get_container),
) -> dict:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return container.auth.decode_token(credentials.credentials)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.message,
        ) from exc
