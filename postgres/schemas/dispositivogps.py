from pydantic import BaseModel
from datetime import date
from .tipodispositivogps import TipoDispositivoGPSSchema

class DispositivoGPSCreateSchema(BaseModel):
    proveedor: str
    numero_serie: str
    fecha_instalacion: date
    estado: str
    

class DispositivoGPSSchema(DispositivoGPSCreateSchema):
    id_dispositivo: int
    tipo_dispositivo: TipoDispositivoGPSSchema

    class Config:
        from_attributes = True