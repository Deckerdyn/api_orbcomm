from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import SessionLocal
from ..schemas.tripconductores import TripConductoresSchema
from ..auth.auth import get_current_user #Importamos para proteccion de rutas

# llamadas al modelo
from ..models import TripConductor
from ..models import Usuario #importamos para proteccion de rutas

router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

#GET
@router.get("/tripconductores", response_model=List[TripConductoresSchema])
async def get_tripconductores(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(TripConductor))
    tripconductores = result.scalars().all()
    return tripconductores

#POST
@router.post("/tripconductores", response_model=TripConductoresSchema)
async def create_tripconductores(
    tripconductores: TripConductoresSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    new_tripconductores = TripConductor(**tripconductores.dict(exclude_unset=True))
    db.add(new_tripconductores)
    await db.commit()
    await db.refresh(new_tripconductores)
    return new_tripconductores

#PUT
@router.put("/tripconductores/{id_tripconductores}", response_model=TripConductoresSchema)
async def update_tripconductores(
    id_tripconductores: int, 
    tripconductores: TripConductoresSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(TripConductor).where(TripConductor.id_tripconductores == id_tripconductores))
    tripconductores_db = result.scalars().first()
    if not tripconductores_db:
        raise HTTPException(status_code=404, detail="TripConductores no encontrada")

    for key, value in tripconductores.dict(exclude_unset=True).items():
        setattr(tripconductores_db, key, value)

    await db.commit()
    await db.refresh(tripconductores_db)
    return tripconductores_db

#DELETE
@router.delete("/tripconductores/{id_tripconductores}")
async def delete_tripconductores(
    id_tripconductores: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(TripConductor).where(TripConductor.id_tripconductores == id_tripconductores))
    tripconductores_db = result.scalars().first()    
    if not tripconductores_db:
        raise HTTPException(status_code=404, detail="TripConductores no encontrada")

    await db.delete(tripconductores_db)
    await db.commit()    
    return {"detail": "TripConductores eliminado"}