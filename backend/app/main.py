"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app import __version__
from app.api.routes import router
from app.config import get_settings
from app.core.exceptions import EutridatsError
from app.core.logging import setup_logging
from app.dependencies import get_container

settings = get_settings()
setup_logging(settings)

limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit])


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = get_container()
    await container.startup()
    yield
    await container.shutdown()


app = FastAPI(
    title=settings.app_name,
    description="Personal Knowledge Graph AI Assistant",
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix=settings.api_prefix)


@app.exception_handler(EutridatsError)
async def eutridats_error_handler(_request: Request, exc: EutridatsError):
    status_map = {
        "NOT_FOUND": 404,
        "VALIDATION_ERROR": 422,
        "AUTHENTICATION_ERROR": 401,
        "AUTHORIZATION_ERROR": 403,
    }
    return JSONResponse(
        status_code=status_map.get(exc.code, 500),
        content={"error": exc.code, "message": exc.message},
    )


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": __version__,
        "docs": "/docs",
        "api": settings.api_prefix,
    }
