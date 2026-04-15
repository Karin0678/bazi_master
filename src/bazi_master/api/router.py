from fastapi import APIRouter
from .bazi import router as bazi_router
from .analysis import router as analysis_router
from .chat import router as chat_router

api_router = APIRouter()

api_router.include_router(bazi_router, prefix="/bazi", tags=["八字计算"])
api_router.include_router(analysis_router, prefix="/analysis", tags=["命理分析"])
api_router.include_router(chat_router, prefix="/chat", tags=["AI对话"])
