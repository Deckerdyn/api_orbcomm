from pydantic import BaseModel
from ..schemas.tramo import TramoSchema
from ..schemas.ruta import RutaSchema

class RutaTramoSchema(BaseModel):
    
    ruta: RutaSchema
    tramo : TramoSchema

    class Config:
        orm_mode = True