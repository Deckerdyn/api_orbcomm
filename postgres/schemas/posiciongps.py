from pydantic import BaseModel
from datetime import datetime
from ..schemas.trip import TripSchema

class PosicionGPSSchema(BaseModel):
    id_registro: int
    timestamp: datetime
    latitud: float
    longitud: float
    velocidad_kmh: float
    rumbo_grados: float

    trip : TripSchema

    class Config:
        from_attributes = True