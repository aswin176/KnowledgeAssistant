"""Pydantic API schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# Auth
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# Chat
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    history: list[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict[str, Any]] = Field(default_factory=list)
    conversation_id: str
    cypher: str | None = None
    result_count: int = 0


class SourceEntity(BaseModel):
    id: str | None = None
    name: str | None = None
    type: str = "Unknown"


# Person
class PersonCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    roll_number: str | None = None
    father_name: str | None = None
    dob: str | None = None
    address: str | None = None
    hometown: str | None = None
    mobile: str | None = None
    email: str | None = None
    class_name: str | None = Field(default=None, alias="class")
    current_employment: str | None = None
    relationship_status: str | None = None
    marriage_date: str | None = None
    kids: int | None = None
    spouse_roll_number: str | None = None
    spouse_name: str | None = None
    linkedin_url: str | None = None
    current_city: str | None = None
    source: str = "manual"


class PersonUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str | None = None
    roll_number: str | None = None
    father_name: str | None = None
    dob: str | None = None
    address: str | None = None
    hometown: str | None = None
    mobile: str | None = None
    email: str | None = None
    class_name: str | None = Field(default=None, alias="class")
    current_employment: str | None = None
    relationship_status: str | None = None
    marriage_date: str | None = None
    kids: int | None = None
    spouse_roll_number: str | None = None
    spouse_name: str | None = None
    linkedin_url: str | None = None
    current_city: str | None = None


class PersonResponse(BaseModel):
    id: str
    name: str
    roll_number: str | None = None
    father_name: str | None = None
    dob: str | None = None
    address: str | None = None
    hometown: str | None = None
    mobile: str | None = None
    email: str | None = None
    class_name: str | None = Field(default=None, alias="class")
    current_employment: str | None = None
    relationship_status: str | None = None
    marriage_date: str | None = None
    kids: int | None = None
    spouse_roll_number: str | None = None
    spouse_name: str | None = None
    linkedin_url: str | None = None
    current_city: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    relationships: list[dict[str, Any]] = Field(default_factory=list)


# Company
class CompanyCreate(BaseModel):
    name: str
    industry: str | None = None
    website: str | None = None
    description: str | None = None
    founded_year: int | None = None
    size: str | None = None
    source: str = "manual"


class CompanyResponse(BaseModel):
    id: str
    name: str
    industry: str | None = None
    website: str | None = None
    description: str | None = None
    founded_year: int | None = None
    size: str | None = None


# Search
class SearchRequest(BaseModel):
    query: str
    mode: str = "hybrid"  # graph, fulltext, hybrid
    limit: int = 20


class SearchResult(BaseModel):
    id: str | None = None
    name: str | None = None
    labels: list[str] = Field(default_factory=list)
    score: float = 0.0
    properties: dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    results: list[SearchResult]
    total: int
    mode: str


# Graph
class GraphExploreRequest(BaseModel):
    node_id: str
    depth: int = 2


class GraphResponse(BaseModel):
    nodes: list[dict[str, Any]]
    relationships: list[dict[str, Any]]
    center_id: str


# Import
class ImportResponse(BaseModel):
    id: str
    filename: str
    status: str
    records_processed: int
    records_created: int
    records_merged: int
    errors: list[str] = Field(default_factory=list)
    created_at: datetime | None = None


# Notes
class NoteCreate(BaseModel):
    title: str
    content: str
    content_type: str = "markdown"
    person_id: str | None = None


class NoteResponse(BaseModel):
    id: str
    title: str
    content: str
    content_type: str
    person_id: str | None = None
    created_at: str | None = None


# Jobs
class JobResponse(BaseModel):
    id: str
    name: str
    status: str
    last_run: datetime | None = None
    next_run: datetime | None = None
    schedule: str | None = None


# Settings
class SettingsResponse(BaseModel):
    llm_model: str
    neo4j_connected: bool
    llm_available: bool
    supported_import_formats: list[str]


# Health
class HealthResponse(BaseModel):
    status: str
    neo4j: bool
    llm: bool
    version: str
