from __future__ import annotations

import uuid

from app.repositories.conflict_repository import ConflictRepository
from app.repositories.sync_repository import SyncRepository
from app.schemas.sync.response import (
    SyncStatisticsResponse,
)


class DashboardService:
    def __init__(
        self,
        sync_repository: SyncRepository,
        conflict_repository: ConflictRepository,
    ) -> None:
        self.sync_repository = sync_repository
        self.conflict_repository = conflict_repository

    def get_summary(
        self,
        *,
        user_id: uuid.UUID,
    ) -> SyncStatisticsResponse:
        pending = self.sync_repository.count_operations(
            user_id=user_id,
            status="pending",
        )

        successful = self.sync_repository.count_history(
            user_id=user_id,
            status="success",
        )

        failed = self.sync_repository.count_history(
            user_id=user_id,
            status="failed",
        )

        conflicts = self.conflict_repository.count(
            user_id=user_id,
            status="unresolved",
        )

        total = self.sync_repository.count_history(
            user_id=user_id,
        )

        last_sync = self.sync_repository.last_successful_sync(
            user_id=user_id,
        )

        return SyncStatisticsResponse(
            pending_changes=pending,
            successful_syncs=successful,
            failed_syncs=failed,
            conflicts=conflicts,
            total_syncs=total,
            last_sync_at=last_sync,
        )