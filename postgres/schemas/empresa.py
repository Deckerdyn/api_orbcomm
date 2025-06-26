from pydantic import BaseModel
from datetime import datetime
from pydantic import EmailStr
from typing import Optional

class EmpresaCreateSchema(BaseModel):
    nombre: str
    direccion: str
    telefono_contacto: str
    email: EmailStr
    fecha_registro: datetime
    estado: str

class EmpresaUpdateSchema(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    telefono_contacto: Optional[str] = None
    email: Optional[EmailStr] = None
    fecha_registro: Optional[datetime] = None
    estado: Optional[str] = None
    
class EmpresaSchema(EmpresaCreateSchema):
    id_empresa: int
    
    class Config:
        from_attributes = True