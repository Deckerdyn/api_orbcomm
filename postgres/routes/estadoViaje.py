from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import SessionLocal
from ..schemas.estadoViaje import EstadoViajeSchema
from ..auth.auth import get_current_user #Importamos para proteccion de rutas

# llamadas al modelo
from ..models import EstadoViaje
from ..models import Usuario #importamos para proteccion de rutas

router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session


@router.get("/estadoViajes", response_model=List[EstadoViajeSchema])
async def get_estadoViajes(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(EstadoViaje))
    estadoViajes = result.scalars().all()
    return estadoViajes

@router.post("/estadoViajes", response_model=EstadoViajeSchema)
async def create_estadoViaje(
    estadoViaje: EstadoViajeSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    new_estadoViaje = EstadoViaje(**estadoViaje.dict(exclude_unset=True))
    db.add(new_estadoViaje)
    await db.commit()
    await db.refresh(new_estadoViaje)
    return new_estadoViaje

@router.put("/estadoViajes/{id_estado}", response_model=EstadoViajeSchema)
async def update_estadoViaje(
    id_estado: int, 
    estadoViaje: EstadoViajeSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(EstadoViaje).where(EstadoViaje.id_estado == id_estado))
    estadoViaje_db = result.scalars().first()
    if not estadoViaje_db:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    for key, value in estadoViaje.dict(exclude_unset=True).items():
        setattr(estadoViaje_db, key, value)

    await db.commit()
    await db.refresh(estadoViaje_db)
    return estadoViaje_db

@router.delete("/estadoViajes/{id_estado}")
async def delete_estadoViaje(
    id_estado: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(EstadoViaje).where(EstadoViaje.id_estado == id_estado))
    estadoViaje_db = result.scalars().first()
    if not estadoViaje_db:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    await db.delete(estadoViaje_db)
    await db.commit()
    return {"detail": "Empresa eliminada"}

