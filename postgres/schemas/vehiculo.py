from pydantic import BaseModel
from ..schemas.empresa import EmpresaSchema
from ..schemas.dispositivogps import DispositivoGPSSchema

class VehiculoSchema(BaseModel):
    id_vehiculo: int
    placa: str
    modelo: str
    anio: int
    capacidad_kg: int
    estado: str

    empresa: EmpresaSchema
    dispositivo: DispositivoGPSSchema

    class Config:
        from_attributes = True