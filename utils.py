from datetime import datetime, timedelta
import requests
from fastapi import HTTPException
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client['orbcomm_db']
tokens_collection = db['tokens']

def get_orbcomm_token():
    # Verificar si ya existe un token válido en la base de datos
    token_data = tokens_collection.find_one({"platform": "orbcomm"})
    if token_data:
        token = token_data['token']
        # Verificar si el token ha expirado
        if datetime.now() < token_data['expires_at']:
            return token  # Si el token es válido, lo usamos
        else:
            # Si el token ha expirado, lo refrescamos
            return refresh_token(token_data['refresh_token'])
    else:
        # Si no hay token en la base de datos, obtenemos uno nuevo
        return refresh_token()

def refresh_token(refresh_token: Optional[str] = None):
    url = "https://platform.orbcomm.com/SynB2BGatewayService/api/generateToken"
    headers = {"Content-Type": "application/json"}
    
    # Si hay un refresh_token, lo usamos, sino obtenemos uno nuevo
    data = {"refreshToken": refresh_token} if refresh_token else {"username": "YOUR_USERNAME", "password": "YOUR_PASSWORD"}
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access_token']
        expires_at = datetime.utcnow() + timedelta(seconds=token_data['expires_in'])  # El token expira en 'expires_in' segundos
        
        # Guardar el nuevo token en MongoDB
        tokens_collection.update_one(
            {"platform": "orbcomm"},
            {"$set": {"token": access_token, "expires_at": expires_at, "refresh_token": token_data['refresh_token']}},
            upsert=True
        )
        
        return access_token
    else:
        raise HTTPException(status_code=500, detail="Error al obtener el token de ORBCOMM")
