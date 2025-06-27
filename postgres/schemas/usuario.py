from pydantic import BaseModel
from datetime import datetime
from pydantic import EmailStr
from typing import Optional

class UsuarioCreateSchema(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    password_hash: str
    fecha_registro: Optional[datetime] = None
    estado: Optional[str] = None

class UsuarioUpdateSchema(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[EmailStr] = None
    password_hash: Optional[str] = None
    fecha_registro: Optional[datetime] = None
    estado: Optional[str] = None

class UsuarioSchema(UsuarioCreateSchema):
    id_usuario: int

    class Config:
        from_attributes = True