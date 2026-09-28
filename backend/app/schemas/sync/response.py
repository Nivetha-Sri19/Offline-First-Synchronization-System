from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.schemas.record.response import RecordResponse


class SyncOperationResponse(BaseModel):
    operation_id: uuid.UUID
    record_id: uuid.UUID
    status: str
    conflict_status: str
    server_version: int | None = None
    message: str | None = None
    error: str | None = None


class SyncPushResponse(BaseModel):
    total_operations: int
    successful_operations: int
    failed_operations: int
    conflict_operations: int
    results: list[SyncOperationResponse]


SyncBatchResponse = SyncPushResponse


class SyncPullResponse(BaseModel):
    items: list[RecordResponse]
    total: int
    page: int
    page_size: int
    has_more: bool
    server_timestamp: datetime


class SyncHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sync_id: uuid.UUID
    operation_id: uuid.UUID
    record_id: uuid.UUID
    operation_type: str
    status: str
    timestamp: datetime
    error_details: str | None
    conflict_status: str


class SyncHistoryListResponse(BaseModel):
    items: list[SyncHistoryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SyncConflictResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    conflict_id: uuid.UUID
    record_id: uuid.UUID
    operation_id: uuid.UUID
    client_version: int
    server_version: int
    client_payload: dict[str, Any] | None
    server_payload: dict[str, Any] | None
    resolution_strategy: str | None
    status: str
    resolved_by: uuid.UUID | None
    resolved_at: datetime | None
    created_at: datetime


class SyncConflictListResponse(BaseModel):
    items: list[SyncConflictResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SyncStatusResponse(BaseModel):
    pending_operations: int
    processing_operations: int
    successful_operations: int
    failed_operations: int
    unresolved_conflicts: int
    total_operations: int
    last_sync_at: datetime | None
    server_timestamp: datetime


class SyncStatisticsResponse(BaseModel):
    pending_changes: int
    successful_syncs: int
    failed_syncs: int
    conflicts: int
    total_syncs: int
    last_sync_at: datetime | None


class SyncDashboardResponse(BaseModel):
    statistics: SyncStatisticsResponse
    recent_syncs: list[SyncHistoryResponse]