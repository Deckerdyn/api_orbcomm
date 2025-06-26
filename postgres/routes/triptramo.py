from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import SessionLocal
from ..schemas.triptramo import TripTramoSchema
from ..auth.auth import get_current_user #Importamos para proteccion de rutas

# llamadas al modelo
from ..models import TripTramo
from ..models import Usuario #importamos para proteccion de rutas

router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

#GET
@router.get("/triptramos", response_model=List[TripTramoSchema])
async def get_triptramos(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(TripTramo))
    triptramos = result.scalars().all()
    return triptramos

#POST
@router.post("/triptramos", response_model=TripTramoSchema)
async def create_triptramos(
    triptramo: TripTramoSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    new_triptramo = TripTramo(**triptramo.dict(exclude_unset=True))
    db.add(new_triptramo)
    await db.commit()
    await db.refresh(new_triptramo)
    return new_triptramo

#PUT
@router.put("/triptramos/{id_triptramo}", response_model=TripTramoSchema)
async def update_triptramos(
    id_triptramo: int, 
    triptramo: TripTramoSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(TripTramo).where(TripTramo.id_triptramo == id_triptramo))
    triptramo_db = result.scalars().first()
    if not triptramo_db:
        raise HTTPException(status_code=404, detail="TripTramo no encontrada")

    for key, value in triptramo.dict(exclude_unset=True).items():        
        setattr(triptramo_db, key, value)

    await db.commit()
    await db.refresh(triptramo_db)
    return triptramo_db

#DELETE
@router.delete("/triptramos/{id_triptramo}")
async def delete_triptramos(
    id_triptramo: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(TripTramo).where(TripTramo.id_triptramo == id_triptramo))
    triptramo_db = result.scalars().first()    
    if not triptramo_db:
        raise HTTPException(status_code=404, detail="TripTramo no encontrada")

    await db.delete(triptramo_db)
    await db.commit()    
    return {"detail": "TripTramo eliminado"}