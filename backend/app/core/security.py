from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)

_password_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
)


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password cannot be empty.")

    return _password_hasher.hash(password)


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    if not password or not password_hash:
        return False

    try:
        return _password_hasher.verify(
            password_hash,
            password,
        )
    except (
        VerifyMismatchError,
        VerificationError,
        InvalidHashError,
    ):
        return False


def create_access_token(
    *,
    subject: str,
    secret_key: str,
    algorithm: str,
    expires_minutes: int,
    role: str,
) -> str:
    now = datetime.now(UTC)

    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }

    return jwt.encode(
        payload,
        secret_key,
        algorithm=algorithm,
    )


def create_refresh_token(
    *,
    subject: str,
    secret_key: str,
    algorithm: str,
    expires_days: int,
) -> str:
    now = datetime.now(UTC)

    payload: dict[str, Any] = {
        "sub": subject,
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=expires_days),
    }

    return jwt.encode(
        payload,
        secret_key,
        algorithm=algorithm,
    )


def decode_token(
    token: str,
    *,
    secret_key: str,
    algorithm: str,
) -> dict[str, Any]:
    return jwt.decode(
        token,
        secret_key,
        algorithms=[algorithm],
    )