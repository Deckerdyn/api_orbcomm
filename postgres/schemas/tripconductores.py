from pydantic import BaseModel
from ..schemas.conductor import ConductorSchema
from ..schemas.trip import TripSchema

class TripConductoresSchema(BaseModel):
    trip: TripSchema
    conductor : ConductorSchema

    class Config:
        orm_mode = True
