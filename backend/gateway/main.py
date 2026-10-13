# backend/gateway/main.py
import httpx
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Mosaiva Gateway")
AUTH_SERVICE_URL = "http://127.0.0.1:8001"


@app.get("/")
def root():
    return {"message": "Mosaiva API is running"}


@app.get("/auth")
async def auth_home():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AUTH_SERVICE_URL}/")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Auth service unavailable",
        ) from exc