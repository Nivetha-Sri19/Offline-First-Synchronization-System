from __future__ import annotations

import uuid
from math import ceil

from sqlalchemy.orm import Session

from app.core.constants import ConflictResolutionStrategy
from app.core.exceptions import ResourceNotFoundError
from app.repositories.conflict_repository import ConflictRepository
from app.repositories.record_repository import RecordRepository
from app.schemas.conflict.request import ConflictResolutionRequest
from app.schemas.conflict.response import (
    ConflictListResponse,
    ConflictResponse,
)
from app.services.conflicts.resolution_service import ResolutionService


class ConflictService:
    def __init__(
        self,
        session: Session,
        conflict_repository: ConflictRepository,
        record_repository: RecordRepository,
    ) -> None:
        self.session = session
        self.conflict_repository = conflict_repository
        self.record_repository = record_repository
        self.resolution_service = ResolutionService()

    def list(
        self,
        *,
        user_id: uuid.UUID,
        page: int,
        page_size: int,
        status: str | None,
    ) -> ConflictListResponse:
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

        total_pages = ceil(total / page_size) if total else 0

        return ConflictListResponse(
            items=conflicts,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def resolve(
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
            raise ResourceNotFoundError(
                "Conflict not found."
            )

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
            strategy=ConflictResolutionStrategy(request.strategy.value),
            resolved_data=request.resolved_data,
        )

        conflict.resolved_by = user_id

        self.record_repository.update(record)
        self.conflict_repository.update(conflict)

        self.session.commit()

        return ConflictResponse.model_validate(conflict)