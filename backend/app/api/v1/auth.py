from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import get_auth_service, get_current_user
from app.models.user import User
from app.schemas.auth.request import (
    UserLoginRequest,
    UserRegisterRequest,
)
from app.schemas.auth.response import TokenResponse, UserResponse
from app.services.auth.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: UserRegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> User:
    return service.register(
        email=request.email,
        password=request.password,
        full_name=request.full_name,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: UserLoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    _, tokens = service.login(
        email=request.email,
        password=request.password,
    )

    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        expires_in=tokens.expires_in,
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user