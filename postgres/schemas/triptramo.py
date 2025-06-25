from pydantic import BaseModel
from datetime import datetime
from ..schemas.tramo import TramoSchema
from ..schemas.estadoViaje import EstadoViajeSchema
from ..schemas.trip import TripSchema

class TripTramoSchema(BaseModel):
    fecha_salida: datetime
    fecha_llegada: datetime
    orden: int

    trip: TripSchema
    tramo: TramoSchema
    estado: EstadoViajeSchema

    class Config:
        orm_mode = True