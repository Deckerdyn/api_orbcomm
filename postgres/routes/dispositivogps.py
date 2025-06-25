from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import SessionLocal
from ..schemas.dispositivogps import DispositivoGPSSchema, DispositivoGPSCreateSchema
from ..auth.auth import get_current_user #Importamos para proteccion de rutas

# llamadas al modelo
from ..models import DispositivoGPS
from ..models import Usuario #importamos para proteccion de rutas

router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

#GET
@router.get("/dispositivogps", response_model=List[DispositivoGPSSchema])
async def get_dispositivogps(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user # Proteccion rutas
    ):
    result = await db.execute(select(DispositivoGPS))
    dispositivogps = result.scalars().all()
    return dispositivogps

#POST
@router.post("/dispositivogps", response_model=DispositivoGPSSchema)
async def create_dispositivogps(
    dispositivogps: DispositivoGPSCreateSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user # Proteccion rutas 
    ):
    new_dispositivogps = DispositivoGPS(**dispositivogps.dict())
    db.add(new_dispositivogps)
    await db.commit()    
    await db.refresh(new_dispositivogps)
    return new_dispositivogps

#PUT
@router.put("/dispositivogps/{id_dispositivo}", response_model=DispositivoGPSSchema)
async def update_dispositivogps(
    id_dispositivo: int, 
    dispositivogps: DispositivoGPSSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user # Proteccion rutas 
    ):
    result = await db.execute(select(DispositivoGPS).where(DispositivoGPS.id_dispositivo == id_dispositivo))
    dispositivogps_db = result.scalars().first()
    if not dispositivogps_db:
        raise HTTPException(status_code=404, detail="DispositivoGPS no encontrada")

    for key, value in dispositivogps.dict(exclude_unset=True).items():
        setattr(dispositivogps_db, key, value)

    await db.commit()
    await db.refresh(dispositivogps_db)
    return dispositivogps_db

#DELETE
@router.delete("/dispositivogps/{id_dispositivo}")
async def delete_dispositivogps(
    id_dispositivo: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user # Proteccion rutas 
    ):
    result = await db.execute(select(DispositivoGPS).where(DispositivoGPS.id_dispositivo == id_dispositivo))
    dispositivogps_db = result.scalars().first()
    if not dispositivogps_db:
        raise HTTPException(status_code=404, detail="DispositivoGPS no encontrada")

    await db.delete(dispositivogps_db)
    await db.commit()
    return {"detail": "DispositivoGPS eliminado"}