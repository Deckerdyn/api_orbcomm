from pydantic import BaseModel

class UbicacionSchema(BaseModel):
    id_ubicacion: int
    nombre: str
    direccion: str
    latitud: float
    longitud: float
    tipo: str

    class Config:
        orm_mode = True