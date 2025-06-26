from pydantic import BaseModel
from datetime import date
from typing import Optional
from ..schemas.usuario import UsuarioSchema
from ..schemas.empresa import EmpresaSchema

class ConductorCreateSchema(BaseModel):
    licencia_numero: str
    fecha_expiracion: date
    telefono_contacto: str
    fecha_contratacion: date
    estado: str
    id_usuario: int
    id_empresa: int
    
class ConductorUpdateSchema(BaseModel):
    licencia_numero: Optional[str] = None
    fecha_expiracion: Optional[date] = None
    telefono_contacto: Optional[str] = None
    fecha_contratacion: Optional[date] = None
    estado: Optional[str] = None
    id_usuario: Optional[int] = None
    id_empresa: Optional[int] = None
    
class ConductorSchema(ConductorCreateSchema):
    id_conductor: int
    
    usuario: Optional[UsuarioSchema] = None
    empresa: EmpresaSchema

    class Config:
        from_attributes = True