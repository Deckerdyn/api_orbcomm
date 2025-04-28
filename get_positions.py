# get_positions.py (versión automática corregida)
import asyncio
import requests
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, date, timedelta
from pymongo import MongoClient
from main import get_or_refresh_token

# ——————————————————————————————
# 1) Cargo .env y MongoDB
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)
MONGO_URI = os.getenv("MONGO_URI")
print(f"📡 Usando MONGO_URI: {MONGO_URI}")
client = MongoClient(MONGO_URI)
db = client["orbcomm_db"]
positions = db["positions"]

ORBCOMM_ASSETS_URL = os.getenv("ORBCOMM_ASSETS_URL")

# Archivo donde guardamos la última fecha procesada
data_file = Path(__file__).parent / "last_date.txt"

# Función para obtener rango de fechas pendientes (usa fecha local)
def get_date_range():
    today_local = date.today()
    if data_file.exists():
        last_str = data_file.read_text().strip()
        last_date = date.fromisoformat(last_str)
    else:
        last_date = today_local - timedelta(days=2)
    start = last_date + timedelta(days=1)
    # Si start es mayor que hoy, no hay nada que hacer
    if start > today_local:
        return None, None, today_local
    return start, today_local, today_local

# Guarda la fecha final al terminar
def save_last_date(d: date):
    data_file.write_text(d.isoformat())

# ——————————————————————————————
# 2) Coroutine de fetch y store
async def fetch_and_store(date_str: str, token: str):
    payload = {
        "fromDate": f"{date_str}T00:00:00.000-04:00",
        "toDate":   f"{date_str}T23:59:59.000-04:00",
        "assetNames": [],
        "assetGroupNames": [],
        "watermark": None
    }
    headers = {"Content-Type": "application/json", "Authorization": token}

    print(f"📤 Fetch {date_str}")
    resp = requests.post(ORBCOMM_ASSETS_URL, json=payload, headers=headers)

    if resp.status_code == 429:
        await asyncio.sleep(300)
        resp = requests.post(ORBCOMM_ASSETS_URL, json=payload, headers=headers)

    if resp.status_code == 401:
        token = await get_or_refresh_token()
        headers["Authorization"] = token
        resp = requests.post(ORBCOMM_ASSETS_URL, json=payload, headers=headers)

    if resp.status_code != 200:
        print(f"❌ Error {resp.status_code}: {resp.text}")
        return

    data = resp.json().get("data", [])
    if not data:
        print(f"ℹ️ Sin datos en {date_str}")
        return

    for rec in data:
        positions.replace_one({"messageId": rec["messageId"]}, rec, upsert=True)
    print(f"✅ {len(data)} registros para {date_str}")

# ——————————————————————————————
# 3) Función principal: descarga automático de fechas pendientes
def main():
    start, end, today_local = get_date_range()
    if start is None:
        print(f"ℹ️ Ya estás al día (última fecha procesada: {today_local})")
        return

    print(f"⌛ Descargando de {start.isoformat()} a {end.isoformat()}")

    async def runner():
        current = start
        while current <= end:
            date_s = current.isoformat()
            try:
                token = await get_or_refresh_token()
                await fetch_and_store(date_s, token)
            except Exception as e:
                print(f"❌ Error {date_s}: {e}")
            current += timedelta(days=1)
        # marca hasta ayer si end==hoy\ n        mark = end
        if end == today_local:
            mark = today_local - timedelta(days=1)
        save_last_date(mark)
        print(f"🏁 Completado hasta {end}")

    asyncio.run(runner())

if __name__ == "__main__":
    import time
    print("🚀 Iniciando ciclo continuo de descarga cada 5 minutos")
    while True:
        main()
        print("⏳ Durmiendo 5 minutos antes del próximo ciclo…")
        time.sleep(300)  # 300 s = 5 min

