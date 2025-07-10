from pydantic import BaseModel
from typing import Optional

class UbicacionCreateSchema(BaseModel):
    nombre: str
    direccion: str
    latitud: float
    longitud: float
    tipo: str
    
class UbicacionUpdateSchema(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    
class UbicacionSchema(UbicacionCreateSchema):
    id_ubicacion: int

    class Config:
        orm_mode = True