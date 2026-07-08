"""API route handlers."""

import json
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect

from app import __version__
from app.core.exceptions import EutridatsError, NotFoundError
from app.dependencies import Container, get_container, get_current_user
from app.schemas.api import (
    ChatRequest,
    ChatResponse,
    CompanyCreate,
    CompanyResponse,
    GraphExploreRequest,
    GraphResponse,
    HealthResponse,
    ImportResponse,
    LoginRequest,
    NoteCreate,
    NoteResponse,
    PersonCreate,
    PersonResponse,
    SearchRequest,
    SearchResponse,
    SettingsResponse,
    TokenResponse,
)

router = APIRouter()


def _handle_error(exc: EutridatsError) -> HTTPException:
    status_map = {
        "NOT_FOUND": 404,
        "VALIDATION_ERROR": 422,
        "AUTHENTICATION_ERROR": 401,
        "AUTHORIZATION_ERROR": 403,
        "UNSAFE_CYPHER": 400,
        "IMPORT_ERROR": 400,
    }
    return HTTPException(status_code=status_map.get(exc.code, 500), detail=exc.message)


# Auth
@router.post("/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest, container: Container = Depends(get_container)):
    try:
        user = container.auth.authenticate(request.username, request.password)
        token = container.auth.create_access_token(user)
        return TokenResponse(
            access_token=token,
            expires_in=container.settings.jwt_expire_minutes * 60,
        )
    except EutridatsError as exc:
        raise _handle_error(exc) from exc


# Health
@router.get("/health", response_model=HealthResponse)
async def health(container: Container = Depends(get_container)):
    neo4j_ok = await container.graph_repo.health_check()
    llm_ok = await container.llm.health_check()
    return HealthResponse(
        status="healthy" if neo4j_ok else "degraded",
        neo4j=neo4j_ok,
        llm=llm_ok,
        version=__version__,
    )


# Chat
@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    container: Container = Depends(get_container),
    _user: dict = Depends(get_current_user),
):
    cid = container.memory.get_or_create(request.conversation_id)
    history = [{"role": m.role, "content": m.content} for m in request.history]
    if not history:
        history = container.memory.get_history(cid)

    container.memory.add_message(cid, "user", request.message)
    result = await container.agent.ask(request.message, history)
    container.memory.add_message(cid, "assistant", result["answer"])

    return ChatResponse(
        answer=result["answer"],
        sources=result.get("sources", []),
        conversation_id=cid,
        cypher=result.get("cypher"),
        result_count=result.get("result_count", 0),
    )


@router.websocket("/chat/ws")
async def chat_ws(websocket: WebSocket, container: Container = Depends(get_container)):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")
            cid = container.memory.get_or_create(data.get("conversation_id"))
            history = container.memory.get_history(cid)
            container.memory.add_message(cid, "user", message)

            full_answer = ""
            meta = {}
            async for chunk in container.agent.stream_answer(message, history):
                if isinstance(chunk, dict) and "__meta__" in chunk:
                    meta = chunk["__meta__"]
                    continue
                full_answer += chunk
                await websocket.send_json({"type": "token", "content": chunk})

            container.memory.add_message(cid, "assistant", full_answer)
            await websocket.send_json({
                "type": "done",
                "conversation_id": cid,
                "sources": meta.get("sources", []),
                "result_count": meta.get("result_count", 0),
            })
    except WebSocketDisconnect:
        pass


# Person
@router.post("/person", response_model=PersonResponse)
async def create_person(
    person: PersonCreate,
    container: Container = Depends(get_container),
    _user: dict = Depends(get_current_user),
):
    node = await container.person_service.create(person.model_dump())
    return PersonResponse(id=node["id"], name=node["name"], **{k: node.get(k) for k in PersonResponse.model_fields if k not in ("id", "name")})


@router.get("/person/{person_id}", response_model=PersonResponse)
async def get_person(
    person_id: str,
    container: Container = Depends(get_container),
    _user: dict = Depends(get_current_user),
):
    try:
        profile = await container.person_service.get(person_id)
        person = profile["person"]
        return PersonResponse(
            id=person["id"],
            name=person.get("name", ""),
            email=person.get("email"),
            phone=person.get("phone"),
            title=person.get("title"),
            bio=person.get("bio"),
            linkedin_url=person.get("linkedin_url"),
            marital_status=person.get("marital_status"),
            has_children=person.get("has_children"),
            tags=person.get("tags", []),
            created_at=person.get("created_at"),
            updated_at=person.get("updated_at"),
            relationships=profile.get("relationships", []),
        )
    except NotFoundError as exc:
        raise _handle_error(exc) from exc


