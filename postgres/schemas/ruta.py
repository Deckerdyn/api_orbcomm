from pydantic import BaseModel
from typing import Optional
from ..schemas.ubicacion import UbicacionSchema

class RutaCreateSchema(BaseModel):
    nombre: str
    descripcion: str
    estado: str
    id_origen: int
    id_destino: int
    
class RutaUpdateSchema(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[str] = None
        
class RutaSchema(BaseModel):
    id_ruta: int
    nombre : str
    descripcion : str
    estado : str
    origen : UbicacionSchema
    destino : UbicacionSchema

    class Config:
        orm_mode = True