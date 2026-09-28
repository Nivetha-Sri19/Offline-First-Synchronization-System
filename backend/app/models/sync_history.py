from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.record import Record
    from app.models.user import User


class SyncHistory(Base):
    __tablename__ = "sync_history"

    __table_args__ = (
        Index(
            "ix_sync_history_user_timestamp",
            "user_id",
            "timestamp",
        ),
        Index(
            "ix_sync_history_status",
            "status",
        ),
        Index(
            "ix_sync_history_conflict_status",
            "conflict_status",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    sync_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        unique=True,
        nullable=False,
        default=uuid.uuid4,
    )

    operation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        nullable=False,
        index=True,
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

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="CURRENT_TIMESTAMP",
        index=True,
    )

    error_details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    conflict_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="none",
        server_default="none",
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="sync_history",
    )

    record: Mapped[Record] = relationship(
        "Record",
        primaryjoin="foreign(SyncHistory.record_id) == Record.id",
        back_populates="sync_history",
        viewonly=True,
    )