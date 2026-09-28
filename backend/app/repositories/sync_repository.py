from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.local_sync_operation import LocalSyncOperation
from app.models.sync_history import SyncHistory


class SyncRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_operation(
        self,
        operation_id: uuid.UUID,
    ) -> LocalSyncOperation | None:
        return self.session.scalar(
            select(LocalSyncOperation).where(
                LocalSyncOperation.operation_id == operation_id,
            )
        )

    def get_operation_for_update(
        self,
        operation_id: uuid.UUID,
    ) -> LocalSyncOperation | None:
        return self.session.scalar(
            select(LocalSyncOperation)
            .where(LocalSyncOperation.operation_id == operation_id)
            .with_for_update()
        )

    def create_operation(
        self,
        operation: LocalSyncOperation,
    ) -> LocalSyncOperation:
        self.session.add(operation)
        self.session.flush()
        return operation

    def update_operation(
        self,
        operation: LocalSyncOperation,
    ) -> LocalSyncOperation:
        self.session.add(operation)
        self.session.flush()
        return operation

    def create_history(
        self,
        history: SyncHistory,
    ) -> SyncHistory:
        self.session.add(history)
        self.session.flush()
        return history

    def list_history(
        self,
        *,
        user_id: uuid.UUID,
        page: int,
        page_size: int,
        status: str | None = None,
        conflict_status: str | None = None,
        operation_type: str | None = None,
    ) -> list[SyncHistory]:
        statement = select(SyncHistory).where(
            SyncHistory.user_id == user_id,
        )

        if status:
            statement = statement.where(
                SyncHistory.status == status,
            )

        if conflict_status:
            statement = statement.where(
                SyncHistory.conflict_status == conflict_status,
            )

        if operation_type:
            statement = statement.where(
                SyncHistory.operation_type == operation_type,
            )

        statement = (
            statement
            .order_by(SyncHistory.timestamp.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        return list(self.session.scalars(statement).all())

    def count_history(
        self,
        *,
        user_id: uuid.UUID,
        status: str | None = None,
        conflict_status: str | None = None,
        operation_type: str | None = None,
    ) -> int:
        statement = select(
            func.count(SyncHistory.id)
        ).where(
            SyncHistory.user_id == user_id,
        )

        if status:
            statement = statement.where(
                SyncHistory.status == status,
            )

        if conflict_status:
            statement = statement.where(
                SyncHistory.conflict_status == conflict_status,
            )

        if operation_type:
            statement = statement.where(
                SyncHistory.operation_type == operation_type,
            )

        return int(self.session.scalar(statement) or 0)

    def count_operations(
        self,
        *,
        user_id: uuid.UUID,
        status: str | None = None,
    ) -> int:
        statement = select(
            func.count(LocalSyncOperation.id)
        ).where(
            LocalSyncOperation.user_id == user_id,
        )

        if status:
            statement = statement.where(
                LocalSyncOperation.status == status,
            )

        return int(self.session.scalar(statement) or 0)

    def last_successful_sync(
        self,
        *,
        user_id: uuid.UUID,
    ) -> datetime | None:
        return self.session.scalar(
            select(
                func.max(SyncHistory.timestamp)
            ).where(
                SyncHistory.user_id == user_id,
                SyncHistory.status == "success",
            )
        )