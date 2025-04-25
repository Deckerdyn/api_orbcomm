from pydantic import BaseModel
from typing import List, Optional

class AssetStatus(BaseModel):
    assetName: str
    assetType: str
    messageStamp: str
    batteryVoltage: float
    reeferState: str
    latitude: float
    longitude: float
    city: str
    state: str
    street: str
    country: str

class TokenResponse(BaseModel):
    watermark: Optional[int]
    data: List[AssetStatus]
