from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import SessionLocal
from sqlalchemy.future import select
from typing import List
from ..schemas.vehiculo import VehiculoSchema, VehiculoCreateSchema, VehiculoUpdateSchema
from ..auth.auth import get_current_user #Importamos para proteccion de rutas
import httpx

# llamadas al modelo
from ..models.vehiculo import Vehiculo
from ..models import Usuario #importamos para proteccion de rutas

router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

#GET
@router.get("/vehiculos", response_model=List[VehiculoSchema])
async def get_vehiculos(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Vehiculo))
    vehiculo = result.scalars().all()
    return vehiculo

#POST
@router.post("/vehiculos")
async def create_conductor(
    vehiculo: VehiculoCreateSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    nuevo_vehiculo = Vehiculo(**vehiculo.dict())
    db.add(nuevo_vehiculo)
    await db.commit()
    await db.refresh(nuevo_vehiculo)
    return {"msg": "Vehiculo creado correctamente"}

#PUT
@router.put("/vehiculos/{id_vehiculo}")
async def update_vehiculo(
    id_vehiculo: int, 
    vehiculo: VehiculoUpdateSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Vehiculo).where(Vehiculo.id_vehiculo == id_vehiculo))
    vehiculo_db = result.scalars().first()
    if not vehiculo_db:
        raise HTTPException(status_code=404, detail="Vehiculo no encontrada")

    for key, value in vehiculo.dict(exclude_unset=True).items():
        setattr(vehiculo_db, key, value)

    await db.commit()
    await db.refresh(vehiculo_db)
    return {"msg": "Vehiculo actualizado correctamente"}

#DELETE
@router.delete("/vehiculos/{id_vehiculo}")
async def delete_vehiculo(
    id_vehiculo: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Vehiculo).where(Vehiculo.id_vehiculo == id_vehiculo))
    vehiculo_db = result.scalars().first()
    if not vehiculo_db:
        raise HTTPException(status_code=404, detail="Vehiculo no encontrada")

    await db.delete(vehiculo_db)
    await db.commit()
    return {"detail": "Vehiculo eliminado"}


# GET Especifico vehiculo
@router.get("/vehiculos/{id_vehiculo}", response_model=VehiculoSchema)
async def get_vehiculo(
    id_vehiculo: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Vehiculo).where(Vehiculo.id_vehiculo == id_vehiculo))
    vehiculo_db = result.scalars().first()
    
    if not vehiculo_db:
        raise HTTPException(status_code=404, detail="Vehiculo no encontrado")
    
    vehiculo_schema = VehiculoSchema.from_orm(vehiculo_db)

    if vehiculo_schema.dispositivo and vehiculo_schema.dispositivo.numero_serie:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://10.30.7.14:8000/positions/last/" + vehiculo_schema.dispositivo.numero_serie
            )
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list) and data and "positionStatus" in data[0]:
                vehiculo_schema.dispositivo.posicion_gps = {
                    "latitud": data[0]["positionStatus"]["latitude"],
                    "longitud": data[0]["positionStatus"]["longitude"]
                }


    return vehiculo_schema
