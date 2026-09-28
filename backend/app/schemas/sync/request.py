from __future__ import annotations

import uuid
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SyncOperationType(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class SyncOperationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operation_id: uuid.UUID
    record_id: uuid.UUID
    operation_type: SyncOperationType
    base_version: int = Field(ge=0)
    payload: dict[str, Any] | None = None


class SyncPushRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operations: list[SyncOperationRequest] = Field(
        min_length=1,
        max_length=100,
    )


SyncBatchRequest = SyncPushRequest


class SyncHistoryFilterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str | None = Field(default=None, max_length=30)
    conflict_status: str | None = Field(default=None, max_length=30)
    operation_type: SyncOperationType | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)