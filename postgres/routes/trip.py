from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import SessionLocal
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from ..schemas.trip import TripSchema, TripUpdateSchema, TripCreateSchema , TripRequestSchema
from ..auth.auth import get_current_user #Importamos para proteccion de rutas
import httpx
import os
import datetime


# llamadas al modelo
from ..models import Trip
from ..models import Usuario #importamos para proteccion de rutas
from ..models import TripLog #Importamos para generacion de logs
from ..models import Ruta #Importamos para generar rutas
from ..models import VehiculoConductor #Importamos para generar datos del vehiculo
from ..models import Empresa #Importamos para generar datos de la empresa
from ..models import Ubicacion #Importamos para generar datos de la ubicacion
from ..models import Vehiculo #Importamos para generar datos del vehiculo

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
    result = await db.execute(
        select(Trip)
        .options(
            selectinload(Trip.vehiculo).selectinload(Vehiculo.dispositivo),
            selectinload(Trip.ruta).selectinload(Ruta.origen),
            selectinload(Trip.ruta).selectinload(Ruta.destino),
            selectinload(Trip.estado_viaje)
        )
    )

    trips = result.scalars().all()
    trips_result = []

    for trip_db in trips:
        # Obtener posición GPS desde API externa si hay dispositivo
        if trip_db.vehiculo and trip_db.vehiculo.dispositivo:
            try:
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
            except httpx.RequestError as e:
                trip_db.vehiculo.dispositivo.posicion_gps = None
                print(f"Error en la solicitud HTTP: {e}")

        # Calcular ETA si origen y destino son válidos
        if (
            trip_db.ruta and
            trip_db.ruta.origen and
            trip_db.ruta.destino and
            trip_db.ruta.origen.latitud is not None and
            trip_db.ruta.origen.longitud is not None and
            trip_db.ruta.destino.latitud is not None and
            trip_db.ruta.destino.longitud is not None
        ):
            distancia_km = haversine(
                trip_db.ruta.origen.latitud,
                trip_db.ruta.origen.longitud,
                trip_db.ruta.destino.latitud,
                trip_db.ruta.destino.longitud
            )
            velocidad_kmh = 70
            tiempo_horas = distancia_km / velocidad_kmh
            tiempo_estimado = timedelta(hours=tiempo_horas)
            fecha_llegada_estim = (
                trip_db.fecha_salida_prog + tiempo_estimado
                if trip_db.fecha_salida_prog else None
            )

            trip_db.tiempo_estimado_horas = round(tiempo_horas, 2)
            trip_db.fecha_llegada_estim = fecha_llegada_estim
        else:
            trip_db.tiempo_estimado_horas = None
            trip_db.fecha_llegada_estim = None

        # Estado actual del viaje
        trip_db.current_state = trip_db.estado_viaje.nombre if trip_db.estado_viaje else None

        trips_result.append(trip_db)

    return trips_result

