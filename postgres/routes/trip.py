from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import SessionLocal
from sqlalchemy.future import select
from typing import List
from ..schemas.trip import TripSchema, TripUpdateSchema, TripCreateSchema
from ..auth.auth import get_current_user #Importamos para proteccion de rutas
import httpx
import os

# llamadas al modelo
from ..models import Trip
from ..models import Usuario #importamos para proteccion de rutas


router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas
ipServidor = os.getenv("IPSERVIDOR")

#calculo tiempo 
from datetime import timedelta
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

#GET
@router.get("/trips", response_model=List[TripSchema])
async def get_trips(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Trip))
    trips = result.scalars().all()
    trips_result = []
    for trip_db in trips:
        # Verificamos si hay ruta con ubicaciones válidas
        if trip_db.vehiculo.dispositivo != None:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{ipServidor}/positions/last/{trip_db.vehiculo.dispositivo.numero_serie}"
                )
                
                if response.status_code == 200:
                    data = response.json()

                    if (
                        isinstance(data, list) and 
                        len(data) > 0 and 
                        data[0].get("positionStatus")
                    ):
                        trip_db.vehiculo.dispositivo.posicion_gps = {
                            "latitud": data[0]["positionStatus"]["latitude"],
                            "longitud": data[0]["positionStatus"]["longitude"]
                        }
                else:
                    trip_db.vehiculo.dispositivo.posicion_gps = None
        if (
            trip_db.ruta and
            trip_db.ruta.origen and
            trip_db.ruta.destino and
            trip_db.ruta.origen.latitud is not None and
            trip_db.ruta.origen.longitud is not None and
            trip_db.ruta.destino.latitud is not None and
            trip_db.ruta.destino.longitud is not None
        ):
            # Paso 1: Calcular distancia
            distancia_km = haversine(
                trip_db.ruta.origen.latitud,
                trip_db.ruta.origen.longitud,
                trip_db.ruta.destino.latitud,
                trip_db.ruta.destino.longitud
            )

            # Paso 2: Calcular tiempo estimado
            velocidad_kmh = 70
            tiempo_horas = distancia_km / velocidad_kmh
            tiempo_estimado = timedelta(hours=tiempo_horas)

            # Paso 3: Calcular fecha llegada estimada
            if trip_db.fecha_salida_prog:
                fecha_llegada_estim = trip_db.fecha_salida_prog + tiempo_estimado
            else:
                fecha_llegada_estim = None

            # Agregamos dinámicamente los campos al objeto
            trip_db.tiempo_estimado_horas = round(tiempo_horas, 2)
            trip_db.fecha_llegada_estim = fecha_llegada_estim
        else:
            trip_db.tiempo_estimado_horas = None
            trip_db.fecha_llegada_estim = None
            
        trips_result.append(trip_db)
    return trips_result

#POST
@router.post("/trips")
async def create_trip(
    trip: TripCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    trip_db = Trip(**trip.dict())
    db.add(trip_db)
    await db.commit()    
    await db.refresh(trip_db)
    return trip_db

#PUT
@router.put("/trips/{id_trip}", response_model=TripSchema)
async def update_trip(
    id_trip: int, 
    trip: TripUpdateSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Trip).where(Trip.id_trip == id_trip))
    trip_db = result.scalars().first()
    if not trip_db:
        raise HTTPException(status_code=404, detail="Trip no encontrada")

    for key, value in trip.dict(exclude_unset=True).items():
        setattr(trip_db, key, value)

    await db.commit()
    await db.refresh(trip_db)
    return trip_db

#DELETE
@router.delete("/trips/{id_trip}")
async def delete_trip(
    id_trip: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Trip).where(Trip.id_trip == id_trip))
    trip_db = result.scalars().first()
    if not trip_db:
        raise HTTPException(status_code=404, detail="Trip no encontrada")

    await db.delete(trip_db)
    await db.commit()
    return {"detail": "Trip eliminado"}


#GET especifico trip
@router.get("/trips/{id_trip}", response_model=TripSchema)
async def get_trip(
    id_trip: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
):
    result = await db.execute(select(Trip).where(Trip.id_trip == id_trip))
    trip_db = result.scalars().first()
    if not trip_db:
        raise HTTPException(status_code=404, detail="Trip no encontrado")

    if trip_db.vehiculo.dispositivo != None:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ipServidor}/positions/last/{trip_db.vehiculo.dispositivo.numero_serie}"
            )
            
            if response.status_code == 200:
                data = response.json()

                if (
                    isinstance(data, list) and 
                    len(data) > 0 and 
                    data[0].get("positionStatus")
                ):
                    trip_db.vehiculo.dispositivo.posicion_gps = {
                        "latitud": data[0]["positionStatus"]["latitude"],
                        "longitud": data[0]["positionStatus"]["longitude"]
                    }
            else:
                trip_db.vehiculo.dispositivo.posicion_gps = None
                
    # Verificamos si hay ruta con ubicaciones válidas
    if (
        trip_db.vehiculo.dispositivo and
        trip_db.vehiculo.dispositivo.posicion_gps and
        trip_db.ruta and
        trip_db.ruta.origen and
        trip_db.ruta.destino and
        trip_db.ruta.origen.latitud is not None and
        trip_db.ruta.origen.longitud is not None and
        trip_db.ruta.destino.latitud is not None and
        trip_db.ruta.destino.longitud is not None
    ):
        lat_actual = trip_db.vehiculo.dispositivo.posicion_gps["latitud"]
        lon_actual = trip_db.vehiculo.dispositivo.posicion_gps["longitud"]

        # Distancia total del viaje (de origen a destino)
        distancia_total_km = haversine(
            trip_db.ruta.origen.latitud,
            trip_db.ruta.origen.longitud,
            trip_db.ruta.destino.latitud,
            trip_db.ruta.destino.longitud
        )

        # Distancia recorrida (de origen a posición actual)
        distancia_recorrida_km = haversine(
            trip_db.ruta.origen.latitud,
            trip_db.ruta.origen.longitud,
            lat_actual,
            lon_actual
        )
        
        velocidad_kmh = 70
        tiempo_horas = distancia_recorrida_km / velocidad_kmh
        tiempo_estimado = timedelta(hours=tiempo_horas)

        if trip_db.fecha_salida_prog:
            fecha_llegada_estim = trip_db.fecha_salida_prog + tiempo_estimado
        else:
            fecha_llegada_estim = None

        # Agregamos dinámicamente los campos al objeto
        trip_db.tiempo_estimado_horas = round(tiempo_horas, 2)
        trip_db.fecha_llegada_estim = fecha_llegada_estim

        porcentaje_viaje = (distancia_recorrida_km / distancia_total_km) * 100
        porcentaje_viaje = max(0, min(round(porcentaje_viaje, 2), 100))  
        trip_db.porcentaje_viaje = porcentaje_viaje
    else:
        trip_db.porcentaje_viaje = None
        trip_db.tiempo_estimado_horas = None
        trip_db.fecha_llegada_estim = None

    return trip_db
