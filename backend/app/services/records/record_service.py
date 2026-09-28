from __future__ import annotations

import uuid
from datetime import UTC, datetime
from math import ceil

from app.core.exceptions import ResourceConflictError, ResourceNotFoundError
from app.models.record import Record
from app.repositories.record_repository import RecordRepository
from app.schemas.common import PaginationMeta
from app.schemas.record.response import RecordListResponse


class RecordService:
    def __init__(
        self,
        repository: RecordRepository,
    ) -> None:
        self.repository = repository

    def create(
        self,
        *,
        owner_id: uuid.UUID,
        data: dict,
    ) -> Record:
        record = Record(
            id=uuid.uuid4(),
            owner_id=owner_id,
            data=data,
            version=1,
            is_deleted=False,
        )

        return self.repository.create(record)

    def get(
        self,
        *,
        owner_id: uuid.UUID,
        record_id: uuid.UUID,
    ) -> Record:
        record = self.repository.get_by_id(record_id)

        if record is None or record.owner_id != owner_id:
            raise ResourceNotFoundError(
                "Record not found."
            )

        return record

    def list(
        self,
        *,
        owner_id: uuid.UUID,
        page: int,
        page_size: int,
        search: str | None,
        status: str | None,
        sort_by: str,
        sort_order: str,
    ) -> RecordListResponse:
        total = self.repository.count(
            owner_id=owner_id,
            search=search,
            status=status,
        )

        records = self.repository.list(
            owner_id=owner_id,
            page=page,
            page_size=page_size,
            search=search,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        total_pages = ceil(total / page_size) if total else 0

        return RecordListResponse(
            items=records,
            pagination=PaginationMeta(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=total_pages,
            ),
        )

    def update(
        self,
        *,
        owner_id: uuid.UUID,
        record_id: uuid.UUID,
        data: dict,
        expected_version: int,
    ) -> Record:
        record = self.repository.get_by_id_for_update(record_id)

        if record is None or record.owner_id != owner_id:
            raise ResourceNotFoundError(
                "Record not found."
            )

        if record.version != expected_version:
            raise ResourceConflictError(
                "Record version has changed.",
                details={
                    "record_id": str(record_id),
                    "expected_version": expected_version,
                    "server_version": record.version,
                },
            )

        record.data = data
        record.version += 1

        self.repository.update(record)

        return record

    def delete(
        self,
        *,
        owner_id: uuid.UUID,
        record_id: uuid.UUID,
        expected_version: int,
    ) -> Record:
        record = self.repository.get_by_id_for_update(record_id)

        if record is None or record.owner_id != owner_id:
            raise ResourceNotFoundError(
                "Record not found."
            )

        if record.version != expected_version:
            raise ResourceConflictError(
                "Record version has changed.",
                details={
                    "record_id": str(record_id),
                    "expected_version": expected_version,
                    "server_version": record.version,
                },
            )

        record.is_deleted = True
        record.deleted_at = datetime.now(UTC)
        record.version += 1

        self.repository.update(record)

        return record