# backend/gateway/main.py
import httpx
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from backend.gateway.middleware.auth_middleware import get_current_user

app = FastAPI(title="Mosaiva Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/auth/login")
async def auth_login(payload: dict, response: Response):
    try:
        async with httpx.AsyncClient() as client:
            upstream = await client.post(
                f"{AUTH_SERVICE_URL}/login",
                json=payload,
                timeout=5.0,
            )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail="Auth service unavailable",
        ) from exc

    response.status_code = upstream.status_code

    # Pass the auth service's HttpOnly session cookie back through the gateway.
    set_cookie = upstream.headers.get("set-cookie")
    if set_cookie:
        response.headers["set-cookie"] = set_cookie

    return upstream.json()

@app.get("/api/me")
async def current_user(user: dict = Depends(get_current_user)):
    return user


@app.post("/auth/logout")
async def auth_logout(response: Response):
    try:
        async with httpx.AsyncClient() as client:
            upstream = await client.post(
                f"{AUTH_SERVICE_URL}/logout",
                timeout=5.0,
            )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail="Auth service unavailable",
        ) from exc

    response.status_code = upstream.status_code

    # Forward the auth service's cookie-clearing header to the browser.
    set_cookie = upstream.headers.get("set-cookie")
    if set_cookie:
        response.headers["set-cookie"] = set_cookie

    return upstream.json()