from pydantic import BaseModel
from datetime import date
from ..schemas.usuario import UsuarioSchema
from ..schemas.empresa import EmpresaSchema

class ConductorSchema(BaseModel):
    id_conductor: int
    licencia_numero: str
    fecha_expiracion: date
    telefono_contacto: str
    fecha_contratacion: date
    estado: str

    usuario: UsuarioSchema
    empresa: EmpresaSchema

    class Config:
        from_attributes = True