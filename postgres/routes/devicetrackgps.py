from fastapi import APIRouter, HTTPException
import httpx


router = APIRouter()



@router.get("/devicetrackgps")
async def get_devicetrackgps():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://10.30.7.14:8000/positions")
            response.raise_for_status()
            data = response.json()
        
        seen = set()
        unique_devices = []

        for item in data:
            asset_status = item.get("assetStatus", {})
            asset_name = asset_status.get("assetName")
            device_sn = asset_status.get("deviceSN")

            if asset_name and device_sn:
                key = (asset_name, device_sn)
                if key not in seen:
                    seen.add(key)
                    unique_devices.append({
                        "assetName": asset_name,
                        "deviceSN": device_sn
                    })

        return unique_devices

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error desde servidor externo: {e.response.text}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"No se pudo conectar con el servidor externo: {str(e)}")