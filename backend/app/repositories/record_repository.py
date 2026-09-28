from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Select, and_, func, select
from sqlalchemy.orm import Session

from app.models.record import Record


class RecordRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(
        self,
        record_id: uuid.UUID,
        *,
        include_deleted: bool = False,
    ) -> Record | None:
        statement = select(Record).where(
            Record.id == record_id,
        )

        if not include_deleted:
            statement = statement.where(
                Record.is_deleted.is_(False),
            )

        return self.session.scalar(statement)

    def get_by_id_for_update(
        self,
        record_id: uuid.UUID,
    ) -> Record | None:
        statement = (
            select(Record)
            .where(Record.id == record_id)
            .with_for_update()
        )

        return self.session.scalar(statement)

    def create(self, record: Record) -> Record:
        self.session.add(record)
        self.session.flush()
        return record

    def update(self, record: Record) -> Record:
        self.session.add(record)
        self.session.flush()
        return record

    def count(
        self,
        *,
        owner_id: uuid.UUID,
        search: str | None = None,
        status: str | None = None,
    ) -> int:
        statement = select(func.count(Record.id)).where(
            Record.owner_id == owner_id,
        )

        if status == "deleted":
            statement = statement.where(Record.is_deleted.is_(True))
        elif status == "active":
            statement = statement.where(Record.is_deleted.is_(False))

        if search:
            pattern = f"%{search}%"
            statement = statement.where(
                func.cast(Record.data, str).like(pattern)
            )

        return int(self.session.scalar(statement) or 0)

    def list(
        self,
        *,
        owner_id: uuid.UUID,
        page: int,
        page_size: int,
        search: str | None = None,
        status: str | None = None,
        sort_by: str = "updated_at",
        sort_order: str = "desc",
    ) -> list[Record]:
        allowed_sort_columns: dict[str, object] = {
            "created_at": Record.created_at,
            "updated_at": Record.updated_at,
            "version": Record.version,
        }

        sort_column = allowed_sort_columns.get(
            sort_by,
            Record.updated_at,
        )

        order_expression = (
            sort_column.asc()
            if sort_order == "asc"
            else sort_column.desc()
        )

        statement: Select[tuple[Record]] = (
            select(Record)
            .where(Record.owner_id == owner_id)
        )

        if status == "deleted":
            statement = statement.where(
                Record.is_deleted.is_(True),
            )
        else:
            statement = statement.where(
                Record.is_deleted.is_(False),
            )

        if search:
            pattern = f"%{search}%"
            statement = statement.where(
                func.cast(Record.data, str).like(pattern)
            )

        statement = (
            statement
            .order_by(order_expression)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        return list(self.session.scalars(statement).all())

    def update_with_version(
        self,
        record: Record,
        *,
        expected_version: int,
    ) -> bool:
        statement = (
            select(Record)
            .where(
                and_(
                    Record.id == record.id,
                    Record.version == expected_version,
                )
            )
            .with_for_update()
        )

        current = self.session.scalar(statement)

        if current is None:
            return False

        current.data = record.data
        current.version = expected_version + 1
        current.is_deleted = record.is_deleted
        current.deleted_at = record.deleted_at

        self.session.flush()
        return True

    def soft_delete(
        self,
        record: Record,
        *,
        expected_version: int,
        deleted_at: datetime,
    ) -> bool:
        statement = (
            select(Record)
            .where(
                and_(
                    Record.id == record.id,
                    Record.version == expected_version,
                    Record.is_deleted.is_(False),
                )
            )
            .with_for_update()
        )

        current = self.session.scalar(statement)

        if current is None:
            return False

        current.is_deleted = True
        current.deleted_at = deleted_at
        current.version = expected_version + 1

        self.session.flush()
        return True