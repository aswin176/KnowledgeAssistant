"""JWT authentication service."""

from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import Settings
from app.core.exceptions import AuthenticationError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def verify_password(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def authenticate(self, username: str, password: str) -> dict[str, Any]:
        if (
            username == self._settings.admin_username
            and password == self._settings.admin_password
        ):
            return {"sub": username, "username": username, "role": "admin"}
        raise AuthenticationError("Invalid username or password")

    def create_access_token(self, data: dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self._settings.jwt_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(
            to_encode,
            self._settings.jwt_secret_key,
            algorithm=self._settings.jwt_algorithm,
        )

    def decode_token(self, token: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(
                token,
                self._settings.jwt_secret_key,
                algorithms=[self._settings.jwt_algorithm],
            )
            return payload
        except JWTError as exc:
            raise AuthenticationError("Invalid or expired token") from exc
