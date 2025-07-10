from pydantic import BaseModel, validator
from typing import Optional
from geoalchemy2.shape import to_shape

class ParadasAutorizadasCreateSchema(BaseModel):
    nombre: str
    categoria: str
    direccion: str
    geom: str | None
    estado: str

    @validator("geom", pre=True)
    def parse_geom(cls, v):
        if v is None:
            return None
        return to_shape(v).wkt

class ParadasAutorizadasUpdateSchema(BaseModel):
    nombre: Optional[str] = None
    categoria: Optional[str] = None
    direccion: Optional[str] = None
    geom: Optional[str] = None
    estado: Optional[str] = None
    
class ParadasAutorizadasSchema(ParadasAutorizadasCreateSchema):
    id_parada: int
    
    class Config:
        orm_mode = True
            