from fastapi import APIRouter, Request, Response
from pydantic import BaseModel

from backend.services.auth.controllers.auth_controller import (
    login,
    logout as logout_controller,
)

router = APIRouter()


class LoginRequest(BaseModel):
    token: str


@router.post("/login")
async def login_route(request: LoginRequest, response: Response):
    return await login(request.token, response)


@router.post("/logout")
async def logout_route(request: Request, response: Response):
    return await logout_controller(
        request.cookies.get("session"),
        response,
    )