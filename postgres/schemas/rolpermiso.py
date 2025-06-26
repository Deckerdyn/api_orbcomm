from pydantic import BaseModel
from ..schemas.permiso import PermisoSchema
from ..schemas.rol import RolSchema

class RolPermisoSchema(BaseModel):
    rol : RolSchema
    permiso : PermisoSchema

    class Config:
        orm_mode = True