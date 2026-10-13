# services/auth/main.py starts the auth service and defines its API routes.

from fastapi import FastAPI
from backend.services.auth.config.db import db

app = FastAPI(title="Mosaiva Auth Service")


@app.get("/")
def auth_home():
    return {"message": "Hello from Auth"}