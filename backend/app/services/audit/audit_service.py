from __future__ import annotations

import uuid
from typing import Any

from app.models.audit_log import AuditLog
from app.repositories.audit_repository import AuditRepository


class AuditService:
    def __init__(
        self,
        repository: AuditRepository,
    ) -> None:
        self.repository = repository

    def log(
        self,
        *,
        user_id: uuid.UUID | None,
        action: str,
        entity_type: str,
        entity_id: str,
        old_value: dict[str, Any] | None = None,
        new_value: dict[str, Any] | None = None,
        ip_address: str | None = None,
        request_id: str | None = None,
        details: str | None = None,
    ) -> AuditLog:
        return self.repository.create(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            request_id=request_id,
            details=details,
        )