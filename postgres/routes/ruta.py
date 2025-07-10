from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import SessionLocal
from ..schemas.ruta import RutaSchema, RutaCreateSchema, RutaUpdateSchema
from ..auth.auth import get_current_user #Importamos para proteccion de rutas

# llamadas al modelo
from ..models import Ruta
from ..models import Usuario #importamos para proteccion de rutas

router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session


# GET
@router.get("/rutas", response_model=List[RutaSchema])
async def get_rutas(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Ruta))
    rutas = result.scalars().all()
    return rutas

# POST
@router.post("/rutas")
async def create_ruta(
    ruta: RutaCreateSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    new_ruta = Ruta(**ruta.dict(exclude_unset=True))
    db.add(new_ruta)
    await db.commit()
    await db.refresh(new_ruta)
    return {
        "data": new_ruta,
        "res" : True,
        "msg": "Ruta creada correctamente"
    }

# PUT
@router.put("/rutas/{id_ruta}")
async def update_ruta(
    id_ruta: int, 
    ruta: RutaUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Ruta).where(Ruta.id_ruta == id_ruta))
    ruta_db = result.scalars().first()
    if not ruta_db:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")

    for key, value in ruta.dict(exclude_unset=True).items():
        setattr(ruta_db, key, value)

    await db.commit()
    await db.refresh(ruta_db)
    return {
        "data": ruta_db,
        "res" : True,
        "msg": "Ruta actualizada correctamente"
    }

# DELETE
@router.delete("/rutas/{id_ruta}")
async def delete_ruta(
    id_ruta: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Ruta).where(Ruta.id_ruta == id_ruta))
    ruta_db = result.scalars().first()
    if not ruta_db:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")

    await db.delete(ruta_db)
    await db.commit()
    return {
            "data": None,
            "res" : True,
            "msg": "Ruta eliminada correctamente"
        }
    
# GET especifico ruta
@router.get("/rutas/{id_ruta}")
async def get_ruta(
    id_ruta: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Ruta).where(Ruta.id_ruta == id_ruta))
    ruta_db = result.scalars().first()
    if not ruta_db:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")

    return {
        "data": ruta_db,
        "res" : True,
        "msg": "Ruta obtenida correctamente"
    }