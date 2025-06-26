from pydantic import BaseModel
from datetime import date
from typing import Optional
from ..schemas.conductor import ConductorSchema
from ..schemas.vehiculo import VehiculoSchema

class VehiculoConductorSchema(BaseModel):
    id_vehiculo: int
    fecha_inicio: date
    fecha_fin: Optional[date]

    conductor: ConductorSchema
    vehiculo : VehiculoSchema

    class Config:
        orm_mode = True