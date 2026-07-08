"""Background job scheduler."""

from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from app.core.logging import get_logger

logger = get_logger(__name__)

_jobs: list[dict[str, Any]] = [
    {
        "id": str(uuid4()),
        "name": "weekly_profile_refresh",
        "status": "idle",
        "schedule": "0 0 * * 0",
        "description": "Weekly incremental profile updates",
        "last_run": None,
        "next_run": datetime.utcnow() + timedelta(days=7),
    },
    {
        "id": str(uuid4()),
        "name": "monthly_deduplication",
        "status": "idle",
        "schedule": "0 0 1 * *",
        "description": "Monthly duplicate detection and merge suggestions",
        "last_run": None,
        "next_run": datetime.utcnow() + timedelta(days=30),
    },
    {
        "id": str(uuid4()),
        "name": "daily_health_check",
        "status": "idle",
        "schedule": "0 6 * * *",
        "description": "Daily system health verification",
        "last_run": None,
        "next_run": datetime.utcnow() + timedelta(days=1),
    },
]


def get_registered_jobs() -> list[dict[str, Any]]:
    return _jobs


async def run_job(job_name: str) -> dict[str, Any]:
    for job in _jobs:
        if job["name"] == job_name:
            job["status"] = "running"
            job["last_run"] = datetime.utcnow()
            logger.info("job_started", job=job_name)
            try:
                # Placeholder for actual job logic - extensible via connectors
                job["status"] = "completed"
                logger.info("job_completed", job=job_name)
            except Exception as exc:
                job["status"] = "failed"
                logger.error("job_failed", job=job_name, error=str(exc))
                raise
            return job
    raise ValueError(f"Job not found: {job_name}")
