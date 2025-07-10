from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TipoVehiculoCreateSchema(BaseModel):
    nombre: str
    
class TipoVehiculoUpdateSchema(BaseModel):
    nombre: str

class TipoVehiculoSchema(TipoVehiculoCreateSchema):
    id_tipo_vehiculo: int

    class Config:
        from_attributes = True