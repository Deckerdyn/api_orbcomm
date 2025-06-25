from pydantic import BaseModel
from ..schemas.ubicacion import UbicacionSchema

class RutaSchema(BaseModel):
    id_ruta: int
    nombre: str
    descripcion: str
    estado: str

    origen: UbicacionSchema
    destino: UbicacionSchema

    class Config:
        orm_mode = True