from __future__ import annotations

import uuid

from app.models.local_sync_operation import LocalSyncOperation
from app.repositories.sync_repository import SyncRepository


class IdempotencyService:
    def __init__(
        self,
        repository: SyncRepository,
    ) -> None:
        self.repository = repository

    def get_existing(
        self,
        operation_id: uuid.UUID,
    ) -> LocalSyncOperation | None:
        return self.repository.get_operation(operation_id)

    def is_processed(
        self,
        operation_id: uuid.UUID,
    ) -> bool:
        operation = self.repository.get_operation(operation_id)

        if operation is None:
            return False

        return operation.status in {
            "success",
            "failed",
            "conflict",
        }