from src import schemas
from src.repo.uow import UnitOfWork
from src.services.auth import Authenticator

class UserService:
    def __init__(self, uow: UnitOfWork, authenticator: Authenticator) -> None:
        self.uow = uow
        self.authenticator = authenticator

    async def create_user(self, obj_in: schemas.UserCreateIn) -> schemas.UserCreateOut:
        hashed_password = self.authenticator.get_password_hash(obj_in.password)
        user = await self.uow.user_repo.create_user(obj_in, hashed_password)
        return user

    async def get_users_with_pagination(self, limit: int, offset: int) -> schemas.UserListOut:
        users = await self.uow.user_repo.get_list(limit=limit, offset=offset)
        return users