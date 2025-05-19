from fastapi import APIRouter
from src.app.api.v1.endpoints.llm import router as llm_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(llm_router)