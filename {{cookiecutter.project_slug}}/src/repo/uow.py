from functools import cached_property

from sqlalchemy.ext.asyncio import AsyncSession

from src.repo.user_repo import UserRepo


class UnitOfWork:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @cached_property
    def user_repo(self) -> UserRepo:
        return UserRepo(self.session)