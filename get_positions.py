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
# Cargo .env y MongoDB
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
async def fetch_and_store(date_str: str, from_hour: int, to_hour: int, token: str, max_retries=3):
    payload = {
        "fromDate": f"{date_str}T{from_hour:02d}:00:00.000-04:00",
        "toDate":   f"{date_str}T{to_hour:02d}:00:00.000-04:00",
        "assetNames": [],
        "assetGroupNames": [],
        "watermark": None
    }
    headers = {"Content-Type": "application/json", "Authorization": token}

    for attempt in range(1, max_retries+1):
        try:
            print(f"📤 Fetch {date_str} {from_hour:02d}-{to_hour:02d} (Intento {attempt})")
            resp = requests.post(ORBCOMM_ASSETS_URL, json=payload, headers=headers, timeout=600)

            if resp.status_code == 401:
                token = await get_or_refresh_token()
                headers["Authorization"] = token
                continue

            if resp.status_code in (423, 429):
                print(f"⚠️ Error {resp.status_code}: demasiadas solicitudes o polling frecuente, esperando 5 minutos...")
                await asyncio.sleep(300)
                continue

            if resp.status_code == 504:
                print(f"⚠️ Error 504 Gateway Time-out, esperando 5 minutos...")
                await asyncio.sleep(300)
                continue

            if resp.status_code != 200:
                print(f"❌ Error {resp.status_code}: {resp.text}")
                return

            data = resp.json().get("data", [])
            if not data:
                print(f"ℹ️ Sin datos en {date_str} {from_hour:02d}-{to_hour:02d}")
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

            break  # ✅ Si salió bien, rompe el bucle de reintentos

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Intento {attempt} fallido: {e}")
            await asyncio.sleep(300)

    # Pausa entre franjas para cumplir la política de polling
    await asyncio.sleep(300)

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
            date_s = current.isoformat()
            try:
                token = await get_or_refresh_token()
                # Franjas de 2 horas
                for from_h in range(0, 24, 2):
                    to_h = from_h + 2
                    await fetch_and_store(date_s, from_h, to_h, token)
                # Guardar progreso solo si todas las franjas se completaron
                save_last_date(current)
            except Exception as e:
                print(f"❌ Error {date_s}: {e}")
            current += timedelta(days=1)

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
