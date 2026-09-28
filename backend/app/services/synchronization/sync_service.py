from __future__ import annotations

import uuid
from datetime import UTC, datetime
from math import ceil

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.constants import SyncOperationStatus
from app.core.exceptions import ResourceConflictError, ResourceNotFoundError
from app.models.local_sync_operation import LocalSyncOperation
from app.models.record import Record
from app.models.sync_history import SyncHistory
from app.repositories.conflict_repository import ConflictRepository
from app.repositories.record_repository import RecordRepository
from app.repositories.sync_repository import SyncRepository
from app.schemas.conflict.request import ConflictResolutionRequest
from app.schemas.conflict.response import ConflictResponse
from app.schemas.sync.request import SyncPushRequest
from app.schemas.sync.response import (
    SyncConflictListResponse,
    SyncConflictResponse,
    SyncHistoryListResponse,
    SyncHistoryResponse,
    SyncOperationResponse,
    SyncPullResponse,
    SyncPushResponse,
    SyncStatusResponse,
)
from app.services.conflicts.resolution_service import ResolutionService
from app.services.synchronization.sync_processor import SyncProcessor


class SyncService:
    def __init__(
        self,
        session: Session,
        sync_repository: SyncRepository,
        record_repository: RecordRepository,
        conflict_repository: ConflictRepository,
    ) -> None:
        self.session = session
        self.sync_repository = sync_repository
        self.record_repository = record_repository
        self.conflict_repository = conflict_repository
        self.resolution_service = ResolutionService()

    def process_batch(
        self,
        *,
        user_id: uuid.UUID,
        request: SyncPushRequest,
    ) -> SyncPushResponse:
        results: list[SyncOperationResponse] = []

        successful = 0
        failed = 0
        conflicts = 0

        for operation_request in request.operations:
            try:
                result = self._process_operation(
                    user_id=user_id,
                    operation_request=operation_request,
                )

                results.append(result)

                if result.status == SyncOperationStatus.SUCCESS:
                    successful += 1
                elif result.status == SyncOperationStatus.CONFLICT:
                    conflicts += 1
                else:
                    failed += 1

            except Exception as exc:
                self.session.rollback()

                results.append(
                    SyncOperationResponse(
                        operation_id=operation_request.operation_id,
                        record_id=operation_request.record_id,
                        status=SyncOperationStatus.FAILED,
                        conflict_status="none",
                        message="Synchronization failed.",
                        error=str(exc),
                    )
                )

                failed += 1

        return SyncPushResponse(
            total_operations=len(request.operations),
            successful_operations=successful,
            failed_operations=failed,
            conflict_operations=conflicts,
            results=results,
        )

    def pull(
        self,
        *,
        user_id: uuid.UUID,
        page: int,
        page_size: int,
        updated_since: datetime | None,
    ) -> SyncPullResponse:
        base_filter = [
            Record.owner_id == user_id,
        ]

        if updated_since is not None:
            base_filter.append(
                Record.updated_at > updated_since,
            )

        total = int(
            self.session.scalar(
                select(func.count(Record.id)).where(*base_filter)
            )
            or 0
        )

        statement = (
            select(Record)
            .where(*base_filter)
            .order_by(Record.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        records = list(
            self.session.scalars(statement).all()
        )

        return SyncPullResponse(
            items=records,
            total=total,
            page=page,
            page_size=page_size,
            has_more=(page * page_size) < total,
            server_timestamp=datetime.now(UTC),
        )

    def list_conflicts(
        self,
        *,
        user_id: uuid.UUID,
        page: int,
        page_size: int,
        status: str | None,
    ) -> SyncConflictListResponse:
        total = self.conflict_repository.count(
            user_id=user_id,
            status=status,
        )

        conflicts = self.conflict_repository.list(
            user_id=user_id,
            page=page,
            page_size=page_size,
            status=status,
        )

        return SyncConflictListResponse(
            items=[
                SyncConflictResponse.model_validate(item)
                for item in conflicts
            ],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=ceil(total / page_size) if total else 0,
        )

    def resolve_conflict(
        self,
        *,
        user_id: uuid.UUID,
        conflict_id: uuid.UUID,
        request: ConflictResolutionRequest,
    ) -> ConflictResponse:
        conflict = self.conflict_repository.get_by_id_for_update(
            conflict_id
        )

        if conflict is None or conflict.user_id != user_id:
            raise ResourceNotFoundError("Conflict not found.")

        record = self.record_repository.get_by_id_for_update(
            conflict.record_id
        )

        if record is None:
            raise ResourceNotFoundError(
                "Record associated with conflict was not found."
            )

        self.resolution_service.resolve(
            conflict=conflict,
            record=record,
            strategy=request.strategy,
            resolved_data=request.resolved_data,
        )

        conflict.resolved_by = user_id

        self.record_repository.update(record)
        self.conflict_repository.update(conflict)

        self.session.commit()

        return ConflictResponse.model_validate(conflict)

    def history(
        self,
        *,
        user_id: uuid.UUID,
        page: int,
        page_size: int,
        status: str | None,
        conflict_status: str | None,
        operation_type: str | None,
    ) -> SyncHistoryListResponse:
        total = self.sync_repository.count_history(
            user_id=user_id,
            status=status,
            conflict_status=conflict_status,
            operation_type=operation_type,
        )

        items = self.sync_repository.list_history(
            user_id=user_id,
            page=page,
            page_size=page_size,
            status=status,
            conflict_status=conflict_status,
            operation_type=operation_type,
        )

        return SyncHistoryListResponse(
            items=[
                SyncHistoryResponse.model_validate(item)
                for item in items
            ],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=ceil(total / page_size) if total else 0,
        )

    def status(
        self,
        *,
        user_id: uuid.UUID,
    ) -> SyncStatusResponse:
        return SyncStatusResponse(
            pending_operations=self.sync_repository.count_operations(
                user_id=user_id,
                status="pending",
            ),
            processing_operations=self.sync_repository.count_operations(
                user_id=user_id,
                status="processing",
            ),
            successful_operations=self.sync_repository.count_operations(
                user_id=user_id,
                status="success",
            ),
            failed_operations=self.sync_repository.count_operations(
                user_id=user_id,
                status="failed",
            ),
            unresolved_conflicts=self.conflict_repository.count(
                user_id=user_id,
                status="unresolved",
            ),
            total_operations=self.sync_repository.count_operations(
                user_id=user_id,
            ),
            last_sync_at=self.sync_repository.last_successful_sync(
                user_id=user_id,
            ),
            server_timestamp=datetime.now(UTC),
        )

    def _process_operation(
        self,
        *,
        user_id: uuid.UUID,
        operation_request,
    ) -> SyncOperationResponse:
        existing = self.sync_repository.get_operation(
            operation_request.operation_id
        )

        if existing is not None:
            if existing.user_id != user_id:
                raise ResourceConflictError(
                    "Operation ID belongs to another user."
                )

            return self._existing_operation_response(existing)

        operation = LocalSyncOperation(
            operation_id=operation_request.operation_id,
            record_id=operation_request.record_id,
            user_id=user_id,
            operation_type=operation_request.operation_type.value,
            base_version=operation_request.base_version,
            payload=operation_request.payload,
            status=SyncOperationStatus.PROCESSING,
            attempt_count=1,
        )

        try:
            self.sync_repository.create_operation(operation)

        except IntegrityError as err:
            self.session.rollback()

            existing = self.sync_repository.get_operation(
                operation_request.operation_id
            )

            if existing is None:
                raise ResourceConflictError(
                    "Synchronization operation could not be created."
                ) from err

            if existing.user_id != user_id:
                raise ResourceConflictError(
                    "Operation ID belongs to another user."
                ) from err

            return self._existing_operation_response(existing)

        processor = SyncProcessor(
            session=self.session,
            record_repository=self.record_repository,
            sync_repository=self.sync_repository,
            conflict_repository=self.conflict_repository,
        )

        try:
            sync_status, conflict_status, server_version = (
                processor.process(
                    user_id=user_id,
                    operation=operation,
                )
            )

            operation.status = sync_status
            operation.processed_at = datetime.now(UTC)

            if sync_status == SyncOperationStatus.CONFLICT:
                operation.error_message = (
                    "Synchronization conflict detected."
                )

            self.sync_repository.create_history(
                SyncHistory(
                    sync_id=uuid.uuid4(),
                    operation_id=operation.operation_id,
                    record_id=operation.record_id,
                    user_id=user_id,
                    operation_type=operation.operation_type,
                    status=sync_status,
                    conflict_status=conflict_status,
                    error_details=operation.error_message,
                )
            )

            self.sync_repository.update_operation(operation)

            self.session.commit()

            return SyncOperationResponse(
                operation_id=operation.operation_id,
                record_id=operation.record_id,
                status=sync_status,
                conflict_status=conflict_status,
                server_version=server_version,
                message=(
                    "Synchronization completed."
                    if sync_status == SyncOperationStatus.SUCCESS
                    else "Synchronization conflict detected."
                ),
            )

        except Exception:
            self.session.rollback()
            raise

    @staticmethod
    def _existing_operation_response(
        operation: LocalSyncOperation,
    ) -> SyncOperationResponse:
        return SyncOperationResponse(
            operation_id=operation.operation_id,
            record_id=operation.record_id,
            status=operation.status,
            conflict_status=(
                "unresolved"
                if operation.status == SyncOperationStatus.CONFLICT
                else "none"
            ),
            message="Operation already processed.",
            error=operation.error_message,
        )