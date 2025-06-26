from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import SessionLocal
from ..schemas.rutaparada import RutaParadaSchema
from sqlalchemy.orm import joinedload
from ..auth.auth import get_current_user #Importamos para proteccion de rutas

# llamadas al modelo
from ..models import RutaParada
from ..models import Usuario #importamos para proteccion de rutas

router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session
    
#GET
@router.get("/rutaparadas", response_model=List[RutaParadaSchema])
async def get_rutaparadas(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(RutaParada).options(joinedload(RutaParada.parada)))
    rutasParadas = result.scalars().all()
    return rutasParadas

#POST
@router.post("/rutaparadas", response_model=RutaParadaSchema)
async def create_rutaparadas(
    rutaparadas: RutaParadaSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    new_rutaparadas = RutaParada(**rutaparadas.dict())
    db.add(new_rutaparadas)
    await db.commit()
    await db.refresh(new_rutaparadas)
    return new_rutaparadas

#PUT
@router.put("/rutaparadas/{id_rutaparadas}", response_model=RutaParadaSchema)
async def update_rutaparadas(
    id_rutaparadas: int, 
    rutaparadas: RutaParadaSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(RutaParada).where(RutaParada.id_rutaparadas == id_rutaparadas))
    rutaparadas_db = result.scalars().first()
    if not rutaparadas_db:
        raise HTTPException(status_code=404, detail="RutaParada no encontrada")

    for key, value in rutaparadas.dict(exclude_unset=True).items():
        setattr(rutaparadas_db, key, value)

    await db.commit()
    await db.refresh(rutaparadas_db)
    return rutaparadas_db

#DELETE
@router.delete("/rutaparadas/{id_rutaparadas}")
async def delete_rutaparadas(
    id_rutaparadas: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(RutaParada).where(RutaParada.id_rutaparadas == id_rutaparadas))
    rutaparadas_db = result.scalars().first()
    if not rutaparadas_db:
        raise HTTPException(status_code=404, detail="RutaParada no encontrada")

    await db.delete(rutaparadas_db)
    await db.commit()  
    return {"detail": "RutaParada eliminado"}