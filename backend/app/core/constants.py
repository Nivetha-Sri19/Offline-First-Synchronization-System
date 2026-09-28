from enum import StrEnum


class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"


class SyncOperationStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    CONFLICT = "conflict"


class ConflictStatus(StrEnum):
    UNRESOLVED = "unresolved"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class ConflictResolutionStrategy(StrEnum):
    SERVER_WINS = "server_wins"
    CLIENT_WINS = "client_wins"
    LAST_WRITE_WINS = "last_write_wins"
    MANUAL = "manual"


class AuditAction(StrEnum):
    USER_REGISTERED = "user_registered"
    USER_LOGIN = "user_login"
    RECORD_CREATED = "record_created"
    RECORD_UPDATED = "record_updated"
    RECORD_DELETED = "record_deleted"
    SYNC_PROCESSED = "sync_processed"
    CONFLICT_CREATED = "conflict_created"
    CONFLICT_RESOLVED = "conflict_resolved"


class OperationType(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"