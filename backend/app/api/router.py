from fastapi import APIRouter

from app.api.v1.routes import content, health, users

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(content.router, prefix="/content")
api_router.include_router(content.admin_router, prefix="/content")
