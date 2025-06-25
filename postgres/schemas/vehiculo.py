from pydantic import BaseModel
from typing import Optional
from ..schemas.empresa import EmpresaSchema
from ..schemas.dispositivogps import DispositivoGPSSchema

class VehiculoCreateSchema(BaseModel):
    placa: str
    modelo: str
    anio: int
    capacidad_kg: int
    estado: str
    id_empresa: int
    id_dispositivo: Optional[int] = None
    
class VehiculoUpdateSchema(BaseModel):
    placa: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    capacidad_kg: Optional[int] = None
    estado: Optional[str] = None
    id_empresa: Optional[int] = None
    id_dispositivo: Optional[int] = None
    
class VehiculoSchema(VehiculoCreateSchema):
    id_vehiculo: int
    empresa: EmpresaSchema
    dispositivo: Optional[DispositivoGPSSchema] = None

    class Config:
        from_attributes = True