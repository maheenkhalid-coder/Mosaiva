from fastapi import FastAPI

app = FastAPI(title="Mosaiva Agent Service")


@app.get("/")
def agent_home():
    return {"message": "Hello from Agent"}