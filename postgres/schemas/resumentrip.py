from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from ..schemas.trip import TripSchema

class ResumenTripSchema(BaseModel):
    id_resumen: int
    fecha_salida_real: datetime
    fecha_llegada_real: Optional[datetime]
    latitud_inicio: float
    longitud_inicio: float
    latitud_fin: float
    longitud_fin: float
    duracion_min: int
    velocidad_promedio: float

    trip: TripSchema

    class Config:
        from_attributes = True