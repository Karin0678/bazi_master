from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api.router import api_router

app = FastAPI(
    title="八字命理专家",
    description="传统八字命理分析 Web 应用",
    version="1.0.0",
)

# 挂载 API 路由
app.include_router(api_router, prefix="/api")

# 静态文件目录
STATIC_DIR = Path(__file__).parent / "static"

# 挂载静态文件
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def index():
    """返回主页"""
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/health")
async def health():
    return {"status": "ok", "service": "八字命理专家"}

