from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import SessionLocal
from sqlalchemy.future import select
from typing import List
from ..schemas.resumentrip import ResumenTripSchema, ResumenTripCreateSchema, ResumenTripUpdateSchema
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
@router.post("/resumentrip")
async def create_resumen_trip(
    resumen_trip: ResumenTripCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    new_resumen_trip = ResumenTrip(**resumen_trip.dict())
    db.add(new_resumen_trip)
    await db.commit()    
    return {
        "data": new_resumen_trip,
        "res" : True,
        "msg": "ResumenTrip creado correctamente"
    }

#PUT
@router.put("/resumentrip/{id_resumen}")
async def update_resumen_trip(
    id_resumen: int, 
    resumen_trip: ResumenTripUpdateSchema,
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
    return {
            "data": resumen_trip_db,
            "res" : True,
            "msg": "ResumenTrip actualizado correctamente"
        }

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
    return {
        "data": None,
        "res" : True,
        "msg": "ResumenTrip eliminado"
    }

# GET especifico resumentrip
@router.get("/resumentrip/{id_resumen}")
async def get_resumen_trip(
    id_resumen: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(ResumenTrip).where(ResumenTrip.id_resumen == id_resumen))
    resumen_trip_db = result.scalars().first()
    if not resumen_trip_db:
        raise HTTPException(status_code=404, detail="ResumenTrip no encontrado")

    return {
        "data": resumen_trip_db,
        "res" : True,
        "msg": "ResumenTrip obtenido correctamente"
    }