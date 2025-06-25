from fastapi import APIRouter, HTTPException, Depends
import httpx

from ..auth.auth import get_current_user #Importamos para proteccion de rutas
proteccion_user = Depends(get_current_user) # Proteccion rutas

from ..models import Usuario #importamos para proteccion de rutas

router = APIRouter()



@router.get("/devicetrackgps/{deviceSN}")
async def get_devicetrackgps(
    deviceSN: str,
    current_user: Usuario = proteccion_user # Proteccion rutas 
):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://10.30.7.14:8000/positions/last/" + deviceSN)
            response.raise_for_status() 
            data = response.json()
            return data
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error desde servidor externo: {e.response.text}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"No se pudo conectar con el servidor externo: {str(e)}")