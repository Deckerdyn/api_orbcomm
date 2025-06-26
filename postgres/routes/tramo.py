
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import SessionLocal
from sqlalchemy.future import select
from typing import List
from ..schemas.tramo import TramoSchema
from ..auth.auth import get_current_user #Importamos para proteccion de rutas

# llamadas al modelo
from ..models.tramo import Tramo
from ..models import Usuario #importamos para proteccion de rutas

router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/tramos", response_model=List[TramoSchema])
async def get_tramos(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user):
    result = await db.execute(select(Tramo))
    tramos = result.scalars().all()
    return tramos

@router.post("/tramos")
async def create_tramos(
    tramos: TramoSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    nuevo = Tramo(**tramos.dict())
    db.add(nuevo)
    await db.commit()
    return {"msg": "Tramo creado correctamente"}
