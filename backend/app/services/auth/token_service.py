from __future__ import annotations

from dataclasses import dataclass

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    expires_in: int


class TokenService:
    def __init__(
        self,
        *,
        secret_key: str,
        algorithm: str,
        access_token_expire_minutes: int,
        refresh_token_expire_days: int,
    ) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    def create_tokens(
        self,
        *,
        user_id: str,
        role: str,
    ) -> TokenPair:
        access_token = create_access_token(
            subject=user_id,
            secret_key=self.secret_key,
            algorithm=self.algorithm,
            expires_minutes=self.access_token_expire_minutes,
            role=role,
        )

        refresh_token = create_refresh_token(
            subject=user_id,
            secret_key=self.secret_key,
            algorithm=self.algorithm,
            expires_days=self.refresh_token_expire_days,
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.access_token_expire_minutes * 60,
        )

    def decode(self, token: str) -> dict:
        return decode_token(
            token,
            secret_key=self.secret_key,
            algorithm=self.algorithm,
        )