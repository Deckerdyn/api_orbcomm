from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timezone
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

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
    token = await get_or_refresh_token()
    return {"access_token": token}

@app.get("/positions")
async def get_all_positions():
    results = list(positions_collection.find({}, {"_id": 0}))
    return results

@app.get("/positions/{asset_name}")
async def get_positions_by_asset(asset_name: str):
    results = list(positions_collection.find({"assetName": asset_name}, {"_id": 0}))
    if not results:
        raise HTTPException(404, f"No se encontraron posiciones para {asset_name}")
    return results

@app.get("/geocerca")
async def get_all_geocerca():
    results = list(geocerca_collection.find({}, {"_id": 0}))
    return results
