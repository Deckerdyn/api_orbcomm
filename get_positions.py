# get_positions.py
import asyncio
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from pymongo import MongoClient
from main import get_or_refresh_token  # importa para que cargue .env y main.py

load_dotenv()

# Conexión a MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["orbcomm_db"]
positions = db["positions"]

ORBCOMM_ASSETS_URL = os.getenv("ORBCOMM_ASSETS_URL")

# Guarda el timestamp de la última llamada
last_call_time = None

async def fetch_and_store(date_str: str, token: str):
    global last_call_time

    payload = {
        "fromDate": f"{date_str}T00:00:00.000-04:00",
        "toDate":   f"{date_str}T23:59:59.000-04:00",
        "assetNames": [],
        "assetGroupNames": [],
        "watermark": None
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }

    # Asegura que hayan pasado 5 minutos desde la última llamada
    if last_call_time:
        elapsed = (datetime.utcnow() - last_call_time).total_seconds()
        if elapsed < 300:
            wait = 300 - elapsed
            print(f"⏳ Sólo han pasado {int(elapsed)}s desde la última llamada. Esperando {int(wait)}s…")
            await asyncio.sleep(wait)

    print(f"📤 Llamando getAssetStatus para {date_str}")
    resp = requests.post(ORBCOMM_ASSETS_URL, json=payload, headers=headers)
    last_call_time = datetime.utcnow()

    # Si devuelve 429, vuelve a esperar 5 minutos y reintenta
    if resp.status_code == 429:
        print(f"⚠️ 429 Rate limit en {date_str}: {resp.text}")
        print("🔁 Esperando 5 minutos completos antes de reintentar…")
        await asyncio.sleep(300)
        # reintenta una vez
        resp = requests.post(ORBCOMM_ASSETS_URL, json=payload, headers=headers)
        last_call_time = datetime.utcnow()

    # Si devuelve 401, regeneramos token y reintentar
    if resp.status_code == 401:
        print(f"⚠️ 401 Invalid token en {date_str}: {resp.text}")
        token = await get_or_refresh_token()
        headers["Authorization"] = token
        print("🔄 Token renovado, reintentando…")
        resp = requests.post(ORBCOMM_ASSETS_URL, json=payload, headers=headers)
        last_call_time = datetime.utcnow()

    if resp.status_code != 200:
        print(f"⚠️ Error {resp.status_code} en {date_str}: {resp.text}")
        return

    body = resp.json()
    data = body.get("data", [])
    if not data:
        print(f"ℹ️ Sin datos en {date_str}")
        return

    for rec in data:
        positions.replace_one({"messageId": rec["messageId"]}, rec, upsert=True)
    print(f"✅ {len(data)} registros insertados para {date_str}")

async def main():
    start = datetime(2025, 4, 25)
    end   = datetime(2025, 4, 25)
    current = start

    while current <= end:
        date_s = current.strftime("%Y-%m-%d")
        print(f"\n📅 Procesando {date_s}")
        try:
            token = await get_or_refresh_token()
            await fetch_and_store(date_s, token)
        except Exception as e:
            print(f"❌ Error en {date_s}: {e}")
        # Marcamos tiempo y luego avanzamos
        current += timedelta(days=1)

    print("\n🏁 Proceso completado.")

if __name__ == "__main__":
    asyncio.run(main())
