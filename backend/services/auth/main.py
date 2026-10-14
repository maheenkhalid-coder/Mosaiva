from fastapi import FastAPI

from backend.services.auth.routes.auth_routes import router as auth_router

app = FastAPI(title="Mosaiva Auth Service")

app.include_router(auth_router)


@app.get("/")
def auth_home():
    return {"message": "Hello from Auth"}