from fastapi import FastAPI, HTTPException, Query
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timezone
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from pymongo import DESCENDING
import pytz
from typing import Optional
from math import radians, cos, sin, asin, sqrt

# ——————————————————————————————
# 1) Cargar variables de entorno y conectar a MongoDB
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["orbcomm_db"]
tokens_collection = db["tokens"]
positions_collection = db["positions"]
geocerca_collection = db["geocerca"]

# ——————————————————————————————
# 2) Crear app FastAPI y permitir CORS
app = FastAPI()

# Permitir acceso desde React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# conexion postgresql
from postgres.routes import api_router
app.include_router(api_router)

# ——————————————————————————————
# 3) Funciones de token
async def generate_token_orbcomm():
    url = os.getenv("ORBCOMM_TOKEN_URL")
    payload = {
        "userName": os.getenv("ORBCOMM_USERNAME"),
        "password": os.getenv("ORBCOMM_PASSWORD")
    }
    resp = requests.post(url, json=payload)
    if resp.status_code != 200:
        raise HTTPException(500, f"Error generando token: {resp.text}")

    body = resp.json()
    if body.get("code") != 0 or not body.get("data"):
        raise HTTPException(
            500,
            f"Token API error: {body.get('message')} (code {body.get('code')})"
        )

    data = body["data"]
    tokens_collection.delete_many({})
    tokens_collection.insert_one(data)
    return data["accessToken"]

async def get_or_refresh_token():
    doc = tokens_collection.find_one()
    if doc:
        exp_str = doc.get("accessTokenexpireOn")
        if exp_str:
            exp = datetime.fromisoformat(exp_str.replace("Z", "+00:00"))
            if datetime.now(timezone.utc) < exp:
                return doc["accessToken"]
    return await generate_token_orbcomm()

# ——————————————————————————————
# 4) Endpoints API

@app.get("/token")
async def read_token():
    """Devuelve un token vigente, o genera uno nuevo si expiró."""
    token = await get_or_refresh_token()
    return {"access_token": token}

@app.get("/refreshtoken")
async def refresh_token():
    """Fuerza la creación de un nuevo token sin importar expiración."""
    token = await generate_token_orbcomm()
    return {"access_token": token}

@app.get("/positions")
async def get_positions_ast_demosat():
    results = list(positions_collection.find(
        {"assetStatus.assetName": "AST-DEMOSAT"},
        {"_id": 0, "messageId": 1, "assetStatus": 1, "positionStatus": 1}
    ))
    return results

@app.get("/positions/asset/{asset_name}")
async def get_positions_by_asset_name(asset_name: str):
    results = list(positions_collection.find(
        {"assetStatus.assetName": asset_name},
        {"_id": 0}
    ))
    if not results:
        raise HTTPException(status_code=404, detail=f"No se encontraron posiciones para assetName: {asset_name}")
    return results

@app.get("/positions/message/{message_id}")
async def get_position_by_message_id(message_id: str):
    result = positions_collection.find_one({"messageId": message_id}, {"_id": 0})
    if not result:
        raise HTTPException(404, f"No se encontró posición con messageId: {message_id}")
    return result

@app.get("/geocerca")
async def get_all_geocerca():
    results = list(geocerca_collection.find({}, {"_id": 0}))
    return results

@app.get("/positions/last")
async def get_last_position_ast_demosat():
    result = positions_collection.find_one(
        {"assetStatus.assetName": "AST-DEMOSAT"},
        sort=[("assetStatus.messageStamp", DESCENDING)],
        projection={"_id": 0, "messageId": 1, "assetStatus": 1, "positionStatus": 1}
    )
    if not result:
        raise HTTPException(404, "No se encontró ninguna posición para AST-DEMOSAT")
    return result

