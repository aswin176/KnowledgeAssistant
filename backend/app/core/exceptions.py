"""Domain exceptions."""


class EutridatsError(Exception):
    """Base application error."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(EutridatsError):
    def __init__(self, resource: str, identifier: str) -> None:
        super().__init__(f"{resource} '{identifier}' not found", "NOT_FOUND")


class ValidationError(EutridatsError):
    def __init__(self, message: str) -> None:
        super().__init__(message, "VALIDATION_ERROR")


class AuthenticationError(EutridatsError):
    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message, "AUTHENTICATION_ERROR")


class AuthorizationError(EutridatsError):
    def __init__(self, message: str = "Not authorized") -> None:
        super().__init__(message, "AUTHORIZATION_ERROR")


class GraphQueryError(EutridatsError):
    def __init__(self, message: str) -> None:
        super().__init__(message, "GRAPH_QUERY_ERROR")


class ImportError(EutridatsError):
    def __init__(self, message: str) -> None:
        super().__init__(message, "IMPORT_ERROR")


class UnsafeCypherError(EutridatsError):
    def __init__(self, message: str = "Query contains unsafe operations") -> None:
        super().__init__(message, "UNSAFE_CYPHER")
