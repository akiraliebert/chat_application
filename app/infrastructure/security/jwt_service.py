from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import jwt, JWTError

from app.application.security.jwt_service import JWTService
from app.config.settings import settings


class JWTErrorInvalidToken(Exception):
    pass


class JoseJWTService(JWTService):
    _ALGORITHM = "HS256"
    _ACCESS_TOKEN_TTL_MIN = 15
    _REFRESH_TOKEN_TTL_DAYS = 7

    def create_access_token(self, user_id: UUID) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "type": "access",
            "iat": now,
            "exp": now + timedelta(minutes=self._ACCESS_TOKEN_TTL_MIN),
        }
        return jwt.encode(
            payload,
            settings.jwt_secret_access,
            algorithm=self._ALGORITHM,
        )

    def create_refresh_token(self, user_id: UUID) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "iat": now,
            "exp": now + timedelta(days=self._REFRESH_TOKEN_TTL_DAYS),
        }
        return jwt.encode(
            payload,
            settings.jwt_secret_refresh,
            algorithm=self._ALGORITHM,
        )

    def verify_access_token(self, token: str) -> UUID:
        return self._verify(token, expected_type="access")

    def verify_refresh_token(self, token: str) -> UUID:
        return self._verify(token, expected_type="refresh")

    def _verify(self, token: str, expected_type: str) -> UUID:
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_access
                if expected_type == "access"
                else settings.jwt_secret_refresh,
                algorithms=[self._ALGORITHM],
            )
        except JWTError:
            raise JWTErrorInvalidToken()

        if payload.get("type") != expected_type:
            raise JWTErrorInvalidToken()

        return UUID(payload["sub"])
