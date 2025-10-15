# get_positions.py
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
positions_2 = db["positions_2"]
geocerca = db["geocerca"]

ORBCOMM_ASSETS_URL = os.getenv("ORBCOMM_ASSETS_URL")
data_file = Path(__file__).parent / "last_date.txt"

# ——————————————————————————————
# Funciones auxiliares
def get_date_range():
    today_local = date.today()
    if data_file.exists():
        last_str = data_file.read_text().strip()
        last_date = date.fromisoformat(last_str)
    else:
        last_date = today_local - timedelta(days=2)
    start = last_date + timedelta(days=1)
    if start > today_local:
        return None, None, today_local
    return start, today_local, today_local

def save_last_date(d: date):
    data_file.write_text(d.isoformat())

# ——————————————————————————————
# Coroutine de fetch y store con reintentos
async def fetch_and_store(date_str: str, token: str, max_retries=3):
    payload = {
        "fromDate": f"{date_str}T00:00:00.000-04:00",
        "toDate":   f"{date_str}T23:59:59.000-04:00",
        "assetNames": [],
        "assetGroupNames": [],
        "watermark": None
    }
    headers = {"Content-Type": "application/json", "Authorization": token}

    for attempt in range(1, max_retries+1):
        try:
            print(f"📤 Fetch {date_str} (Intento {attempt})")
            resp = requests.post(ORBCOMM_ASSETS_URL, json=payload, headers=headers, timeout=300)

            if resp.status_code == 401:
                token = await get_or_refresh_token()
                headers["Authorization"] = token
                continue

            if resp.status_code == 423:
                print(f"⚠️ Error 423: demasiadas solicitudes concurrentes, esperando 5 min...")
                await asyncio.sleep(300)
                continue

            if resp.status_code == 504:
                print(f"⚠️ Error 504 Gateway Time-out, esperando 5 min...")
                await asyncio.sleep(300)
                continue

            if resp.status_code != 200:
                print(f"❌ Error {resp.status_code}: {resp.text}")
                return

            data = resp.json().get("data", [])
            if not data:
                print(f"ℹ️ Sin datos en {date_str}")
                return

            # — Procesar registros —
            for rec in data:
                try:
                    message_stamp = rec.get("assetStatus", {}).get("messageStamp")
                    if message_stamp and "/" in message_stamp and ("AM" in message_stamp or "PM" in message_stamp):
                        dt = datetime.strptime(message_stamp, "%m/%d/%Y %I:%M:%S %p")
                        rec["assetStatus"]["messageStamp"] = dt.strftime("%Y-%m-%dT%H:%M:%S.000-04:00")
                except Exception as e:
                    print(f"⚠️ Error al convertir assetStatus.messageStamp: {message_stamp} -> {e}")

                geofence_status = rec.get("positionStatus", {}).get("geofenceStatus")
                message_id = rec.get("messageId")
                asset_name = rec.get("assetName")
                status = (geofence_status or "").strip().upper()

                target_collection = positions_2 if asset_name == "FSKC623020600" else positions

                if status in ("ARRIVAL", "IN"):
                    geocerca.replace_one({"messageId": message_id}, rec, upsert=True)
                    target_collection.delete_one({"messageId": message_id})
                elif status == "DEPARTURE":
                    geocerca.replace_one({"messageId": message_id}, rec, upsert=True)
                    target_collection.replace_one({"messageId": message_id}, rec, upsert=True)
                else:
                    if not geocerca.find_one({"messageId": message_id}):
                        target_collection.replace_one({"messageId": message_id}, rec, upsert=True)

            break  # ✅ Si salió bien, salir del loop de reintentos

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Intento {attempt} fallido: {e}")
            await asyncio.sleep(300)

    await asyncio.sleep(5)  # Pausa corta entre fechas

# ——————————————————————————————
# Función principal
def main():
    start, end, today_local = get_date_range()
    if start is None:
        print(f"ℹ️ Ya estás al día (última fecha procesada: {today_local})")
        return

    print(f"⌛ Descargando de {start.isoformat()} a {end.isoformat()}")

    async def runner():
        current = start
        while current <= end:
            # Descarga por bloques de 5 días
            block_end = min(current + timedelta(days=4), end)
            date_block = []
            temp = current
            while temp <= block_end:
                date_block.append(temp)
                temp += timedelta(days=1)

            token = await get_or_refresh_token()
            for d in date_block:
                date_s = d.isoformat()
                try:
                    await fetch_and_store(date_s, token)
                except Exception as e:
                    print(f"❌ Error {date_s}: {e}")

            # Guarda el progreso del último día del bloque
            save_last_date(block_end)
            current = block_end + timedelta(days=1)

        print(f"🏁 Completado hasta {end}")

    asyncio.run(runner())

# ——————————————————————————————
if __name__ == "__main__":
    import time
    print("🚀 Iniciando ciclo continuo de descarga cada 5 minutos")
    while True:
        main()
        print("⏳ Durmiendo 5 minutos antes del próximo ciclo…")
        time.sleep(300)