@app.get("/positions/last/time")
async def get_last_position_time():
    result = positions_collection.find_one(
        {"assetStatus.assetName": "AST-DEMOSAT"},
        sort=[("assetStatus.messageStamp", DESCENDING)],
        projection={"_id": 0, "messageId": 1, "assetStatus.messageStamp": 1}
    )

    if not result:
        raise HTTPException(404, "No se encontró ninguna posición para AST-DEMOSAT")

    # Usamos el string completo con offset -04:00
    timestamp_str = result["assetStatus"]["messageStamp"]
    last_update = datetime.fromisoformat(timestamp_str)

    # Fecha actual con la misma zona horaria (-04:00)
    now = datetime.now(pytz.timezone("America/Santiago"))

    # Convertimos last_update a la misma zona si fuera necesario
    if last_update.tzinfo is None:
        last_update = last_update.replace(tzinfo=pytz.FixedOffset(-240))  # -04:00

    elapsed = now - last_update
    elapsed_minutes = int(elapsed.total_seconds() / 60)

    return {
        "last_update": last_update.isoformat(),
        "now": now.isoformat(),
        "elapsed_minutes": elapsed_minutes,
        "message": f"Han pasado {elapsed_minutes} minutos desde la última actualización."
    }
@app.get("/estado-camion")
def estado_camion():
    ultimo = positions_collection.find_one(
        {"impactStatus.moving": {"$exists": True}},
        sort=[("assetStatus.messageStamp", DESCENDING)]
    )

    if not ultimo:
        raise HTTPException(status_code=404, detail="No se encontraron datos del camión.")

    moving_status = ultimo.get("impactStatus", {}).get("moving", "Desconocido")
    timestamp = ultimo.get("assetStatus", {}).get("messageStamp")

    if timestamp:
        try:
            timestamp_dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except:
            timestamp_dt = timestamp
    else:
        timestamp_dt = "Fecha desconocida"

    if moving_status == "Stationary":
        estado = "detenido"
    elif moving_status == "Moving":
        estado = "en movimiento"
    else:
        estado = f"estado desconocido ({moving_status})"

    return {
        "estado": estado,
        "ultimo_mensaje": timestamp_dt
    }
@app.get("/geocerca/estado-reciente")
def geocerca_estado_reciente(asset_name: Optional[str] = Query(None, alias="assetName")):

    filtro_base = {}
    if asset_name:
        filtro_base["assetStatus.assetName"] = asset_name

    # Buscar llegada más reciente (ARRIVAL)
    filtro_llegada = filtro_base.copy()
    filtro_llegada["positionStatus.geofenceStatus"] = "ARRIVAL"
    llegada = geocerca_collection.find_one(
        filtro_llegada, sort=[("assetStatus.messageStamp", -1)]
    )

    # Buscar salida más reciente (DEPARTURE)
    filtro_salida = filtro_base.copy()
    filtro_salida["positionStatus.geofenceStatus"] = "DEPARTURE"
    salida = geocerca_collection.find_one(
        filtro_salida, sort=[("assetStatus.messageStamp", -1)]
    )

    if not llegada and not salida:
        raise HTTPException(status_code=404, detail="No se encontraron eventos de entrada o salida.")

    def formatear_evento(evento):
        if evento is None:
            return None
        
        estado = evento["positionStatus"].get("geofenceStatus", "")
        
        if estado == "ARRIVAL":
            geocerca_nombre = evento["positionStatus"].get("geofenceName", "Desconocida")
        elif estado == "DEPARTURE":
            geocerca_nombre = evento["positionStatus"].get("nearestGeofence", "Desconocida")
        else:
            geocerca_nombre = "Desconocida"

        return {
            "hora": evento["assetStatus"].get("messageStamp"),
            "geocerca": geocerca_nombre,
            "direccion": {
                "street": evento["positionStatus"].get("street", "Desconocido"),
                "city": evento["positionStatus"].get("city", "Desconocido"),
                "state": evento["positionStatus"].get("state", "Desconocido"),
                "zipCode": evento["positionStatus"].get("zipCode", "Desconocido"),
                "country": evento["positionStatus"].get("country", "Desconocido"),
            }
        }

    llegada_formateada = formatear_evento(llegada)
    salida_formateada = formatear_evento(salida)

    # Determinar evento más reciente
    llegada_time = datetime.fromisoformat(llegada_formateada["hora"].replace("Z", "+00:00")) if llegada_formateada else None
    salida_time = datetime.fromisoformat(salida_formateada["hora"].replace("Z", "+00:00")) if salida_formateada else None

    if llegada_time and salida_time:
        evento_reciente = "llegada" if llegada_time > salida_time else "salida"
    elif llegada_time:
        evento_reciente = "llegada"
    elif salida_time:
        evento_reciente = "salida"
    else:
        evento_reciente = None

    return {
        "llegada": llegada_formateada,
        "salida": salida_formateada,
        "evento_reciente": evento_reciente
    }

