from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional
from ..schemas.ruta import RutaSchema
from ..schemas.empresa import EmpresaSchema
from ..schemas.vehiculo import VehiculoSchema
from ..schemas.estadoViaje import EstadoViajeSchema


class TripCreateSchema(BaseModel):
    fecha_registro: datetime
    fecha_salida_prog: datetime
    fecha_llegada_estim: datetime
    fecha_salida_real: datetime
    fecha_llegada_real: Optional[datetime]
    comentarios: str
    id_ruta: int
    id_empresa: int
    id_vehiculo: int
    id_estado: int
    
    @validator(
        "fecha_registro",
        "fecha_salida_prog",
        "fecha_llegada_estim",
        "fecha_salida_real",
        "fecha_llegada_real",
        pre=True
    )
    
    def strip_tz(cls, value):
        if isinstance(value, str):
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if value and value.tzinfo:
            return value.astimezone(tz=None).replace(tzinfo=None)
        return value
    
class TripUpdateSchema(BaseModel):
    fecha_registro: Optional[datetime] = None
    fecha_salida_prog: Optional[datetime] = None
    fecha_llegada_estim: Optional[datetime] = None
    fecha_salida_real: Optional[datetime] = None
    fecha_llegada_real: Optional[datetime] = None
    comentarios: Optional[str] = None
    id_ruta: Optional[int] = None
    id_empresa: Optional[int] = None
    id_vehiculo: Optional[int] = None
    id_estado: Optional[int] = None
    
class TripSchema(TripCreateSchema):
    id_trip: int

    ruta: RutaSchema
    empresa: EmpresaSchema
    vehiculo: VehiculoSchema
    estado: EstadoViajeSchema
    
    tiempo_estimado_horas: Optional[float] = None
    fecha_llegada_estim: Optional[datetime] = None
    porcentaje_viaje: Optional[float] = None
    distancia_total_km: Optional[float] = None

    class Config:
        from_attributes = True