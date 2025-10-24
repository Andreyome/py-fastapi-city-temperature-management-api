from pydantic import BaseModel, ConfigDict


class Temperature(BaseModel):
    temperature: float
    city_id: int


class TemperatureSchema(BaseModel):
    id: int
    temperature: float
    city_id: int

    model_config = ConfigDict(from_attributes=True)
