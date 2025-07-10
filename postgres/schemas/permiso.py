from pydantic import BaseModel
from typing import Optional

class PermisoCreateSchema(BaseModel):
    nombre: str 
    descripcion: str

class PermisoUpdateSchema(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

class PermisoSchema(PermisoCreateSchema):
    id_permiso: int

    class Config:
        orm_mode = True