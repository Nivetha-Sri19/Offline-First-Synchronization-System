from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.core.constants import ConflictResolutionStrategy
from app.core.exceptions import ResourceConflictError
from app.models.conflict import Conflict
from app.models.record import Record


class ResolutionService:
    def resolve(
        self,
        *,
        conflict: Conflict,
        record: Record,
        strategy: ConflictResolutionStrategy,
        resolved_data: dict[str, Any] | None,
    ) -> Record:
        if conflict.status != "unresolved":
            raise ResourceConflictError(
                "Conflict has already been resolved."
            )

        if strategy == ConflictResolutionStrategy.SERVER_WINS:
            pass

        elif strategy == ConflictResolutionStrategy.CLIENT_WINS:
            record.data = conflict.client_payload or {}
            record.version += 1

        elif strategy == ConflictResolutionStrategy.LAST_WRITE_WINS:
            record.data = conflict.client_payload or {}
            record.version += 1

        elif strategy == ConflictResolutionStrategy.MANUAL:
            if resolved_data is None:
                raise ResourceConflictError(
                    "Manual conflict resolution requires resolved_data."
                )

            record.data = resolved_data
            record.version += 1

        else:
            raise ResourceConflictError(
                "Unsupported conflict resolution strategy."
            )

        conflict.resolution_strategy = strategy.value
        conflict.status = "resolved"
        conflict.resolved_at = datetime.now(UTC)

        return record