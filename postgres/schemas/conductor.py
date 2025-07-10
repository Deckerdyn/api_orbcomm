from pydantic import BaseModel, validator
from datetime import datetime, date
from typing import Optional
from ..schemas.usuario import UsuarioSchema
from ..schemas.empresa import EmpresaSchema

class ConductorCreateSchema(BaseModel):
    licencia_numero: str
    fecha_expiracion: datetime
    telefono_contacto: str
    fecha_contratacion: datetime
    estado: str
    id_usuario: int
    id_empresa: int
    
    @validator(
        "fecha_expiracion",
        "fecha_contratacion",
        pre=True
    )
    
    def strip_tz(cls, value):
        if isinstance(value, str):
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))

        # Si es un date (sin hora), lo convertimos a datetime
        if isinstance(value, date) and not isinstance(value, datetime):
            value = datetime.combine(value, datetime.min.time())

        if isinstance(value, datetime) and value.tzinfo:
            return value.astimezone(tz=None).replace(tzinfo=None)
        return value
    
class ConductorUpdateSchema(BaseModel):
    licencia_numero: Optional[str] = None
    fecha_expiracion: Optional[datetime] = None
    telefono_contacto: Optional[str] = None
    fecha_contratacion: Optional[datetime] = None
    estado: Optional[str] = None
    id_usuario: Optional[int] = None
    id_empresa: Optional[int] = None
    
class ConductorSchema(ConductorCreateSchema):
    id_conductor: int
    
    usuario: Optional[UsuarioSchema] = None
    empresa: EmpresaSchema

    class Config:
        from_attributes = True