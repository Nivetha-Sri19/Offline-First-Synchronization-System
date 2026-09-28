from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.constants import OperationType, SyncOperationStatus
from app.core.exceptions import ResourceNotFoundError
from app.models.conflict import Conflict
from app.models.local_sync_operation import LocalSyncOperation
from app.models.record import Record
from app.repositories.conflict_repository import ConflictRepository
from app.repositories.record_repository import RecordRepository
from app.repositories.sync_repository import SyncRepository
from app.services.synchronization.version_service import VersionService


class SyncProcessor:
    def __init__(
        self,
        session: Session,
        record_repository: RecordRepository,
        sync_repository: SyncRepository,
        conflict_repository: ConflictRepository,
    ) -> None:
        self.session = session
        self.record_repository = record_repository
        self.sync_repository = sync_repository
        self.conflict_repository = conflict_repository

    def process(
        self,
        *,
        user_id: uuid.UUID,
        operation: LocalSyncOperation,
    ) -> tuple[str, str, int | None]:
        record = self.record_repository.get_by_id_for_update(
            operation.record_id
        )

        if operation.operation_type == OperationType.CREATE:
            return self._process_create(
                user_id=user_id,
                operation=operation,
                record=record,
            )

        if record is None:
            raise ResourceNotFoundError(
                "Record not found for synchronization."
            )

        version_result = VersionService.check(
            client_version=operation.base_version,
            server_version=record.version,
        )

        if not version_result.matches:
            return self._create_conflict(
                user_id=user_id,
                operation=operation,
                record=record,
            )

        if operation.operation_type == OperationType.UPDATE:
            return self._process_update(
                operation=operation,
                record=record,
            )

        if operation.operation_type == OperationType.DELETE:
            return self._process_delete(
                operation=operation,
                record=record,
            )

        raise ValueError(
            f"Unsupported operation type: {operation.operation_type}"
        )

    def _process_create(
        self,
        *,
        user_id: uuid.UUID,
        operation: LocalSyncOperation,
        record: Record | None,
    ) -> tuple[str, str, int]:
        if record is not None:
            return self._create_conflict(
                user_id=user_id,
                operation=operation,
                record=record,
            )

        new_record = Record(
            id=operation.record_id,
            owner_id=user_id,
            data=operation.payload or {},
            version=1,
            is_deleted=False,
        )

        self.record_repository.create(new_record)

        return (
            SyncOperationStatus.SUCCESS,
            "none",
            new_record.version,
        )

    def _process_update(
        self,
        *,
        operation: LocalSyncOperation,
        record: Record,
    ) -> tuple[str, str, int]:
        record.data = operation.payload or {}
        record.version += 1

        self.record_repository.update(record)

        return (
            SyncOperationStatus.SUCCESS,
            "none",
            record.version,
        )

    def _process_delete(
        self,
        *,
        operation: LocalSyncOperation,
        record: Record,
    ) -> tuple[str, str, int]:
        record.is_deleted = True
        record.deleted_at = datetime.now(UTC)
        record.version += 1

        self.record_repository.update(record)

        return (
            SyncOperationStatus.SUCCESS,
            "none",
            record.version,
        )

    def _create_conflict(
        self,
        *,
        user_id: uuid.UUID,
        operation: LocalSyncOperation,
        record: Record,
    ) -> tuple[str, str, int]:
        conflict = Conflict(
            conflict_id=uuid.uuid4(),
            record_id=record.id,
            operation_id=operation.operation_id,
            user_id=user_id,
            client_version=operation.base_version,
            server_version=record.version,
            client_payload=operation.payload,
            server_payload=record.data,
            status="unresolved",
        )

        self.conflict_repository.create(conflict)

        return (
            SyncOperationStatus.CONFLICT,
            "unresolved",
            record.version,
        )