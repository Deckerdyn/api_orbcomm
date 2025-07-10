from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import SessionLocal
from ..schemas.ubicacion import UbicacionSchema, UbicacionCreateSchema, UbicacionUpdateSchema
from ..auth.auth import get_current_user #Importamos para proteccion de rutas

# llamadas al modelo
from ..models import Ubicacion
from ..models import Usuario #importamos para proteccion de rutas

router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

# GET
@router.get("/ubicacion", response_model=List[UbicacionSchema])
async def get_ubicacion(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Ubicacion))
    ubicaciaones = result.scalars().all()
    return ubicaciaones

# POST
@router.post("/ubicacion")
async def create_ubicacion(
    ubicacion: UbicacionCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    new_ubicacion = Ubicacion(**ubicacion.dict(exclude_unset=True))
    db.add(new_ubicacion)
    await db.commit()
    await db.refresh(new_ubicacion)
    return {
        "data": new_ubicacion,
        "res" : True,
        "msg": "Ubicacion creada correctamente"
    }

# PUT
@router.put("/ubicacion/{id_ubicacion}")
async def update_ubicacion(
    id_ubicacion: int, 
    ubicacion: UbicacionUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Ubicacion).where(Ubicacion.id_ubicacion == id_ubicacion))
    ubicacion_db = result.scalars().first()
    if not ubicacion_db:
        raise HTTPException(status_code=404, detail="Ubicacion no encontrada")

    for key, value in ubicacion.dict(exclude_unset=True).items():
        setattr(ubicacion_db, key, value)

    await db.commit()
    await db.refresh(ubicacion_db)
    return {
        "data": ubicacion_db,
        "res" : True,
        "msg": "Ubicacion actualizada correctamente"
    }

# DELETE
@router.delete("/ubicacion/{id_ubicacion}")
async def delete_ubicacion(
    id_ubicacion: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Ubicacion).where(Ubicacion.id_ubicacion == id_ubicacion))
    ubicacion_db = result.scalars().first()
    if not ubicacion_db:
        raise HTTPException(status_code=404, detail="Ubicacion no encontrada")

    await db.delete(ubicacion_db)
    await db.commit()
    return {
            "data": None,
            "res" : True,
            "msg": "Ubicacion eliminada"
        }

# GET especifico ubicacion
@router.get("/ubicacion/{id_ubicacion}")
async def get_ubicacion(
    id_ubicacion: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Ubicacion).where(Ubicacion.id_ubicacion == id_ubicacion))
    ubicacion_db = result.scalars().first()
    if not ubicacion_db:
        raise HTTPException(status_code=404, detail="Ubicacion no encontrada")

    return {
        "data": ubicacion_db,
        "res" : True,
        "msg": "Ubicacion obtenida correctamente"
    }