# @app.get("/geocerca/ultima-nearest")
# def ultima_nearest_geofence():
#     # Obtener el documento más reciente de la colección positions
#     ultimo = positions_collection.find_one(
#         {}, sort=[("assetStatus.messageStamp", DESCENDING)]
#     )

#     if not ultimo:
#         raise HTTPException(status_code=404, detail="No se encontró ningún dato en positions.")

#     nearest = ultimo.get("positionStatus", {}).get("nearestGeofence")

#     if not nearest:
#         raise HTTPException(status_code=404, detail="No se encontró nearestGeofence en el último dato.")

#     return {
#         "nearestGeofence": nearest,
#         "hora": ultimo["assetStatus"].get("messageStamp")
#     }
@app.get("/positions/last/{deviceSN}")
async def get_last_positions_by_device_sn(deviceSN: str):
    results = list(positions_collection.find(
        {"assetStatus.deviceSN": deviceSN},
        sort=[("assetStatus.messageStamp", DESCENDING)],
        projection={"_id": 0}
    ).limit(10))

    if not results:
        raise HTTPException(status_code=404, detail=f"No se encontraron posiciones para deviceSN: {deviceSN}")

    return results

def haversine(lat1, lon1, lat2, lon2):
    """Calcula distancia entre dos puntos GPS en km"""
    R = 6371  # Radio de la Tierra en km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

@app.get("/positions/nearest/{device_sn}")
def nearest_device(device_sn: str):
    # 1. Obtener la última posición del dispositivo consultado
    origen = positions_collection.find_one(
        {"assetStatus.deviceSN": device_sn},
        sort=[("assetStatus.messageStamp", DESCENDING)]
    )
    if not origen:
        raise HTTPException(404, f"No se encontró dispositivo con deviceSN: {device_sn}")

    lat1 = origen.get("positionStatus", {}).get("latitude")
    lon1 = origen.get("positionStatus", {}).get("longitude")

    if lat1 is None or lon1 is None:
        raise HTTPException(400, f"Dispositivo {device_sn} no tiene coordenadas GPS válidas")

    # 2. Buscar otros dispositivos con coordenadas válidas
    otros = positions_collection.find({
        "assetStatus.deviceSN": {"$ne": device_sn},
        "positionStatus.latitude": {"$ne": None},
        "positionStatus.longitude": {"$ne": None}
    })

    # 3. Calcular distancias y encontrar el más cercano
    mas_cercano = None
    menor_distancia = float("inf")

    for doc in otros:
        lat2 = doc["positionStatus"]["latitude"]
        lon2 = doc["positionStatus"]["longitude"]
        dist = haversine(lat1, lon1, lat2, lon2)
        if dist < menor_distancia:
            menor_distancia = dist
            mas_cercano = doc

    if not mas_cercano:
        raise HTTPException(404, "No se encontró ningún otro dispositivo con ubicación válida")

    return {
        "dispositivo_consultado": {
            "deviceSN": device_sn,
            "ubicacion": origen["positionStatus"].get("address"),
            "coordenadas": [lat1, lon1]
        },
        "dispositivo_mas_cercano": {
            "deviceSN": mas_cercano["assetStatus"]["deviceSN"],
            "ubicacion": mas_cercano["positionStatus"].get("address"),
            "coordenadas": [
                mas_cercano["positionStatus"]["latitude"],
                mas_cercano["positionStatus"]["longitude"]
            ],
            "distancia_km": round(menor_distancia, 2)
        }
    }