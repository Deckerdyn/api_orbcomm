from pydantic import BaseModel

class EstadoViajeSchema(BaseModel):
    id_estado: int
    nombre: str 
    descripcion: str

    class Config:
        orm_mode = True