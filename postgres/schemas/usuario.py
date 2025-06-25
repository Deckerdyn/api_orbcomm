from pydantic import BaseModel
from datetime import datetime
from pydantic import EmailStr

class UsuarioSchema(BaseModel):
    id_usuario: int
    nombre: str
    apellido: str
    email: EmailStr
    password_hash: str
    fecha_registro: datetime
    # rol: RolEnum
    estado: str

    class Config:
        from_attributes = True