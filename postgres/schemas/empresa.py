from pydantic import BaseModel , validator
from datetime import datetime
from pydantic import EmailStr
from typing import Optional


class EmpresaCreateSchema(BaseModel):
    nombre: str
    direccion: str
    rut: str
    telefono_contacto: str
    email: EmailStr
    fecha_registro: datetime
    estado: str
    
    @validator(
        "fecha_registro",
        pre=True
    )
    
    def strip_tz(cls, value):
        if isinstance(value, str):
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if value and value.tzinfo:
            return value.astimezone(tz=None).replace(tzinfo=None)
        return value

class EmpresaUpdateSchema(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    rut: Optional[str] = None
    telefono_contacto: Optional[str] = None
    email: Optional[EmailStr] = None
    fecha_registro: Optional[datetime] = None
    estado: Optional[str] = None
    
class EmpresaSchema(EmpresaCreateSchema):
    id_empresa: int
    
    class Config:
        from_attributes = True