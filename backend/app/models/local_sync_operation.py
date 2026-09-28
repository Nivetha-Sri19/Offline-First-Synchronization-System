from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.record import Record
    from app.models.user import User


class LocalSyncOperation(Base):
    __tablename__ = "local_sync_operations"

    __table_args__ = (
        UniqueConstraint(
            "operation_id",
            name="uq_local_sync_operations_operation_id",
        ),
        Index(
            "ix_local_sync_operations_user_status",
            "user_id",
            "status",
        ),
        Index(
            "ix_local_sync_operations_record_id",
            "record_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    operation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        nullable=False,
    )

    record_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        nullable=False,
        index=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    operation_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    base_version: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    payload: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",
        server_default="pending",
        index=True,
    )

    attempt_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
        server_default="0",
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="CURRENT_TIMESTAMP",
    )

    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="sync_operations",
    )

    record: Mapped[Record] = relationship(
        "Record",
        primaryjoin="foreign(LocalSyncOperation.record_id) == Record.id",
        back_populates="sync_operations",
        viewonly=True,
    )