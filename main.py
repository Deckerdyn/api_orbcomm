from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timezone
import requests
import os
from dotenv import load_dotenv
from pathlib import Path

# Cargar el .env desde el mismo directorio donde está main.py
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Conexión a MongoDB (remoto o local, según el .env)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)

# Si estás autenticando con usuario/contraseña, mejor especificar authSource
# ejemplo de URI en tu .env:
# mongodb://admin:admin123@10.20.7.231:27017/?authSource=admin

db = client["orbcomm_db"]
tokens_collection = db["tokens"]

app = FastAPI()

async def generate_token_orbcomm():
    url = os.getenv("ORBCOMM_TOKEN_URL")
    payload = {
        "userName": os.getenv("ORBCOMM_USERNAME"),
        "password": os.getenv("ORBCOMM_PASSWORD")
    }
    resp = requests.post(url, json=payload)
    raw = resp.text
    if resp.status_code != 200:
        print("❌ generateToken HTTP error:", resp.status_code, raw)
        raise HTTPException(500, f"Error generando token: {raw}")

    body = resp.json()
    print("🔑 generateToken response:", body)

    if body.get("code") != 0 or not body.get("data"):
        raise HTTPException(
            500,
            f"Token API error: {body.get('message')} (code {body.get('code')})"
        )

    data = body["data"]
    print("🔑 Nuevo accessToken generado:", data["accessToken"])

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
                print("🔑 Reusando accessToken:", doc["accessToken"])
                return doc["accessToken"]
    return await generate_token_orbcomm()

@app.get("/token")
async def read_token():
    token = await get_or_refresh_token()
    return {"access_token": token}
