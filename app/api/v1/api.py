# app/api/v1/api.py
from fastapi import APIRouter

from app.api.v1.endpoints import parts

api_router = APIRouter()

# Подключаем роутер для деталей с префиксом /parts
api_router.include_router(parts.router, prefix="/parts", tags=["parts"])

# Сюда можно будет добавлять другие роутеры (например, /users, /orders)
