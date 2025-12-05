from fastapi import Depends

from src.services.user_service import UserService
from src.services.auth import Authenticator
from .repo import get_uow


def get_user_service():
    async def dep(uow=Depends(get_uow()), authenticator=Depends()) -> UserService:
        yield UserService(uow=uow, authenticator=authenticator)
    return dep