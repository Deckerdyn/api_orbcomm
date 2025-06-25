from pydantic import BaseModel

class RolSchema(BaseModel):
    id_rol: int
    nombre: str 
    descripcion: str

    class Config:
        orm_mode = True
