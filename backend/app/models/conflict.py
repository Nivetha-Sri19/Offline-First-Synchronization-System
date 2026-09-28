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
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.record import Record
    from app.models.user import User


class Conflict(Base):
    __tablename__ = "conflicts"

    __table_args__ = (
        Index(
            "ix_conflicts_user_status",
            "user_id",
            "status",
        ),
        Index(
            "ix_conflicts_record_status",
            "record_id",
            "status",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    conflict_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        unique=True,
        nullable=False,
        default=uuid.uuid4,
    )

    record_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        nullable=False,
        index=True,
    )

    operation_id: Mapped[uuid.UUID] = mapped_column(
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

    client_version: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    server_version: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    client_payload: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    server_payload: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    resolution_strategy: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="unresolved",
        server_default="unresolved",
        index=True,
    )

    resolved_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="conflicts",
        foreign_keys=[user_id],
    )

    resolver: Mapped[User | None] = relationship(
        "User",
        foreign_keys=[resolved_by],
    )

    record: Mapped[Record] = relationship(
        "Record",
        primaryjoin="foreign(Conflict.record_id) == Record.id",
        back_populates="conflicts",
        viewonly=True,
    )