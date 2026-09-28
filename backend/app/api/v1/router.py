# app/api/v1/router.py

from fastapi import APIRouter

from app.api.v1 import (
    auth,
    dashboard,
    records,
    synchronization,
    users,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(records.router)
api_router.include_router(synchronization.router)
api_router.include_router(dashboard.router)