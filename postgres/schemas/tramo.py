from pydantic import BaseModel
from ..schemas.ubicacion import UbicacionSchema

class TramoSchema(BaseModel):
    id_tramo: int
    distancia_km: float
    tiempo_estimado_min: int
    descripcion: str
    estado: str

    origen: UbicacionSchema
    destino: UbicacionSchema

    class Config:
        from_attributes = True