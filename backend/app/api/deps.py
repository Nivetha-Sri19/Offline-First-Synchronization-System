from __future__ import annotations

import uuid
from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.security import decode_token
from app.database.redis import RedisManager
from app.database.session import DatabaseSessionManager
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.conflict_repository import ConflictRepository
from app.repositories.record_repository import RecordRepository
from app.repositories.sync_repository import SyncRepository
from app.repositories.user_repository import UserRepository
from app.services.audit.audit_service import AuditService
from app.services.auth.auth_service import AuthService
from app.services.auth.token_service import TokenService
from app.services.conflicts.conflict_service import ConflictService
from app.services.dashboard.dashboard_service import DashboardService
from app.services.records.record_service import RecordService
from app.services.synchronization.sync_service import SyncService

security_scheme = HTTPBearer(auto_error=False)

_database_manager: DatabaseSessionManager | None = None
_redis_manager: RedisManager | None = None


def initialize_dependencies(
    database_manager: DatabaseSessionManager,
    redis_manager: RedisManager,
) -> None:
    global _database_manager
    global _redis_manager

    _database_manager = database_manager
    _redis_manager = redis_manager


def get_db() -> Generator[Session, None, None]:
    if _database_manager is None:
        raise RuntimeError(
            "Database session manager has not been initialized."
        )

    yield from _database_manager.session_dependency()


def get_redis() -> RedisManager:
    if _redis_manager is None:
        raise RuntimeError(
            "Redis manager has not been initialized."
        )

    return _redis_manager


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        security_scheme
    ),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(
            credentials.credentials,
            secret_key=settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    subject = payload.get("sub")

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = uuid.UUID(subject)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = UserRepository(db).get_by_id(user_id)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is unavailable.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required.",
        )

    return current_user


def get_token_service(
    settings: Settings = Depends(get_settings),
) -> TokenService:
    return TokenService(
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        access_token_expire_minutes=settings.access_token_expire_minutes,
        refresh_token_expire_days=settings.refresh_token_expire_days,
    )


def get_auth_service(
    db: Session = Depends(get_db),
    token_service: TokenService = Depends(get_token_service),
) -> AuthService:
    return AuthService(
        user_repository=UserRepository(db),
        token_service=token_service,
    )


def get_record_service(
    db: Session = Depends(get_db),
) -> RecordService:
    return RecordService(
        repository=RecordRepository(db),
    )


def get_sync_service(
    db: Session = Depends(get_db),
) -> SyncService:
    return SyncService(
        session=db,
        sync_repository=SyncRepository(db),
        record_repository=RecordRepository(db),
        conflict_repository=ConflictRepository(db),
    )


def get_conflict_service(
    db: Session = Depends(get_db),
) -> ConflictService:
    return ConflictService(
        session=db,
        conflict_repository=ConflictRepository(db),
        record_repository=RecordRepository(db),
    )


def get_dashboard_service(
    db: Session = Depends(get_db),
) -> DashboardService:
    return DashboardService(
        sync_repository=SyncRepository(db),
        conflict_repository=ConflictRepository(db),
    )


def get_audit_service(
    db: Session = Depends(get_db),
) -> AuditService:
    return AuditService(
        repository=AuditRepository(db),
    )