#POST
@router.post("/trips")
async def create_trip(
    trip: TripRequestSchema,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
):
    # 1. Crear la Ruta
    nueva_ruta = Ruta(
        nombre="viaje",
        descripcion=trip.comentarios,
        estado="activo",
        id_origen=trip.id_origen,
        id_destino=trip.id_destino
    )
    db.add(nueva_ruta)
    await db.commit()
    await db.refresh(nueva_ruta)
    

    # 2. Crear el Trip usando el id_ruta generado
    trip_db = Trip(
        fecha_registro=trip.fecha_registro,
        fecha_salida_prog=trip.fecha_salida_prog,
        fecha_llegada_estim=trip.fecha_llegada_estim,
        fecha_salida_real=trip.fecha_salida_real,
        fecha_llegada_real=trip.fecha_llegada_real,
        comentarios=trip.comentarios,
        id_ruta=nueva_ruta.id_ruta,
        id_empresa=trip.id_empresa,
        id_vehiculo=trip.id_vehiculo,
        id_estado=trip.id_estado
    )
    db.add(trip_db)
    await db.commit()
    await db.refresh(trip_db)

    # # Traer datos del vehiculo
    # result = await db.execute(select(VehiculoConductor).where(VehiculoConductor.id_vehiculo == trip.id_vehiculo))
    # vehiculoConductor = result.scalars().first()
    
    # # Traer datos de la empresa
    # result = await db.execute(select(Empresa).where(Empresa.id_empresa == trip.id_empresa))
    # empresa = result.scalars().first()
    
    # # Traer datos de la ubicacion
    # result = await db.execute(select(Ubicacion).where(Ubicacion.id_ubicacion == trip.id_origen))
    # origen = result.scalars().first()
    
    # result = await db.execute(select(Ubicacion).where(Ubicacion.id_ubicacion == trip.id_destino))
    # destino = result.scalars().first()

    # # 3. Crear log
    # log = TripLog(
    #     id_trip=trip_db,
    #     accion="CREAR",
    #     descripcion=f"Viaje creado por usuario {current_user.nombre} {current_user.apellido}",
    #     usuario_id=current_user.id_usuario,
    #     origen="sistema",
        
    #     id_vehiculo = trip_db.vehiculo,
    #     # si no hay conductor, crea id_conductor como None
    #     id_conductor = vehiculoConductor.conductor if vehiculoConductor.conductor else None,
    #     id_empresa = trip_db.empresa,
    #     id_ruta = trip_db.ruta,
        
    #     patente_vehiculo = vehiculoConductor.vehiculo.placa,
    #     nombre_conductor = vehiculoConductor.conductor.usuario.nombre + " " + vehiculoConductor.conductor.usuario.apellido,
    #     rut_empresa = empresa.rut,
    #     origen_viaje = origen.nombre,
    #     destino_viaje = destino.nombre,
    #     fecha_salida_prog = trip.fecha_salida_prog,
    #     fecha_llegada_estim = trip.fecha_llegada_estim,
    #     comentarios = trip.comentarios
    # )
    # db.add(log)
    # await db.commit()
    # await db.refresh(log)  

    return {
        "data": trip_db,
        "res" : True,
        "msg": "Viaje creado correctamente"
        }

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
    
    # Traer datos del vehiculo
    # result = await db.execute(select(VehiculoConductor).where(VehiculoConductor.id_vehiculo == trip_db.id_vehiculo))
    # vehiculoConductor = result.scalars().first()
    
    # # Traer datos de la empresa
    # result = await db.execute(select(Empresa).where(Empresa.id_empresa == trip_db.id_empresa))
    # empresa = result.scalars().first()
    
    # # Traer datos de la ubicacion
    # result = await db.execute(select(Ubicacion).where(Ubicacion.id_ubicacion == trip_db.ruta.id_origen))
    # origen = result.scalars().first()
    
    # result = await db.execute(select(Ubicacion).where(Ubicacion.id_ubicacion == trip_db.ruta.id_destino))
    # destino = result.scalars().first()
    
    # 3. Crear log
    # log = TripLog(
    #     id_trip=trip_db,
    #     accion="ELIMINAR",
    #     descripcion=f"Viaje eliminado por usuario {current_user.nombre} {current_user.apellido}",
    #     usuario_id=current_user.id_usuario,
    #     origen="sistema",
        
    #     id_vehiculo = trip_db.vehiculo,
    #     id_conductor = vehiculoConductor.conductor,
    #     id_empresa = trip_db.empresa,
    #     id_ruta = trip_db.ruta,
        
    #     patente_vehiculo = vehiculoConductor.vehiculo.placa,
    #     nombre_conductor = vehiculoConductor.conductor.usuario.nombre + " " + vehiculoConductor.conductor.usuario.apellido,
    #     rut_empresa = empresa.rut,
    #     origen_viaje = origen.nombre,
    #     destino_viaje = destino.nombre,
    #     fecha_salida_prog = trip_db.fecha_salida_prog,
    #     fecha_llegada_estim = trip_db.fecha_llegada_estim,
    #     comentarios = trip_db.comentarios
    # )
    # db.add(log)
    # await db.commit()
    # await db.refresh(log)
    
    await db.delete(trip_db)
    await db.commit()
    
    return {
            "data": None,
            "res" : True,
            "msg": "Trip eliminado"
        }

