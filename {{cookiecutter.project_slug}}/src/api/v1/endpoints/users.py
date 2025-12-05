from fastapi import APIRouter, Depends, HTTPException

from src import deps, schemas
from src.exceptions import repo as repo_exc
from src.repo.uow import UnitOfWork
from src.services.user_service import UserService

router = APIRouter()


@router.post("/")
async def create_user(
    user_in: schemas.UserCreate,
    _: schemas.User = Depends(deps.authenticated_user),
    service: UserService = Depends(deps.get_user_service())
) -> schemas.User:
    """
    Create User.
    """
    user = await service.create_user(user_in)
    return user


@router.get("/")
async def read_users(
    limit: int = 20,
    offset: int = 0,
    _: schemas.User = Depends(deps.authenticated_user),
    service: UserService = Depends(deps.get_user_service())
) -> list[schemas.User]:
    """
    Retrieve users.
    """
    users = await service.get_users_with_pagination(limit=limit, offset=offset)
    return users


@router.get("/me")
async def read_user(
    user: schemas.User = Depends(deps.authenticated_user)
) -> schemas.User:
    """
    Retrieve user from the bearer token
    """
    return user
