from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from ..schemas.trip import TripSchema

class PosicionGPSCreateSchema(BaseModel):
    timestamp: datetime
    latitud: float
    longitud: float
    velocidad_kmh: float
    rumbo_grados: float

class PosicionGPSUpdateSchema(BaseModel):
    timestamp: Optional[datetime] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    velocidad_kmh: Optional[float] = None
    rumbo_grados: Optional[float] = None

class PosicionGPSSchema(PosicionGPSCreateSchema):
    id_registro: int

    trip : TripSchema

    class Config:
        from_attributes = True