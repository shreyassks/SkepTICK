from fastapi import APIRouter

from app.api.v1.endpoints import transcribe
from app.api.v1.endpoints import stock_tips
from app.api.v1.endpoints import wholetruth

v1_router = APIRouter()

v1_router.include_router(transcribe.router, prefix="/v1")
v1_router.include_router(stock_tips.router, prefix="/v1")
v1_router.include_router(wholetruth.router, prefix="/v1")