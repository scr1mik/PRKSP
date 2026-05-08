from pydantic import BaseModel, Field


class EventBase(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=3, max_length=1000)
    year: int = Field(ge=2024, le=9999)
    category: str = Field(min_length=3, max_length=60)


class EventCreate(EventBase):
    pass


class EventUpdate(EventBase):
    pass


class EventRead(EventBase):
    id: int

    model_config = {"from_attributes": True}
