# backend/gateway/main.py
import httpx
from fastapi import Depends, FastAPI, HTTPException, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
CHAT_SERVICE_URL = "http://127.0.0.1:8002"


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def root():
    return {"message": "Mosaiva API is running"}


@app.get("/auth")
async def auth_home():
    try:
        async with httpx.AsyncClient() as client:
            upstream = await client.get(f"{AUTH_SERVICE_URL}/")
            upstream.raise_for_status()
            return upstream.json()
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

    # Forward the auth service's HttpOnly session cookie to the browser.
    set_cookie = upstream.headers.get("set-cookie")
    if set_cookie:
        response.headers["set-cookie"] = set_cookie

    return upstream.json()


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


@app.get("/api/me")
async def current_user(user: dict = Depends(get_current_user)):
    return user


@app.post("/chat")
async def chat(payload: ChatRequest):
    try:
        async with httpx.AsyncClient() as client:
            upstream = await client.post(
                f"{CHAT_SERVICE_URL}/chat",
                json=payload.model_dump(),
                timeout=30.0,
            )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail="Chat service unavailable",
        ) from exc

    # Relay the chat service response and its status through the gateway.
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        media_type=upstream.headers.get("content-type"),
    )

CHAT_SERVICE_URL = "http://127.0.0.1:8002"


@app.api_route(
    "/api/chat/{chat_path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def proxy_chat(
    chat_path: str,
    request: Request,
    user: dict = Depends(get_current_user),
):
    user_id = user.get("userId")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user session")

    try:
        async with httpx.AsyncClient() as client:
            upstream = await client.request(
                method=request.method,
                url=f"{CHAT_SERVICE_URL}/{chat_path}",
                params=request.query_params,
                content=await request.body(),
                headers={"x-user-id": str(user_id)},
                timeout=30.0,
            )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail="Chat service unavailable",
        ) from exc

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        media_type=upstream.headers.get("content-type"),
    )

AGENT_SERVICE_URL = "http://127.0.0.1:8003"


@app.api_route(
    "/api/agent",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
@app.api_route(
    "/api/agent/{agent_path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def proxy_agent(
    request: Request,
    user: dict = Depends(get_current_user),
    agent_path: str = "",
):
    user_id = user.get("userId")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user session")

    target_url = f"{AGENT_SERVICE_URL}/{agent_path}"

    try:
        async with httpx.AsyncClient() as client:
            upstream = await client.request(
                method=request.method,
                url=target_url,
                params=request.query_params,
                content=await request.body(),
                headers={"x-user-id": str(user_id)},
                timeout=30.0,
            )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail="Agent service unavailable",
        ) from exc

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        media_type=upstream.headers.get("content-type"),
    )