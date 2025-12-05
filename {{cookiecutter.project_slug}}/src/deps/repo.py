from typing import AsyncGenerator, Type

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.repo.base import SQLAlchemyRepo

from ..repo.uow import UnitOfWork
from .session import get_async_session


def get_repo(repo: Type[SQLAlchemyRepo]):
    async def dep(session: AsyncSession = Depends(get_async_session)) -> AsyncGenerator[SQLAlchemyRepo, None]:
        yield repo(session)

    return dep

def get_uow():
    async def dep(session=Depends(get_async_session)) -> AsyncGenerator[UnitOfWork, None]:
        yield UnitOfWork(session)

    return dep

