from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PricePredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    address: str = ""
    building_type: str = Field(default="기타")
    total_area: float = Field(gt=0)
    land_area: float = Field(gt=0)
    build_year: int = Field(ge=1800, le=2100)
    contract_year: int = Field(ge=2000, le=2100)
    contract_month: int = Field(default=1, ge=1, le=12)
    contract_day: int = Field(default=1, ge=1, le=31)
    road_condition: str = "기타"
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class PricePredictionResponse(BaseModel):
    predicted_price_manwon: int
    predicted_price_text: str
