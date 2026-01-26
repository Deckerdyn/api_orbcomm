# get_positions.py
import asyncio
import requests
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, date, timedelta, timezone
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
                    asset_status = rec.get("assetStatus", {})
                    message_stamp = asset_status.get("messageStamp")
                    print(f"🔄 Procesando messageStamp: {message_stamp} ")

                    if message_stamp and "/" in message_stamp and ("AM" in message_stamp or "PM" in message_stamp):
                        dt = datetime.strptime(message_stamp, "%m/%d/%Y %I:%M:%S %p")
                        
                        rec["assetStatus"]["messageStamp"] = dt.strftime("%Y-%m-%dT%H:%M:%S.000-04:00")
                        
                        tz_origen = timezone(timedelta(hours=-4))
                        dt_con_tz = dt.replace(tzinfo=tz_origen)
                        dt_utc = dt_con_tz.astimezone(timezone.utc)
                        print(f"entre a procesar el messageStamp")
                        
                        # ESTO es lo que se guarda como fecha real en la BD
                        rec["assetStatus"]["messageStamp_dt"] = dt_utc
                        
                except Exception as e:
                    print(f"⚠️ Error al convertir assetStatus.messageStamp: {message_stamp} -> {e}")

                geofence_status = rec.get("positionStatus", {}).get("geofenceStatus")
                message_id = rec.get("messageId")
                asset_name = rec.get("assetName")
                status = (geofence_status or "").strip().upper()

                # Determinar colección destino principal
                target_collection = positions_2 if asset_name == "FSKC623020600" else positions

                # 🟢 SIEMPRE guardar en histórico general
                target_collection.replace_one({"messageId": message_id}, rec, upsert=True)

                # 🔵 Si es evento de geocerca, también guardarlo en colección geocerca
                if status in ("ARRIVAL", "IN", "DEPARTURE"):
                    geocerca.replace_one({"messageId": message_id}, rec, upsert=True)

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
                # Si es la fecha de hoy, solo procesar hasta la hora actual
                limit_hour = 24
                if current == today_local:
                    now_hour = datetime.now().hour
                    # Redondea hacia arriba a la siguiente franja par (ej: 15 → 16)
                    limit_hour = (now_hour + 1) if (now_hour + 1) % 2 == 0 else (now_hour + 2)

                # Franjas de 2 horas hasta limit_hour
                for from_h in range(0, limit_hour, 2):
                    to_h = min(from_h + 2, limit_hour)
                    await fetch_and_store(date_s, from_h, to_h, token)

                # Guardar progreso solo si NO es hoy (para forzar refrescar hoy en próximos ciclos)
                if current < today_local:
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