# GET especifico batch , carga más rapida de datos
@router.get("/trips/batch", response_model=List[TripSchema])
async def get_multiple_trips(
    ids: List[int] = Query(..., description="IDs de viajes separados por coma"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Trip).where(Trip.id_trip.in_(ids)))
    trips_db = result.scalars().all()
        

    if not trips_db:
        raise HTTPException(status_code=404, detail="No se encontraron viajes.")

    async with httpx.AsyncClient() as client:
        for trip in trips_db:
            if trip.vehiculo and trip.vehiculo.dispositivo:
                try:
                    response = await client.get(
                        f"{ipServidor}/positions/last/{trip.vehiculo.dispositivo.numero_serie}"
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if (
                            isinstance(data, list)
                            and len(data) > 0
                            and data[0].get("positionStatus")
                        ):
                            trip.vehiculo.dispositivo.posicion_gps = {
                                "latitud": data[0]["positionStatus"]["latitude"],
                                "longitud": data[0]["positionStatus"]["longitude"]
                            }
                        else:
                            trip.vehiculo.dispositivo.posicion_gps = None
                    else:
                        trip.vehiculo.dispositivo.posicion_gps = None
                except Exception:
                    trip.vehiculo.dispositivo.posicion_gps = None

            # Cálculo de porcentaje y ETA
            if (
                trip.vehiculo and
                trip.vehiculo.dispositivo and
                trip.vehiculo.dispositivo.posicion_gps and
                trip.ruta and
                trip.ruta.origen and
                trip.ruta.destino and
                trip.ruta.origen.latitud is not None and
                trip.ruta.origen.longitud is not None and
                trip.ruta.destino.latitud is not None and
                trip.ruta.destino.longitud is not None
            ):
                lat_actual = trip.vehiculo.dispositivo.posicion_gps["latitud"]
                lon_actual = trip.vehiculo.dispositivo.posicion_gps["longitud"]

                distancia_total_km = haversine(
                    trip.ruta.origen.latitud,
                    trip.ruta.origen.longitud,
                    trip.ruta.destino.latitud,
                    trip.ruta.destino.longitud
                )
                distancia_recorrida_km = haversine(
                    trip.ruta.origen.latitud,
                    trip.ruta.origen.longitud,
                    lat_actual,
                    lon_actual
                )

                velocidad_kmh = 70
                tiempo_horas = distancia_recorrida_km / velocidad_kmh
                tiempo_estimado = timedelta(hours=tiempo_horas)

                fecha_llegada_estim = (
                    trip.fecha_salida_prog + tiempo_estimado
                    if trip.fecha_salida_prog else None
                )

                trip.tiempo_estimado_horas = round(tiempo_horas, 2)
                trip.fecha_llegada_estim = fecha_llegada_estim

                porcentaje_viaje = (distancia_recorrida_km / distancia_total_km) * 100
                porcentaje_viaje = max(0, min(round(porcentaje_viaje, 2), 100))
                trip.porcentaje_viaje = porcentaje_viaje
                trip.distancia_total_km = round(distancia_total_km, 2)
            else:
                trip.porcentaje_viaje = None
                trip.tiempo_estimado_horas = None
                trip.fecha_llegada_estim = None
                trip.distancia_total_km = None
            # Estado actual del viaje
            trip.current_state = trip.estado_viaje.nombre if trip.estado_viaje else None
    return trips_db

#GET especifico trip
@router.get("/trips/{id_trip}")
async def get_trip(
    id_trip: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
):
    result = await db.execute(select(Trip).where(Trip.id_trip == id_trip))
    trip_db = result.scalars().first()
    if not trip_db:
        raise HTTPException(status_code=404, detail="Trip no encontrado")

    trip_db.current_state = trip_db.estado_viaje.nombre


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
        trip_db.distancia_total_km = round(distancia_total_km, 2)
    else:
        trip_db.porcentaje_viaje = None
        trip_db.tiempo_estimado_horas = None
        trip_db.fecha_llegada_estim = None
        trip_db.distancia_total_km = None


    return {
            "data": trip_db,
            "res" : True,
            "msg": "Trip obtenido correctamente"
        }


