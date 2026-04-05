from fastapi import APIRouter
from .routes import user, webhook

api_router = APIRouter()

api_router.include_router(user.router)
api_router.include_router(webhook.router)