from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.core.exceptions import AuthenticationError, ResourceConflictError
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth.token_service import TokenPair, TokenService


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        token_service: TokenService,
    ) -> None:
        self.user_repository = user_repository
        self.token_service = token_service

    def register(
        self,
        *,
        email: str,
        password: str,
        full_name: str,
    ) -> User:
        normalized_email = email.strip().lower()

        existing_user = self.user_repository.get_by_email(
            normalized_email
        )

        if existing_user is not None:
            raise ResourceConflictError(
                "A user with this email already exists."
            )

        user = User(
            id=uuid.uuid4(),
            email=normalized_email,
            password_hash=hash_password(password),
            full_name=full_name.strip(),
            role="user",
            is_active=True,
        )

        return self.user_repository.create(user)

    def login(
        self,
        *,
        email: str,
        password: str,
    ) -> tuple[User, TokenPair]:
        normalized_email = email.strip().lower()

        user = self.user_repository.get_by_email(
            normalized_email
        )

        if user is None:
            raise AuthenticationError(
                "Invalid email or password."
            )

        if not user.is_active:
            raise AuthenticationError(
                "User account is inactive."
            )

        password_valid = verify_password(
            password,
            user.password_hash,
        )

        if not password_valid:
            raise AuthenticationError(
                "Invalid email or password."
            )

        user.last_login_at = datetime.now(UTC)

        self.user_repository.update(user)

        tokens = self.token_service.create_tokens(
            user_id=str(user.id),
            role=user.role,
        )

        return user, tokens