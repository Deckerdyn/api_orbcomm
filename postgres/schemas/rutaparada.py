from pydantic import BaseModel
from ..schemas.paradasautorizadas import ParadasAutorizadasSchema
from ..schemas.ruta import RutaSchema

class RutaParadaSchema(BaseModel):
    orden: int

    ruta: RutaSchema
    parada: ParadasAutorizadasSchema

    class Config:
        orm_mode = True