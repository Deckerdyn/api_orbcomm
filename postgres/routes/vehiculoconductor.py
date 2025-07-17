from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import SessionLocal
from ..schemas.vehiculoconductor import VehiculoConductorSchema, VehiculoConductorCreateSchema
from ..auth.auth import get_current_user #Importamos para proteccion de rutas

# llamadas al modelo
from ..models import VehiculoConductor
from ..models import Usuario #importamos para proteccion de rutas

router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

#GET
@router.get("/vehiculoconductores", response_model=List[VehiculoConductorSchema])
async def get_vehiculoconductores(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(VehiculoConductor))
    vehiculoconductores = result.scalars().all()
    return vehiculoconductores

#POST
@router.post("/vehiculoconductores")
async def create_vehiculoconductores(
    vehiculoconductores: VehiculoConductorCreateSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    new_vehiculoconductores = VehiculoConductor(**vehiculoconductores.dict(exclude_unset=True))
    db.add(new_vehiculoconductores)
    await db.commit()
    await db.refresh(new_vehiculoconductores)
    return {
            "data": new_vehiculoconductores,
            "res" : True,
            "msg": "VehiculoConductor creado correctamente"
        }

#PUT
@router.put("/vehiculoconductores/{id_vehiculoconductores}", response_model=VehiculoConductorSchema)
async def update_vehiculoconductores(
    id_vehiculoconductores: int, 
    vehiculoconductores: VehiculoConductorSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(VehiculoConductor).where(VehiculoConductor.id_vehiculoconductores == id_vehiculoconductores))
    vehiculoconductores_db = result.scalars().first()
    if not vehiculoconductores_db:
        raise HTTPException(status_code=404, detail="VehiculoConductores no encontrada")

    for key, value in vehiculoconductores.dict(exclude_unset=True).items():
        setattr(vehiculoconductores_db, key, value)

    await db.commit()
    await db.refresh(vehiculoconductores_db)
    return vehiculoconductores_db

#DELETE
@router.delete("/vehiculoconductores/{id_vehiculoconductores}")
async def delete_vehiculoconductores(
    id_vehiculoconductores: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(VehiculoConductor).where(VehiculoConductor.id_vehiculoconductores == id_vehiculoconductores))
    vehiculoconductores_db = result.scalars().first()    
    if not vehiculoconductores_db:
        raise HTTPException(status_code=404, detail="VehiculoConductores no encontrada")

    await db.delete(vehiculoconductores_db)
    await db.commit()    
    return {"detail": "VehiculoConductores eliminado"}