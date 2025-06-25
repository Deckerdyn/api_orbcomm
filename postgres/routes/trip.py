from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import SessionLocal
from sqlalchemy.future import select
from typing import List
from ..schemas.trip import TripSchema
from ..auth.auth import get_current_user #Importamos para proteccion de rutas

# llamadas al modelo
from ..models import Trip
from ..models import Usuario #importamos para proteccion de rutas

router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/trips", response_model=List[TripSchema])
async def get_trips(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Trip))
    trips = result.scalars().all()
    return trips

@router.post("/trips")
async def create_trip(
    trip: TripSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    nuevo = Trip(**trip.dict())
    db.add(nuevo)
    await db.commit()
    return {"msg": "Trip creado correctamente"}

