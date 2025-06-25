from pydantic import BaseModel
from ..schemas.usuario import UsuarioSchema
from ..schemas.rol import RolSchema

class UsuarioRolSchema(BaseModel):
    usuario: UsuarioSchema
    rol: RolSchema

    class Config:
        orm_mode = True