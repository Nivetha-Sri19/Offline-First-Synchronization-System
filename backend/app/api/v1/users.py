from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_admin
from app.core.exceptions import ResourceConflictError, ResourceNotFoundError
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth.request import UserRegisterRequest
from app.schemas.auth.response import UserResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "",
    response_model=list[UserResponse],
)
def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[User]:
    return UserRepository(db).list(
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    user = UserRepository(db).get_by_id(user_id)

    if user is None:
        raise ResourceNotFoundError("User not found.")

    return user


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    request: UserRegisterRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> User:
    repository = UserRepository(db)

    email = str(request.email).strip().lower()

    if repository.get_by_email(email) is not None:
        raise ResourceConflictError(
            "A user with this email already exists."
        )

    user = User(
        id=uuid.uuid4(),
        email=email,
        password_hash=hash_password(request.password),
        full_name=request.full_name.strip(),
        role="user",
        is_active=True,
    )

    return repository.create(user)