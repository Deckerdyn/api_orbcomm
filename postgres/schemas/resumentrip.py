from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from ..schemas.trip import TripSchema

class ResumenTripCreateSchema(BaseModel):
    fecha_salida_real: datetime
    fecha_llegada_real: Optional[datetime]
    latitud_inicio: float
    longitud_inicio: float
    latitud_fin: float
    longitud_fin: float
    duracion_min: int
    velocidad_promedio: float
    id_trip: int

class ResumenTripUpdateSchema(BaseModel):
    fecha_salida_real: Optional[datetime] = None
    fecha_llegada_real: Optional[datetime] = None
    latitud_inicio: Optional[float] = None
    longitud_inicio: Optional[float] = None
    latitud_fin: Optional[float] = None
    longitud_fin: Optional[float] = None
    duracion_min: Optional[int] = None
    velocidad_promedio: Optional[float] = None
    id_trip: Optional[int] = None

class ResumenTripSchema(ResumenTripCreateSchema):
    id_resumen: int

    trip: TripSchema

    class Config:
        from_attributes = True