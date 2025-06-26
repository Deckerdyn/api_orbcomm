from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import SessionLocal
from ..schemas.ruta import RutaSchema
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


@router.get("/rutas", response_model=List[RutaSchema])
async def get_rutas(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Ruta))
    rutas = result.scalars().all()
    return rutas

@router.post("/rutas", response_model=RutaSchema)
async def create_ruta(
    ruta: RutaSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    new_ruta = Ruta(**ruta.dict(exclude_unset=True))
    db.add(new_ruta)
    await db.commit()
    await db.refresh(new_ruta)
    return new_ruta

@router.put("/rutas/{id_ruta}", response_model=RutaSchema)
async def update_ruta(
    id_ruta: int, 
    ruta: RutaSchema, 
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
    return ruta_db

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
    return {"detail": "Ruta eliminada"}

