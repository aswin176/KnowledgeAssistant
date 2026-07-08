"""Repository and service interfaces (ports)."""

from abc import ABC, abstractmethod
from typing import Any

from app.core.domain.entities import (
    CompanyEntity,
    ImportRecord,
    NodeLabel,
    NoteEntity,
    PersonEntity,
    RelationshipEntity,
    RelationshipType,
)


class GraphRepository(ABC):
    """Port for graph database operations."""

    @abstractmethod
    async def initialize_schema(self) -> None:
        ...

    @abstractmethod
    async def create_node(
        self,
        label: NodeLabel,
        properties: dict[str, Any],
        merge_keys: list[str] | None = None,
    ) -> dict[str, Any]:
        ...

    @abstractmethod
    async def get_node_by_id(self, node_id: str) -> dict[str, Any] | None:
        ...

    @abstractmethod
    async def find_nodes(
        self,
        label: NodeLabel | None,
        filters: dict[str, Any] | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def create_relationship(
        self,
        from_id: str,
        to_id: str,
        rel_type: RelationshipType,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        ...

    @abstractmethod
    async def execute_read_query(self, cypher: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def full_text_search(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def get_person_profile(self, person_id: str) -> dict[str, Any] | None:
        ...

    @abstractmethod
    async def get_subgraph(self, node_id: str, depth: int = 2) -> dict[str, Any]:
        ...

    @abstractmethod
    async def merge_duplicate_nodes(
        self,
        primary_id: str,
        duplicate_id: str,
    ) -> dict[str, Any]:
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        ...


class PersonRepository(ABC):
    @abstractmethod
    async def create(self, person: PersonEntity) -> PersonEntity:
        ...

    @abstractmethod
    async def get_by_id(self, person_id: str) -> PersonEntity | None:
        ...

    @abstractmethod
    async def update(self, person_id: str, data: dict[str, Any]) -> PersonEntity:
        ...

    @abstractmethod
    async def search(self, query: str, limit: int = 20) -> list[PersonEntity]:
        ...


class CompanyRepository(ABC):
    @abstractmethod
    async def create(self, company: CompanyEntity) -> CompanyEntity:
        ...

    @abstractmethod
    async def get_by_id(self, company_id: str) -> CompanyEntity | None:
        ...

    @abstractmethod
    async def search(self, query: str, limit: int = 20) -> list[CompanyEntity]:
        ...


class NoteRepository(ABC):
    @abstractmethod
    async def create(self, note: NoteEntity) -> NoteEntity:
        ...

    @abstractmethod
    async def get_by_person(self, person_id: str) -> list[NoteEntity]:
        ...


class ImportRepository(ABC):
    @abstractmethod
    async def save_record(self, record: ImportRecord) -> ImportRecord:
        ...

    @abstractmethod
    async def get_record(self, record_id: str) -> ImportRecord | None:
        ...

    @abstractmethod
    async def list_records(self, limit: int = 50) -> list[ImportRecord]:
        ...


class LLMService(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system: str | None = None) -> str:
        ...

    @abstractmethod
    async def stream(self, prompt: str, system: str | None = None):
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        ...


class ConnectorInterface(ABC):
    """Generic connector port for external data sources."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    async def fetch(self, **kwargs: Any) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def validate_config(self, config: dict[str, Any]) -> bool:
        ...
