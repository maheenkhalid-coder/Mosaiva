from fastapi import FastAPI

from backend.services.chat.routes.chat_routes import router as chat_router

app = FastAPI(title="Mosaiva Chat Service")
app.include_router(chat_router)


@app.get("/")
def chat_home():
    return {"message": "Hello from Chat"}