from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import SessionLocal
from ..auth.auth import get_current_user #Importamos para proteccion de rutas
from dotenv import load_dotenv
from typing import Dict, List
import asyncio
import httpx
import os

load_dotenv()

router = APIRouter()

ipServidor = os.getenv("IPSERVIDOR","http://10.30.7.14:8002")
fechaEntrega = "2025-09-25"

GPS_DEVICES = [
    {"numero_serie": "FSKC623020600", "modelo": "ORBCOMN"},
    {"numero_serie": "FJKB624330851", "modelo": "ORBCOMN"},
    {"numero_serie": "KAAB1242700077", "modelo": "ORBCOMN"},
    {"numero_serie": "0-4799154", "modelo": "globalmini"}
]

async def obtener_posicion_gps(
        client: httpx.AsyncClient, 
        dispositivo: Dict
    ) -> Dict:
    
    numero_serie = dispositivo["numero_serie"]
    modelo = dispositivo["modelo"]
    posicion_gps = None
    
    try:
        if modelo != "globalmini":
            url = f"{ipServidor}/positions/last/{numero_serie}"
            response = await client.get(url, timeout=10.0)
            response.raise_for_status() 
            
            data = response.json()
            if isinstance(data, list) and len(data) > 0 and data[0].get("positionStatus"):
                posicion_gps = {
                    "latitud": data[0]["positionStatus"]["latitude"],
                    "longitud": data[0]["positionStatus"]["longitude"],
                    "fecha": data[0]["positionStatus"]["priorDepartureTime"] if data[0]["positionStatus"]["priorDepartureTime"] else data[0]["assetStatus"]["messageStamp"]
                }
        else:
            url = f"{ipServidor}/globalMini/dataFecha/{fechaEntrega}"
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            
            data = response.json()
            if isinstance(data, dict) and "Latitude" in data and "Longitude" in data:
                posicion_gps = {
                    "latitud": data["Latitude"],
                    "longitud": data["Longitude"],
                    "fecha": data["time_stamp"]
                }
    except httpx.HTTPError as e:
        print(f"Error HTTP al obtener datos del GPS {numero_serie}: {e}")
    except Exception as e:
        print(f"Error inesperado al procesar datos del GPS {numero_serie}: {e}")
        
    return {
        "numero_serie": numero_serie,
        "modelo": modelo,
        "posicion": posicion_gps
    }

@router.get("/gps-todos")
async def obtener_todas_las_posiciones() -> List[Dict]:
    
    todas_las_posiciones = []
    async with httpx.AsyncClient() as client:
        
        tasks = [obtener_posicion_gps(client, dispositivo) for dispositivo in GPS_DEVICES]
        results = await asyncio.gather(*tasks)
        
        for result in results:
            if result["posicion"]:
                todas_las_posiciones.append({
                    "numero_serie": result["numero_serie"],
                    "modelo": result["modelo"],
                    "latitud": result["posicion"]["latitud"],
                    "longitud": result["posicion"]["longitud"],
                    "fecha": result["posicion"]["fecha"]
                })
                
    if not todas_las_posiciones:
        raise HTTPException(
            status_code=404,
            detail="No se pudo obtener la ubicación de ningún GPS. Revisa las configuraciones."
        )
        
    return todas_las_posiciones

