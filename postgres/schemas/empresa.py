from pydantic import BaseModel
from datetime import datetime
from pydantic import EmailStr

class EmpresaSchema(BaseModel):
    id_empresa: int
    nombre: str
    direccion: str
    telefono_contacto: str
    email: EmailStr
    fecha_registro: datetime
    estado: str

    class Config:
        from_attributes = True