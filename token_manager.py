# token_manager.py
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timezone
from fastapi import HTTPException
import requests
import os

load_dotenv()

class TokenManager:
    def __init__(self):
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.client = MongoClient(mongo_uri)
        self.db = self.client["orbcomm_db"]
        self.coll = self.db["tokens"]
        self.token_url = os.getenv("ORBCOMM_TOKEN_URL")
        self.user = os.getenv("ORBCOMM_USERNAME")
        self.pw = os.getenv("ORBCOMM_PASSWORD")

    async def generate(self):
        payload = {"username": self.user, "password": self.pw}
        resp = requests.post(self.token_url, json=payload)
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Error generando token: {resp.text}")
        data = resp.json()["data"]
        self.coll.delete_many({})
        self.coll.insert_one(data)
        return data["accessToken"]

    async def get(self):
        doc = self.coll.find_one()
        if doc:
            exp = doc.get("accessTokenexpireOn")
            if exp:
                exp_dt = datetime.fromisoformat(exp.replace("Z", "+00:00"))
                if datetime.now(timezone.utc) < exp_dt:
                    return doc["accessToken"]
        return await self.generate()
