from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.audit_log import AuditLog
    from app.models.conflict import Conflict
    from app.models.local_sync_operation import LocalSyncOperation
    from app.models.record import Record
    from app.models.sync_history import SyncHistory


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="user",
        server_default="user",
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="1",
        index=True,
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    records: Mapped[list[Record]] = relationship(
        "Record",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    sync_operations: Mapped[list[LocalSyncOperation]] = relationship(
        "LocalSyncOperation",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    sync_history: Mapped[list[SyncHistory]] = relationship(
        "SyncHistory",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    conflicts: Mapped[list[Conflict]] = relationship(
        "Conflict",
        back_populates="user",
        foreign_keys="Conflict.user_id",
        cascade="all, delete-orphan",
    )

    audit_logs: Mapped[list[AuditLog]] = relationship(
        "AuditLog",
        back_populates="user",
    )