from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from ..schemas.ruta import RutaSchema
from ..schemas.empresa import EmpresaSchema
from ..schemas.vehiculo import VehiculoSchema
from ..schemas.estadoViaje import EstadoViajeSchema


class TripSchema(BaseModel):
    id_trip: int
    fecha_registro: datetime
    fecha_salida_prog: datetime
    fecha_llegada_estim: datetime
    fecha_salida_real: datetime
    fecha_llegada_real: Optional[datetime]
    comentarios: str

    ruta: RutaSchema
    empresa: EmpresaSchema
    vehiculo: VehiculoSchema
    estado: EstadoViajeSchema

    class Config:
        from_attributes = True