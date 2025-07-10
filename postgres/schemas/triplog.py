from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, Dict, Any
from ..schemas.trip import TripSchema
from ..schemas.vehiculo import VehiculoSchema
from ..schemas.conductor import ConductorSchema
from ..schemas.empresa import EmpresaSchema
from ..schemas.ruta import RutaSchema

class TripLogCreateSchema(BaseModel):
    id_trip: Optional[Dict[str, Any]]
    accion: str
    descripcion: Optional[str] = None
    usuario_id: Optional[Dict[str, Any]]
    origen: Optional[str] = "sistema"
    id_vehiculo: Optional[Dict[str, Any]]
    id_conductor: Optional[Dict[str, Any]]
    id_empresa: Optional[Dict[str, Any]]
    id_ruta: Optional[Dict[str, Any]]
    patente_vehiculo: str
    nombre_conductor: str
    rut_empresa: str
    origen_viaje: str
    destino_viaje: str
    fecha_log: datetime
    fecha_salida_prog: datetime
    fecha_llegada_estim: datetime
    comentarios: str
    
    @validator(
        'fecha_log',
        'fecha_salida_prog',
        'fecha_llegada_estim',
        pre=True
    )
    
    def strip_tz(cls, value):
        if isinstance(value, str):
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if value and value.tzinfo:
            return value.astimezone(tz=None).replace(tzinfo=None)
        return value
    
    

class TripLogSchema(TripLogCreateSchema):
    id_log: int

    class Config:
        orm_mode = True
        