from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import SessionLocal
from ..schemas.posiciongps import PosicionGPSSchema
from ..auth.auth import get_current_user #Importamos para proteccion de rutas

# llamadas al modelo
from ..models import PosicionGPS
from ..models import Usuario #importamos para proteccion de rutas

router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

#GET
@router.get("/posiciongps", response_model=List[PosicionGPSSchema])
async def get_posiciongps(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(PosicionGPS))
    posiciongps = result.scalars().all()
    return posiciongps

#POST
@router.post("/posiciongps", response_model=PosicionGPSSchema)
async def create_posiciongps(
    posiciongps: PosicionGPSSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    new_posiciongps = PosicionGPS(**posiciongps.dict())
    db.add(new_posiciongps)
    await db.commit()    
    return new_posiciongps

#PUT
@router.put("/posiciongps/{id_posiciongps}", response_model=PosicionGPSSchema)
async def update_posiciongps(
    id_posiciongps: int, 
    posiciongps: PosicionGPSSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(PosicionGPS).where(PosicionGPS.id_registro == id_posiciongps))
    posiciongps_db = result.scalars().first()
    if not posiciongps_db:
        raise HTTPException(status_code=404, detail="PosicionGPS no encontrada")

    for key, value in posiciongps.dict(exclude_unset=True).items():
        setattr(posiciongps_db, key, value)

    await db.commit()
    await db.refresh(posiciongps_db)
    return posiciongps_db

#DELETE
@router.delete("/posiciongps/{id_posiciongps}")
async def delete_posiciongps(
    id_posiciongps: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(PosicionGPS).where(PosicionGPS.id_registro == id_posiciongps))
    posiciongps_db = result.scalars().first()
    if not posiciongps_db:
        raise HTTPException(status_code=404, detail="PosicionGPS no encontrada")

    await db.delete(posiciongps_db)
    await db.commit()
    return {"detail": "PosicionGPS eliminado"}
