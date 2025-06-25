from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import SessionLocal
from sqlalchemy.future import select
from typing import List
from ..schemas.resumentrip import ResumenTripSchema
from ..auth.auth import get_current_user #Importamos para proteccion de rutas

# llamadas al modelo
from ..models import ResumenTrip
from ..models import Usuario #importamos para proteccion de rutas

router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

#GET
@router.get("/resumentrip", response_model=List[ResumenTripSchema])
async def get_resumen_trip(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(ResumenTrip))
    resumen_trip = result.scalars().all()
    return resumen_trip

#POST
@router.post("/resumentrip", response_model=ResumenTripSchema)
async def create_resumen_trip(
    resumen_trip: ResumenTripSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    new_resumen_trip = ResumenTrip(**resumen_trip.dict())
    db.add(new_resumen_trip)
    await db.commit()    
    return new_resumen_trip

#PUT
@router.put("/resumentrip/{id_resumen}", response_model=ResumenTripSchema)
async def update_resumen_trip(
    id_resumen: int, 
    resumen_trip: ResumenTripSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(ResumenTrip).where(ResumenTrip.id_resumen == id_resumen))
    resumen_trip_db = result.scalars().first()
    if not resumen_trip_db:
        raise HTTPException(status_code=404, detail="ResumenTrip no encontrada")

    for key, value in resumen_trip.dict(exclude_unset=True).items():
        setattr(resumen_trip_db, key, value)

    await db.commit()
    await db.refresh(resumen_trip_db)
    return resumen_trip_db

#DELETE
@router.delete("/resumentrip/{id_resumen}")
async def delete_resumen_trip(
    id_resumen: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(ResumenTrip).where(ResumenTrip.id_resumen == id_resumen))
    resumen_trip_db = result.scalars().first()
    if not resumen_trip_db:
        raise HTTPException(status_code=404, detail="ResumenTrip no encontrada")

    await db.delete(resumen_trip_db)
    await db.commit()
    return {"detail": "ResumenTrip eliminado"}