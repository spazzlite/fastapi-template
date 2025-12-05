from pydantic import BaseModel, ConfigDict


class BaseOutModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

class BaseListOutModel(BaseModel):
    total: int