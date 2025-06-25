from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import SessionLocal
from sqlalchemy.future import select
from typing import List
from ..schemas.conductor import ConductorSchema
from ..auth.auth import get_current_user #Importamos para proteccion de rutas


# llamadas al modelo
from ..models import Conductor
from ..models import Usuario #importamos para proteccion de rutas

router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

#GET
@router.get("/conductores", response_model=List[ConductorSchema])
async def get_conductores(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user # Proteccion rutas 
    ):
    result = await db.execute(select(Conductor))
    conductores = result.scalars().all()
    return conductores

#POST
@router.post("/conductores")
async def create_conductor(
    conductor: ConductorSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user # Proteccion rutas 
    ):
    nuevo = Conductor(**conductor.dict())
    db.add(nuevo)
    await db.commit()
    return {"msg": "Conductor creado correctamente"}

#PUT
@router.put("/conductores/{id_conductor}", response_model=ConductorSchema)
async def update_conductor(
    id_conductor: int, 
    conductor: ConductorSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user # Proteccion rutas 
    ):
    result = await db.execute(select(Conductor).where(Conductor.id_conductor == id_conductor))
    conductor_db = result.scalars().first()
    if not conductor_db:
        raise HTTPException(status_code=404, detail="Conductor no encontrada")

    for key, value in conductor.dict(exclude_unset=True).items():
        setattr(conductor_db, key, value)

    await db.commit()
    await db.refresh(conductor_db)
    return conductor_db

#DELETE
@router.delete("/conductores/{id_conductor}")
async def delete_conductor(
    id_conductor: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user # Proteccion rutas 
    ):
    result = await db.execute(select(Conductor).where(Conductor.id_conductor == id_conductor))
    conductor_db = result.scalars().first()
    if not conductor_db:
        raise HTTPException(status_code=404, detail="Conductor no encontrada")

    await db.delete(conductor_db)
    await db.commit()
    return {"detail": "Conductor eliminado"}