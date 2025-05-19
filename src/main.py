from fastapi import FastAPI
from app.api.v1.routes import api_v1_router

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Server, Open!"}

app.include_router(api_v1_router)