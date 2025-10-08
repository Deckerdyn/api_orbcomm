from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import SessionLocal
from ..schemas.dispositivogps import DispositivoGPSSchema, DispositivoGPSCreateSchema, DispositivoGPSUpdateSchema
from ..auth.auth import get_current_user #Importamos para proteccion de rutas
import httpx
import os


# llamadas al modelo
from ..models import DispositivoGPS
from ..models import Usuario #importamos para proteccion de rutas

router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas
ipServidor = os.getenv("IPSERVIDOR")

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

#GET
@router.get("/dispositivogps", response_model=List[DispositivoGPSSchema])
async def get_dispositivogps(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user # Proteccion rutas
    ):
    result = await db.execute(select(DispositivoGPS))
    dispositivogps = result.scalars().all()
    
    newDispoitivo = []
    for dispositivo in dispositivogps:
        dispositivogps_schema = DispositivoGPSSchema.from_orm(dispositivo)
        
        try:
            async with httpx.AsyncClient() as client:
                if dispositivogps_schema.modelo_dispositivo != "globalmini":
                    response = await client.get(
                        f"{ipServidor}/positions/last/{dispositivogps_schema.numero_serie}"                    
                    )
                    
                    if response.status_code == 200:
                        data = response.json()

                        if (
                            isinstance(data, list) and 
                            len(data) > 0 and 
                            data[0].get("positionStatus")
                        ):
                            dispositivogps_schema.posicion_gps = {
                                "latitud": data[0]["positionStatus"]["latitude"],
                                "longitud": data[0]["positionStatus"]["longitude"]
                            }
                    else:
                        dispositivogps_schema.posicion_gps = None
                else:
                    response = await client.get(
                        f"{ipServidor}/globalMini/ultimaPosicion/" + dispositivogps_schema.numero_serie
                    )
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    if isinstance(data, dict) and "Latitude" and "Longitude" in data:
                        dispositivogps_schema.posicion_gps = {
                            "latitud": data["Latitude"],
                            "longitud": data["Longitude"]
                        }
                
                

                newDispoitivo.append(dispositivogps_schema)
        except httpx.RequestError as e:
            dispositivogps_schema.posicion_gps = None
            newDispoitivo.append(dispositivogps_schema)
            print(f"Error en la solicitud HTTP: {e}")
    return newDispoitivo

#POST
@router.post("/dispositivogps")
async def create_dispositivogps(
    dispositivogps: DispositivoGPSCreateSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user # Proteccion rutas 
    ):
    new_dispositivogps = DispositivoGPS(**dispositivogps.dict())
    db.add(new_dispositivogps)
    await db.commit()    
    await db.refresh(new_dispositivogps)
    return {
            "data": new_dispositivogps,
            "res" : True,
            "msg": "DispositivoGPS creado correctamente"
        }

#PUT
@router.put("/dispositivogps/{id_dispositivo}", response_model=DispositivoGPSSchema)
async def update_dispositivogps(
    id_dispositivo: int, 
    dispositivogps: DispositivoGPSUpdateSchema,  
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(DispositivoGPS).where(DispositivoGPS.id_dispositivo == id_dispositivo))
    dispositivogps_db = result.scalars().first()
    if not dispositivogps_db:
        raise HTTPException(status_code=404, detail="DispositivoGPS no encontrado")

    for key, value in dispositivogps.dict(exclude_unset=True).items():
        setattr(dispositivogps_db, key, value)

    await db.commit()
    await db.refresh(dispositivogps_db)
    return {
            "data": dispositivogps_db,
            "res" : True,
            "msg": "DispositivoGPS actualizado correctamente"
        }

#DELETE
@router.delete("/dispositivogps/{id_dispositivo}")
async def delete_dispositivogps(
    id_dispositivo: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user # Proteccion rutas 
    ):
    result = await db.execute(select(DispositivoGPS).where(DispositivoGPS.id_dispositivo == id_dispositivo))
    dispositivogps_db = result.scalars().first()
    if not dispositivogps_db:
        raise HTTPException(status_code=404, detail="DispositivoGPS no encontrada")

    await db.delete(dispositivogps_db)
    await db.commit()
    return {
            "data": None,
            "res" : True,
            "msg": "DispositivoGPS eliminado"
        }

# GET especifico dispositivogps
@router.get("/dispositivogps/{id_dispositivo}")
async def get_dispositivogps(
    id_dispositivo: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(DispositivoGPS).where(DispositivoGPS.id_dispositivo == id_dispositivo))
    dispositivogps_db = result.scalars().first()
    
    if not dispositivogps_db:
        raise HTTPException(status_code=404, detail="DispositivoGPS no encontrado")
    
    return {
        "data": dispositivogps_db,
        "res" : True,
        "msg": "DispositivoGPS obtenido correctamente"
    }