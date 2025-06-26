from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from ..schemas.ruta import RutaSchema
from ..schemas.empresa import EmpresaSchema
from ..schemas.vehiculo import VehiculoSchema
from ..schemas.estadoViaje import EstadoViajeSchema


class TripCreateSchema(BaseModel):
    id_trip: int
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

    class Config:
        from_attributes = True