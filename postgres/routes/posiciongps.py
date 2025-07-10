from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import SessionLocal
from ..schemas.posiciongps import PosicionGPSSchema, PosicionGPSCreateSchema, PosicionGPSUpdateSchema
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
@router.post("/posiciongps")
async def create_posiciongps(
    posiciongps: PosicionGPSCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    new_posiciongps = PosicionGPS(**posiciongps.dict())
    db.add(new_posiciongps)
    await db.commit()    
    return {
            "data": new_posiciongps,
            "res" : True,
            "msg": "PosicionGPS creado correctamente"
        }

#PUT
@router.put("/posiciongps/{id_posiciongps}")
async def update_posiciongps(
    id_posiciongps: int, 
    posiciongps: PosicionGPSUpdateSchema, 
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
    return {
            "data": posiciongps_db,
            "res" : True,
            "msg": "PosicionGPS actualizado correctamente"
        }

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
    return {
            "data": None,
            "res" : True,
            "msg": "PosicionGPS eliminado"
        }

# GET especifico posiciongps
@router.get("/posiciongps/{id_posiciongps}")
async def get_posiciongps(
    id_posiciongps: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(PosicionGPS).where(PosicionGPS.id_registro == id_posiciongps))
    posiciongps_db = result.scalars().first()
    if not posiciongps_db:
        raise HTTPException(status_code=404, detail="PosicionGPS no encontrado")

    return {
        "data": posiciongps_db,
        "res" : True,
        "msg": "PosicionGPS obtenido correctamente"
    }
