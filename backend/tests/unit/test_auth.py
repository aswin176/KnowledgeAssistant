"""Unit tests for auth service."""

import pytest

from app.config import Settings
from app.core.exceptions import AuthenticationError
from app.infrastructure.auth.jwt import AuthService


@pytest.fixture
def auth_service():
    settings = Settings(
        admin_username="testuser",
        admin_password="testpass",
        jwt_secret_key="test-secret-key",
    )
    return AuthService(settings)


class TestAuthService:
    def test_authenticate_success(self, auth_service):
        user = auth_service.authenticate("testuser", "testpass")
        assert user["username"] == "testuser"
        assert user["role"] == "admin"

    def test_authenticate_failure(self, auth_service):
        with pytest.raises(AuthenticationError):
            auth_service.authenticate("wrong", "credentials")

    def test_create_and_decode_token(self, auth_service):
        user = {"sub": "testuser", "username": "testuser", "role": "admin"}
        token = auth_service.create_access_token(user)
        assert isinstance(token, str)
        payload = auth_service.decode_token(token)
        assert payload["username"] == "testuser"

    def test_decode_invalid_token(self, auth_service):
        with pytest.raises(AuthenticationError):
            auth_service.decode_token("invalid.token.here")

    def test_hash_and_verify_password(self, auth_service):
        hashed = auth_service.hash_password("mypassword")
        assert auth_service.verify_password("mypassword", hashed)
        assert not auth_service.verify_password("wrong", hashed)
