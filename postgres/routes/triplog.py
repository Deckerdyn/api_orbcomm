from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import SessionLocal
from ..auth.auth import get_current_user #Importamos para proteccion de rutas
from ..schemas.triplog import TripLogSchema

from ..models import TripLog
from ..models import Usuario #importamos para proteccion de rutas

router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

# GET Filtrado
@router.get("/tripslogs/filtrado")
async def get_trip_filtrado(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
):
    result = await db.execute(select(TripLog))
    triplogs = result.scalars().all()
    #filtrar
    triplogs_filtrados = []
    for trip in triplogs:
        
        json_trip = {
            "titulo": trip.accion,
            "descripcion": trip.descripcion,
            "categoria": "Viaje",
            "fecha": trip.fecha_log,
            "prioridad": "media"
        }
        
        triplogs_filtrados.append(json_trip)
    
    return triplogs_filtrados

# GET
@router.get("/tripslogs", response_model=List[TripLogSchema])
async def get_triplog(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(TripLog))
    triplogs = result.scalars().all()
    return triplogs

@router.get("/trips/{id_trip}/logs", response_model=List[TripLogSchema])
async def get_trip_logs(
    id_trip: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
):
    result = await db.execute(select(TripLog).where(TripLog.id_trip == id_trip))
    logs = result.scalars().all()
    return logs

