from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    ApplicationError,
    AuthenticationError,
    AuthorizationError,
    ResourceConflictError,
    ResourceNotFoundError,
    ValidationError,
)


async def application_error_handler(
    request: Request,
    exc: ApplicationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "data": exc.details,
            },
        },
    )


async def authentication_error_handler(
    request: Request,
    exc: AuthenticationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "data": exc.details,
            },
        },
    )


async def authorization_error_handler(
    request: Request,
    exc: AuthorizationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "data": exc.details,
            },
        },
    )


async def resource_not_found_error_handler(
    request: Request,
    exc: ResourceNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "data": exc.details,
            },
        },
    )


async def resource_conflict_error_handler(
    request: Request,
    exc: ResourceConflictError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "data": exc.details,
            },
        },
    )


async def validation_error_handler(
    request: Request,
    exc: ValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "data": exc.details,
            },
        },
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal server error occurred.",
                "data": None,
            },
        },
    )


def register_exception_handlers(application: FastAPI) -> None:
    application.add_exception_handler(
        ApplicationError,
        application_error_handler,
    )
    application.add_exception_handler(
        AuthenticationError,
        authentication_error_handler,
    )
    application.add_exception_handler(
        AuthorizationError,
        authorization_error_handler,
    )
    application.add_exception_handler(
        ResourceNotFoundError,
        resource_not_found_error_handler,
    )
    application.add_exception_handler(
        ResourceConflictError,
        resource_conflict_error_handler,
    )
    application.add_exception_handler(
        ValidationError,
        validation_error_handler,
    )
    application.add_exception_handler(
        Exception,
        unhandled_exception_handler,
    )