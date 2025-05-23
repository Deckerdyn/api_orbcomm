from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timezone
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from pymongo import DESCENDING
import pytz

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