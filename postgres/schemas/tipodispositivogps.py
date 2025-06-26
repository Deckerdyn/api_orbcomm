from pydantic import BaseModel
from datetime import date

class TipoDispositivoGPSCreateSchema(BaseModel):
    nombre: str

class TipoDispositivoGPSSchema(TipoDispositivoGPSCreateSchema):
    id_tipodispositivo: int

    class Config:
        from_attributes = True