from pydantic import BaseModel
from datetime import date
from typing import Optional
from ..schemas.conductor import ConductorSchema
from ..schemas.vehiculo import VehiculoSchema

class VehiculoConductorCreateSchema(BaseModel):
    id_vehiculo: int
    id_conductor: int
    fecha_inicio: date
    fecha_fin: Optional[date] = None

class VehiculoConductorSchema(VehiculoConductorCreateSchema):
    id_vehiculo: int
    id_conductor: int
    conductor: ConductorSchema
    vehiculo : VehiculoSchema

    class Config:
        orm_mode = True