from pydantic import BaseModel
from pydantic import BaseModel, validator
from geoalchemy2.shape import to_shape

class ParadasAutorizadasSchema(BaseModel):
    id_parada: int
    nombre: str
    categoria: str
    direccion: str
    geom: str | None
    estado: str

    class Config:
        orm_mode = True

    @validator("geom", pre=True)
    def parse_geom(cls, v):
        if v is None:
            return None
        return to_shape(v).wkt