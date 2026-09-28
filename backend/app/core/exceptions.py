class ApplicationError(Exception):
    def __init__(
        self,
        message: str,
        *,
        code: str = "APPLICATION_ERROR",
        status_code: int = 400,
        details: dict | list | None = None,
    ) -> None:
        super().__init__(message)

        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class AuthenticationError(ApplicationError):
    def __init__(
        self,
        message: str = "Authentication failed.",
        *,
        details: dict | list | None = None,
    ) -> None:
        super().__init__(
            message,
            code="AUTHENTICATION_FAILED",
            status_code=401,
            details=details,
        )


class AuthorizationError(ApplicationError):
    def __init__(
        self,
        message: str = "You do not have permission to perform this action.",
        *,
        details: dict | list | None = None,
    ) -> None:
        super().__init__(
            message,
            code="AUTHORIZATION_FAILED",
            status_code=403,
            details=details,
        )


class ResourceNotFoundError(ApplicationError):
    def __init__(
        self,
        message: str = "Resource not found.",
        *,
        details: dict | list | None = None,
    ) -> None:
        super().__init__(
            message,
            code="RESOURCE_NOT_FOUND",
            status_code=404,
            details=details,
        )


class ResourceConflictError(ApplicationError):
    def __init__(
        self,
        message: str = "Resource conflict detected.",
        *,
        details: dict | list | None = None,
    ) -> None:
        super().__init__(
            message,
            code="RESOURCE_CONFLICT",
            status_code=409,
            details=details,
        )


class ValidationError(ApplicationError):
    def __init__(
        self,
        message: str = "Validation failed.",
        *,
        details: dict | list | None = None,
    ) -> None:
        super().__init__(
            message,
            code="VALIDATION_FAILED",
            status_code=422,
            details=details,
        )


class DuplicateOperationError(ApplicationError):
    def __init__(
        self,
        message: str = "The synchronization operation has already been processed.",
        *,
        details: dict | list | None = None,
    ) -> None:
        super().__init__(
            message,
            code="DUPLICATE_OPERATION",
            status_code=409,
            details=details,
        )


class SyncConflictError(ApplicationError):
    def __init__(
        self,
        message: str = "A synchronization conflict was detected.",
        *,
        details: dict | list | None = None,
    ) -> None:
        super().__init__(
            message,
            code="SYNC_CONFLICT",
            status_code=409,
            details=details,
        )


class DatabaseError(ApplicationError):
    def __init__(
        self,
        message: str = "A database error occurred.",
        *,
        details: dict | list | None = None,
    ) -> None:
        super().__init__(
            message,
            code="DATABASE_ERROR",
            status_code=500,
            details=details,
        )