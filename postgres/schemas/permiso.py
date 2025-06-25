from pydantic import BaseModel

class PermisoSchema(BaseModel):
    id_permiso: int
    nombre: str 
    descripcion: str

    class Config:
        orm_mode = True