import time
import requests

# URL de tu API local
API_URL = "http://127.0.0.1:8000/get_asset_data"

# Intervalo de espera entre solicitudes (en segundos)
WAIT_TIME = 5 * 60  # 5 minutos

def main():
    while True:
        try:
            print("🔄 Haciendo solicitud a la API de ORBCOMM...")
            response = requests.post(API_URL)

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "completed":
                    print("✅ No hay más datos que recuperar. Proceso completado.")
                    break
                else:
                    print("⏳ Datos descargados. Esperando 5 minutos antes del siguiente intento...")
                    time.sleep(WAIT_TIME)
            else:
                print(f"⚠️ Error {response.status_code}: {response.text}")
                print("🔁 Reintentando en 5 minutos...")
                time.sleep(WAIT_TIME)
        except Exception as e:
            print(f"❌ Error al conectar con la API: {e}")
            print("🔁 Reintentando en 5 minutos...")
            time.sleep(WAIT_TIME)

if __name__ == "__main__":
    main()
