from typing import Any, Generator, Generic, Type, TypeVar

from sqlalchemy import Numeric, cast, delete, desc, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.base import BaseModel as OrmBaseModel
from src.schemas.admin.base import BaseListOutModel, BaseOutModel


OrmModel = TypeVar("OrmModel", bound=OrmBaseModel)
PydanticModelOut = TypeVar("PydanticModelOut", bound=BaseOutModel)
PydanticListOut = TypeVar("PydanticListOut", bound=BaseListOutModel)
PydanticListItemOut = TypeVar("PydanticListItemOut", bound=BaseOutModel)


class SQLAlchemyRepo(Generic[OrmModel, PydanticModelOut, PydanticListOut, PydanticListItemOut]):
    ORM_MODEL: Type[OrmModel]
    OUT_MODEL: Type[PydanticModelOut]
    OUT_LIST_MODEL: Type[PydanticListOut]
    OUT_LIST_ITEM_MODEL: Type[PydanticListItemOut]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        for attr in ["ORM_MODEL", "OUT_MODEL", "OUT_LIST_MODEL", "OUT_LIST_ITEM_MODEL"]:
            assert hasattr(self, attr), f"Class {self.__class__.__name__} must define attribute {attr}"

    async def get_list(
        self,
        limit: int,
        offset: int,
        custom_out_list_class: Type[PydanticListOut] | None = None,
        custom_out_list_item_class: Type[PydanticListItemOut] | None = None,
    ) -> PydanticListOut:
        list_out_item_class = custom_out_list_item_class if custom_out_list_item_class else self.OUT_LIST_ITEM_MODEL
        list_out_class = custom_out_list_class if custom_out_list_class else self.OUT_LIST_MODEL
        count_stmt = select(func.count()).select_from(self.ORM_MODEL)
        stmt_select_model = select(self.ORM_MODEL).limit(limit).offset(offset).order_by(desc("id"))

        count_result = await self.session.scalar(count_stmt)
        select_model_result = await self.session.scalars(stmt_select_model)

        items_list = [list_out_item_class.model_validate(item) for item in select_model_result]

        return list_out_class(total=count_result, items=items_list)

    async def get_by_id(self, _id: Any, custom_model_out: Type[PydanticModelOut] | None = None) -> PydanticModelOut:
        stmt = select(self.ORM_MODEL).where(self.ORM_MODEL.id == _id)
        result = await self.session.scalar(stmt)
        model_out = custom_model_out if custom_model_out else self.OUT_MODEL
        return model_out.model_validate(result)

    async def create(
        self, create_params: dict, custom_out_class: Type[PydanticModelOut] | None = None
    ) -> PydanticModelOut:
        stmt = insert(self.ORM_MODEL).returning(self.ORM_MODEL).values(**create_params)
        result = await self.session.scalar(stmt)
        model_out = custom_out_class if custom_out_class else self.OUT_MODEL
        return model_out.model_validate(result)

    async def get_one_by_kwargs(self, **kwargs) -> PydanticModelOut:
        stmt = select(self.ORM_MODEL).filter_by(**kwargs)
        result = await self.session.scalar(stmt)
        return self.OUT_MODEL.model_validate(result)

    async def get_by_kwargs(self, **kwargs) -> Generator[PydanticModelOut, Any, None]:
        stmt = select(self.ORM_MODEL).filter_by(**kwargs)
        result = await self.session.scalars(stmt)
        return (self.OUT_MODEL.model_validate(item) for item in result)

    async def update(
        self, _id: Any, update_params: dict, custom_out_model: Type[PydanticModelOut] | None = None
    ) -> PydanticModelOut:
        for key in update_params:
            if not hasattr(self, key):
                assert hasattr(self, key), f"Class {self.__class__.__name__} must define attribute {key}"

        out_model = custom_out_model if custom_out_model else self.OUT_MODEL
        upd_stmt = update(self.ORM_MODEL).where(self.ORM_MODEL.id == _id).values(**update_params)
        await self.session.execute(upd_stmt)
        select_stmt = select(self.ORM_MODEL).where(self.ORM_MODEL.id == _id)
        result = await self.session.scalar(select_stmt)
        return out_model.model_validate(result)

    async def delete(self, _id: Any) -> None:
        stmt = delete(self.ORM_MODEL).where(self.ORM_MODEL.id == _id)
        await self.session.execute(stmt)
        await self.session.commit()


