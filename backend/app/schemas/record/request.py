from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RecordCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    data: dict[str, Any] = Field(default_factory=dict)


class RecordUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    data: dict[str, Any] = Field(default_factory=dict)
    expected_version: int = Field(ge=1)


class RecordDeleteRequest(BaseModel):
    expected_version: int = Field(ge=1)


class RecordSearchRequest(BaseModel):
    search: str | None = Field(default=None, max_length=200)
    status: str | None = Field(default=None, max_length=30)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="updated_at", max_length=50)
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")