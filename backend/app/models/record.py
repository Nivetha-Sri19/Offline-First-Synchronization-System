from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.conflict import Conflict
    from app.models.local_sync_operation import LocalSyncOperation
    from app.models.sync_history import SyncHistory
    from app.models.user import User


class Record(Base, TimestampMixin):
    __tablename__ = "records"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    owner_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    data: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    version: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=1,
        server_default="1",
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
        index=True,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    owner: Mapped[User] = relationship(
        "User",
        back_populates="records",
    )

    sync_operations: Mapped[list[LocalSyncOperation]] = relationship(
        "LocalSyncOperation",
        primaryjoin="foreign(LocalSyncOperation.record_id) == Record.id",
        back_populates="record",
        viewonly=True,
    )

    sync_history: Mapped[list[SyncHistory]] = relationship(
        "SyncHistory",
        primaryjoin="foreign(SyncHistory.record_id) == Record.id",
        back_populates="record",
        viewonly=True,
    )

    conflicts: Mapped[list[Conflict]] = relationship(
        "Conflict",
        primaryjoin="foreign(Conflict.record_id) == Record.id",
        back_populates="record",
        viewonly=True,
    )