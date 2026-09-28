from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.conflict import Conflict


class ConflictRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(
        self,
        conflict_id: uuid.UUID,
    ) -> Conflict | None:
        statement = select(Conflict).where(
            Conflict.conflict_id == conflict_id,
        )

        return self.session.scalar(statement)

    def get_by_id_for_update(
        self,
        conflict_id: uuid.UUID,
    ) -> Conflict | None:
        statement = (
            select(Conflict)
            .where(
                Conflict.conflict_id == conflict_id,
            )
            .with_for_update()
        )

        return self.session.scalar(statement)

    def create(
        self,
        conflict: Conflict,
    ) -> Conflict:
        self.session.add(conflict)
        self.session.flush()
        return conflict

    def update(
        self,
        conflict: Conflict,
    ) -> Conflict:
        self.session.add(conflict)
        self.session.flush()
        return conflict

    def count(
        self,
        *,
        user_id: uuid.UUID,
        status: str | None = None,
    ) -> int:
        statement = select(
            func.count(Conflict.id)
        ).where(
            Conflict.user_id == user_id,
        )

        if status:
            statement = statement.where(
                Conflict.status == status,
            )

        return int(self.session.scalar(statement) or 0)

    def list(
        self,
        *,
        user_id: uuid.UUID,
        page: int,
        page_size: int,
        status: str | None = None,
    ) -> list[Conflict]:
        statement = select(Conflict).where(
            Conflict.user_id == user_id,
        )

        if status:
            statement = statement.where(
                Conflict.status == status,
            )

        statement = (
            statement
            .order_by(Conflict.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        return list(self.session.scalars(statement).all())