from pydantic import BaseModel
from datetime import date
from typing import Optional
from .tipodispositivogps import TipoDispositivoGPSSchema

class DispositivoGPSCreateSchema(BaseModel):
    proveedor: str
    numero_serie: str
    fecha_instalacion: date
    estado: str
    modelo_dispositivo: str
    id_tipodispositivo: int
    
class DispositivoGPSUpdateSchema(BaseModel):
    proveedor: Optional[str] = None
    numero_serie: Optional[str] = None
    fecha_instalacion: Optional[date] = None
    estado: Optional[str] = None
    modelo_dispositivo: Optional[str] = None
    id_tipodispositivo: Optional[int] = None

class DispositivoGPSSchema(DispositivoGPSCreateSchema):
    id_dispositivo: int
    tipo_dispositivo: TipoDispositivoGPSSchema

    class Config:
        from_attributes = True