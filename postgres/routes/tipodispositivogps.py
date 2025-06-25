from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import SessionLocal
from ..schemas.tipodispositivogps import TipoDispositivoGPSSchema, TipoDispositivoGPSCreateSchema
from ..auth.auth import get_current_user #Importamos para proteccion de rutas

# llamadas al modelo
from ..models import TipoDispositivoGPS
from ..models import Usuario #importamos para proteccion de rutas

router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

#GET
@router.get("/tipodispositivogps", response_model=List[TipoDispositivoGPSSchema])
async def get_tipodispositivogps(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user # Proteccion rutas
    ):
    result = await db.execute(select(TipoDispositivoGPS))
    tipodispositivogps = result.scalars().all()
    return tipodispositivogps

#POST
@router.post("/tipodispositivogps", response_model=TipoDispositivoGPSSchema)
async def create_tipodispositivogps(
    tipodispositivogps: TipoDispositivoGPSCreateSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user # Proteccion rutas 
    ):
    new_tipodispositivogps = TipoDispositivoGPS(**tipodispositivogps.dict())
    db.add(new_tipodispositivogps)
    await db.commit()    
    await db.refresh(new_tipodispositivogps)
    return new_tipodispositivogps

#PUT
@router.put("/tipodispositivogps/{id_tipodispositivo}", response_model=TipoDispositivoGPSSchema)
async def update_tipodispositivogps(
    id_tipodispositivo: int, 
    tipodispositivogps: TipoDispositivoGPSSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user # Proteccion rutas 
    ):
    result = await db.execute(select(TipoDispositivoGPS).where(TipoDispositivoGPS.id_tipodispositivo == id_tipodispositivo))
    tipodispositivogps_db = result.scalars().first()
    if not tipodispositivogps_db:
        raise HTTPException(status_code=404, detail="TipoDispositivoGPS no encontrada")

    for key, value in tipodispositivogps.dict(exclude_unset=True).items():
        setattr(tipodispositivogps_db, key, value)

    await db.commit()
    await db.refresh(tipodispositivogps_db)
    return tipodispositivogps_db

#DELETE
@router.delete("/tipodispositivogps/{id_tipodispositivo}")
async def delete_tipodispositivogps(
    id_tipodispositivo: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user # Proteccion rutas 
    ):
    result = await db.execute(select(TipoDispositivoGPS).where(TipoDispositivoGPS.id_tipodispositivo == id_tipodispositivo))
    tipodispositivogps_db = result.scalars().first()
    if not tipodispositivogps_db:
        raise HTTPException(status_code=404, detail="TipoDispositivoGPS no encontrada")

    await db.delete(tipodispositivogps_db)
    await db.commit()
    return {"detail": "TipoDispositivoGPS eliminado"}