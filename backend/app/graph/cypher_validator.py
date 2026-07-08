"""Cypher query safety validation."""

import re

# Destructive or write operations blocked in agent-generated queries
FORBIDDEN_PATTERNS = [
    r"\bCREATE\b",
    r"\bMERGE\b",
    r"\bDELETE\b",
    r"\bDETACH\b",
    r"\bSET\b",
    r"\bREMOVE\b",
    r"\bDROP\b",
    r"\bLOAD\s+CSV\b",
    r"\bCALL\s+db\.schema\b",
    r"\bapoc\.",
    r"\bgds\.",
]

FORBIDDEN_REGEX = re.compile("|".join(FORBIDDEN_PATTERNS), re.IGNORECASE)


def validate_read_only_cypher(cypher: str) -> tuple[bool, str | None]:
    """Ensure Cypher query is read-only."""
    stripped = cypher.strip()
    if not stripped:
        return False, "Empty query"

    if FORBIDDEN_REGEX.search(stripped):
        return False, "Query contains forbidden write/destructive operations"

    # Must start with allowed read operations
    allowed_starts = ("MATCH", "WITH", "OPTIONAL", "CALL", "RETURN", "UNWIND")
    first_token = stripped.split()[0].upper() if stripped.split() else ""
    if first_token not in allowed_starts:
        return False, f"Query must start with a read operation, got: {first_token}"

    return True, None


def sanitize_cypher_params(params: dict) -> dict:
    """Sanitize query parameters."""
    sanitized = {}
    for key, value in params.items():
        if isinstance(value, str) and len(value) > 10000:
            sanitized[key] = value[:10000]
        else:
            sanitized[key] = value
    return sanitized