@router.get("/person")
async def list_persons(
    limit: int = 50,
    offset: int = 0,
    container: Container = Depends(get_container),
    _user: dict = Depends(get_current_user),
):
    nodes = await container.person_service.list_all(limit, offset)
    return {"items": nodes, "total": len(nodes)}


# Company
@router.post("/company", response_model=CompanyResponse)
async def create_company(
    company: CompanyCreate,
    container: Container = Depends(get_container),
    _user: dict = Depends(get_current_user),
):
    node = await container.company_service.create(company.model_dump())
    return CompanyResponse(id=node["id"], name=node["name"], **{k: node.get(k) for k in CompanyResponse.model_fields if k not in ("id", "name")})


@router.get("/company/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: str,
    container: Container = Depends(get_container),
    _user: dict = Depends(get_current_user),
):
    try:
        node = await container.company_service.get(company_id)
        return CompanyResponse(id=node["id"], name=node["name"], **{k: node.get(k) for k in CompanyResponse.model_fields if k not in ("id", "name")})
    except NotFoundError as exc:
        raise _handle_error(exc) from exc


@router.get("/company")
async def list_companies(
    limit: int = 50,
    offset: int = 0,
    container: Container = Depends(get_container),
    _user: dict = Depends(get_current_user),
):
    nodes = await container.company_service.list_all(limit, offset)
    return {"items": nodes, "total": len(nodes)}


# Graph
@router.post("/graph/explore", response_model=GraphResponse)
async def explore_graph(
    request: GraphExploreRequest,
    container: Container = Depends(get_container),
    _user: dict = Depends(get_current_user),
):
    try:
        subgraph = await container.graph_repo.get_subgraph(request.node_id, request.depth)
        return GraphResponse(**subgraph)
    except NotFoundError as exc:
        raise _handle_error(exc) from exc


# Search
@router.post("/search", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    container: Container = Depends(get_container),
    _user: dict = Depends(get_current_user),
):
    result = await container.search_service.search(request.query, request.mode, request.limit)
    return SearchResponse(**result)


# Import / Upload
@router.post("/import", response_model=ImportResponse)
@router.post("/upload", response_model=ImportResponse)
async def import_file(
    file: UploadFile = File(...),
    merge: bool = True,
    container: Container = Depends(get_container),
    _user: dict = Depends(get_current_user),
):
    settings = container.settings
    settings.upload_dir.mkdir(parents=True, exist_ok=True)

    if file.filename and file.size and file.size > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="File too large")

    file_id = str(uuid4())
    ext = file.filename.rsplit(".", 1)[-1] if file.filename and "." in file.filename else "bin"
    file_path = settings.upload_dir / f"{file_id}.{ext}"

    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="File too large")

    file_path.write_bytes(content)

    try:
        record = await container.import_service.import_file(str(file_path), merge=merge)
        return ImportResponse(
            id=record.id,
            filename=record.filename,
            status=record.status,
            records_processed=record.records_processed,
            records_created=record.records_created,
            records_merged=record.records_merged,
            errors=record.errors,
            created_at=record.created_at,
        )
    except EutridatsError as exc:
        raise _handle_error(exc) from exc


@router.get("/import")
async def list_imports(
    container: Container = Depends(get_container),
    _user: dict = Depends(get_current_user),
):
    records = await container.import_service.list_imports()
    return {"items": [r.model_dump() for r in records]}


# Notes
@router.post("/notes", response_model=NoteResponse)
async def create_note(
    note: NoteCreate,
    container: Container = Depends(get_container),
    _user: dict = Depends(get_current_user),
):
    node = await container.note_service.create(note.model_dump())
    return NoteResponse(
        id=node["id"],
        title=node["title"],
        content=node["content"],
        content_type=node.get("content_type", "markdown"),
        person_id=note.person_id,
        created_at=node.get("created_at"),
    )


@router.get("/notes/person/{person_id}")
async def get_person_notes(
    person_id: str,
    container: Container = Depends(get_container),
    _user: dict = Depends(get_current_user),
):
    notes = await container.note_service.get_by_person(person_id)
    return {"items": notes}


# Jobs
@router.get("/jobs")
async def list_jobs(
    container: Container = Depends(get_container),
    _user: dict = Depends(get_current_user),
):
    from app.scheduler.jobs import get_registered_jobs

    return {"items": get_registered_jobs()}


# Settings
@router.get("/settings", response_model=SettingsResponse)
async def get_settings_endpoint(
    container: Container = Depends(get_container),
    _user: dict = Depends(get_current_user),
):
    return SettingsResponse(
        llm_model=container.settings.gemini_model,
        neo4j_connected=await container.graph_repo.health_check(),
        llm_available=await container.llm.health_check(),
        supported_import_formats=container.import_service.supported_extensions,
    )
