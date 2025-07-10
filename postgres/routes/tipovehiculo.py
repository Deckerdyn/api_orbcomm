from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import SessionLocal
from ..auth.auth import get_current_user #Importamos para proteccion de rutas
from ..schemas.tipovehiculo import TipoVehiculoSchema, TipoVehiculoCreateSchema, TipoVehiculoUpdateSchema

from ..models import TipoVehiculo
from ..models import Usuario #importamos para proteccion de rutas


router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session
        

#GET
@router.get("/tipovehiculos", response_model=List[TipoVehiculoSchema])
async def get_tipo_vehiculos(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user # Proteccion rutas 
    ):
    result = await db.execute(select(TipoVehiculo))
    tipovehiculos = result.scalars().all()
    return tipovehiculos

#POST
@router.post("/tipovehiculos")
async def create_tipo_vehiculo(
    tipovehiculo: TipoVehiculoCreateSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user # Proteccion rutas 
    ):
    new_tipo_vehiculo = TipoVehiculo(**tipovehiculo.dict())
    db.add(new_tipo_vehiculo)
    await db.commit()
    await db.refresh(new_tipo_vehiculo)
    return {
            "data": new_tipo_vehiculo,
            "res" : True,
            "msg": "TipoVehiculo creado correctamente"
        }

#PUT
@router.put("/tipovehiculos/{id_tipo_vehiculo}")
async def update_tipo_vehiculo(
    id_tipo_vehiculo: int, 
    tipovehiculo: TipoVehiculoUpdateSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user # Proteccion rutas 
    ):
    result = await db.execute(select(TipoVehiculo).where(TipoVehiculo.id_tipo_vehiculo == id_tipo_vehiculo))
    tipovehiculo_db = result.scalars().first()
    if not tipovehiculo_db:
        raise HTTPException(status_code=404, detail="TipoVehiculo no encontrada")

    for key, value in tipovehiculo.dict(exclude_unset=True).items():
        setattr(tipovehiculo_db, key, value)

    await db.commit()
    await db.refresh(tipovehiculo_db)
    return {
            "data": tipovehiculo_db,
            "res" : True,
            "msg": "TipoVehiculo actualizado correctamente"
        }

#DELETE
@router.delete("/tipovehiculos/{id_tipo_vehiculo}")
async def delete_tipo_vehiculo(
    id_tipo_vehiculo: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user # Proteccion rutas 
    ):
    result = await db.execute(select(TipoVehiculo).where(TipoVehiculo.id_tipo_vehiculo == id_tipo_vehiculo))
    tipovehiculo_db = result.scalars().first()
    if not tipovehiculo_db:
        raise HTTPException(status_code=404, detail="TipoVehiculo no encontrada")

    await db.delete(tipovehiculo_db)
    await db.commit()
    return {
            "data": None,
            "res" : True,
            "msg": "TipoVehiculo eliminado"
        }
    
# GET especifico tipovehiculo
@router.get("/tipovehiculos/{id_tipo_vehiculo}")
async def get_tipo_vehiculo(
    id_tipo_vehiculo: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(TipoVehiculo).where(TipoVehiculo.id_tipo_vehiculo == id_tipo_vehiculo))
    tipovehiculo_db = result.scalars().first()
    if not tipovehiculo_db:
        raise HTTPException(status_code=404, detail="TipoVehiculo no encontrado")

    return {
        "data": tipovehiculo_db,
        "res" : True,
        "msg": "TipoVehiculo obtenido correctamente"
    }