from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.constants import SyncOperationStatus
from app.models.conflict import Conflict
from app.models.local_sync_operation import LocalSyncOperation
from app.models.record import Record
from app.models.sync_history import SyncHistory
from app.models.user import User


def seed_demo_data() -> None:
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
    )

    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    with SessionLocal() as session:
        user = session.scalar(
            select(User).where(
            User.email == "nivetha@gmail.com",
            User.is_active.is_(True),
            )

        )

        if user is None:
            print("ERROR: No active user found.")
            print("Register a user first, then run this script again.")
            return

        print(f"Seeding data for: {user.email}")
        print(f"User ID: {user.id}")

        now = datetime.now(UTC)

        # ---------------------------------------------------------
        # 1. RECORDS
        # ---------------------------------------------------------

        records: list[Record] = []

        for index in range(1, 41):
            record = Record(
                id=uuid.uuid4(),
                owner_id=user.id,
                data={
                    "title": f"Enterprise Record {index:02d}",
                    "customer": f"Customer {index:02d}",
                    "category": [
                        "Finance",
                        "Healthcare",
                        "Retail",
                        "Technology",
                        "Logistics",
                    ][(index - 1) % 5],
                    "amount": 10000 + (index * 1250),
                    "priority": (
                        "high"
                        if index % 3 == 0
                        else "medium"
                        if index % 2 == 0
                        else "low"
                    ),
                    "region": [
                        "Chennai",
                        "Bangalore",
                        "Hyderabad",
                        "Mumbai",
                        "Delhi",
                    ][(index - 1) % 5],
                    "status": (
                        "active"
                        if index % 4 != 0
                        else "review"
                    ),
                },
                version=2 if index > 30 else 1,
                is_deleted=False,
            )

            session.add(record)
            records.append(record)

        session.flush()

        print("Created 40 records.")

        # ---------------------------------------------------------
        # 2. 10 PENDING OPERATIONS
        # ---------------------------------------------------------

        for index in range(10):
            record = records[index]

            operation = LocalSyncOperation(
                operation_id=uuid.uuid4(),
                record_id=record.id,
                user_id=user.id,
                operation_type="update",
                base_version=record.version,
                payload={
                    **record.data,
                    "offline_update": True,
                    "queue_position": index + 1,
                },
                status=SyncOperationStatus.PENDING,
                attempt_count=0,
                error_message=None,
                created_at=now - timedelta(minutes=10 - index),
                processed_at=None,
            )

            session.add(operation)

        print("Created 10 pending operations.")

        # ---------------------------------------------------------
        # 3. 10 SUCCESSFUL OPERATIONS + HISTORY
        # ---------------------------------------------------------

        for index in range(10):
            record = records[10 + index]

            operation_id = uuid.uuid4()
            timestamp = now - timedelta(hours=1, minutes=index)

            operation = LocalSyncOperation(
                operation_id=operation_id,
                record_id=record.id,
                user_id=user.id,
                operation_type="update",
                base_version=1,
                payload={
                    **record.data,
                    "sync_status": "success",
                },
                status=SyncOperationStatus.SUCCESS,
                attempt_count=1,
                error_message=None,
                created_at=timestamp - timedelta(minutes=1),
                processed_at=timestamp,
            )

            history = SyncHistory(
                sync_id=uuid.uuid4(),
                operation_id=operation_id,
                record_id=record.id,
                user_id=user.id,
                operation_type="update",
                status=SyncOperationStatus.SUCCESS,
                timestamp=timestamp,
                error_details=None,
                conflict_status="none",
            )

            session.add(operation)
            session.add(history)

        print("Created 10 successful syncs.")

        # ---------------------------------------------------------
        # 4. 10 FAILED OPERATIONS + HISTORY
        # ---------------------------------------------------------

        failure_messages = [
            "Network timeout while synchronizing.",
            "Server temporarily unavailable.",
            "Database connection timeout.",
            "Request exceeded synchronization timeout.",
            "Remote service returned HTTP 503.",
            "Connection interrupted during upload.",
            "Synchronization retry limit reached.",
            "Temporary Redis coordination failure.",
            "Payload validation failed.",
            "Unexpected synchronization error.",
        ]

        for index in range(10):
            record = records[20 + index]

            operation_id = uuid.uuid4()
            timestamp = now - timedelta(hours=3, minutes=index)

            error_message = failure_messages[index]

            operation = LocalSyncOperation(
                operation_id=operation_id,
                record_id=record.id,
                user_id=user.id,
                operation_type="update",
                base_version=record.version,
                payload={
                    **record.data,
                    "sync_status": "failed",
                },
                status=SyncOperationStatus.FAILED,
                attempt_count=3,
                error_message=error_message,
                created_at=timestamp - timedelta(minutes=2),
                processed_at=timestamp,
            )

            history = SyncHistory(
                sync_id=uuid.uuid4(),
                operation_id=operation_id,
                record_id=record.id,
                user_id=user.id,
                operation_type="update",
                status=SyncOperationStatus.FAILED,
                timestamp=timestamp,
                error_details=error_message,
                conflict_status="none",
            )

            session.add(operation)
            session.add(history)

        print("Created 10 failed syncs.")

        # ---------------------------------------------------------
        # 5. 10 CONFLICT OPERATIONS + CONFLICTS + HISTORY
        # ---------------------------------------------------------

        for index in range(10):
            record = records[30 + index]

            operation_id = uuid.uuid4()
            timestamp = now - timedelta(hours=5, minutes=index)

            client_payload = {
                **record.data,
                "customer": f"Client Edited Customer {index + 1:02d}",
                "amount": 50000 + (index * 3000),
                "edited_offline": True,
            }

            server_payload = {
                **record.data,
                "customer": f"Server Customer {index + 1:02d}",
                "amount": 60000 + (index * 3500),
                "edited_server": True,
            }

            operation = LocalSyncOperation(
                operation_id=operation_id,
                record_id=record.id,
                user_id=user.id,
                operation_type="update",
                base_version=1,
                payload=client_payload,
                status=SyncOperationStatus.CONFLICT,
                attempt_count=1,
                error_message="Synchronization conflict detected.",
                created_at=timestamp - timedelta(minutes=1),
                processed_at=timestamp,
            )

            conflict = Conflict(
                conflict_id=uuid.uuid4(),
                record_id=record.id,
                operation_id=operation_id,
                user_id=user.id,
                client_version=1,
                server_version=record.version,
                client_payload=client_payload,
                server_payload=server_payload,
                resolution_strategy=None,
                status="unresolved",
                resolved_by=None,
                resolved_at=None,
                created_at=timestamp,
            )

            history = SyncHistory(
                sync_id=uuid.uuid4(),
                operation_id=operation_id,
                record_id=record.id,
                user_id=user.id,
                operation_type="update",
                status=SyncOperationStatus.CONFLICT,
                timestamp=timestamp,
                error_details="Client and server versions differ.",
                conflict_status="unresolved",
            )

            session.add(operation)
            session.add(conflict)
            session.add(history)

        print("Created 10 unresolved conflicts.")

        session.commit()

        print()
        print("=" * 60)
        print("DEMO DATA SEEDED SUCCESSFULLY")
        print("=" * 60)
        print("User              :", user.email)
        print("Records           : 40")
        print("Pending           : 10")
        print("Successful        : 10")
        print("Failed            : 10")
        print("Conflicts         : 10")
        print("Sync history      : 30")
        print("Total operations  : 40")
        print("=" * 60)

    engine.dispose()


if __name__ == "__main__":
    seed_demo_data()