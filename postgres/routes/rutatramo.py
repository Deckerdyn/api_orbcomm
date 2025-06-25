from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import SessionLocal
from ..schemas.rutatramo import RutaTramoSchema
from ..auth.auth import get_current_user #Importamos para proteccion de rutas

# llamadas al modelo
from ..models import RutaTramo
from ..models import Usuario #importamos para proteccion de rutas

router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

#GET
@router.get("/rutatramos", response_model=List[RutaTramoSchema])
async def get_rutatramos(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(RutaTramo))
    rutatramos = result.scalars().all()
    return rutatramos

#POST
@router.post("/rutatramos", response_model=RutaTramoSchema)
async def create_rutatramos(
    rutatramo: RutaTramoSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    new_rutatramo = RutaTramo(**rutatramo.dict(exclude_unset=True))
    db.add(new_rutatramo)
    await db.commit()
    await db.refresh(new_rutatramo)
    return new_rutatramo

#PUT
@router.put("/rutatramos/{id_rutatramo}", response_model=RutaTramoSchema)
async def update_rutatramos(
    id_rutatramo: int, 
    rutatramo: RutaTramoSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(RutaTramo).where(RutaTramo.id_rutatramo == id_rutatramo))
    rutatramo_db = result.scalars().first()
    if not rutatramo_db:
        raise HTTPException(status_code=404, detail="RutaTramo no encontrada")

    for key, value in rutatramo.dict(exclude_unset=True).items():        
        setattr(rutatramo_db, key, value)

    await db.commit()
    await db.refresh(rutatramo_db)
    return rutatramo_db

#DELETE
@router.delete("/rutatramos/{id_rutatramo}")
async def delete_rutatramos(
    id_rutatramo: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(RutaTramo).where(RutaTramo.id_rutatramo == id_rutatramo))
    rutatramo_db = result.scalars().first()    
    if not rutatramo_db:
        raise HTTPException(status_code=404, detail="RutaTramo no encontrada")

    await db.delete(rutatramo_db)
    await db.commit()
    return {"detail": "RutaTramo eliminado"}