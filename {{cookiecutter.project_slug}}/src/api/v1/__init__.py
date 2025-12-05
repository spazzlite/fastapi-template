from fastapi import APIRouter

from .endpoints import users, auth


v1_router = APIRouter()

v1_router.include_router(users.router, prefix="/users")
v1_router.include_router(auth.router, prefix="/auth")

