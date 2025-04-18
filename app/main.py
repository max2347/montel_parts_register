# app/main.py
from fastapi import FastAPI

from app.api.v1.api import api_router
from app.db.session import create_db_and_tables

# Запуск создания таблиц при старте (лучше делать через Alembic)
# @app.on_event("startup")
# def on_startup():
#     create_db_and_tables()

app = FastAPI(
    title="Metal Parts API",
    description="API для управления базой данных металлических деталей.",
    version="0.1.0"
)

# Подключаем роутер v1 с префиксом /api/v1
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Добро пожаловать в Metal Parts API!"}

# Если запускать напрямую через python main.py (не рекомендуется для продакшена)
# if __name__ == "__main__":
#     import uvicorn
#     # Обратите внимание: путь к app должен быть в формате "модуль:объект"
#     # В данном случае, если main.py в папке app, запуск из корня проекта будет:
#     # uvicorn app.main:app --reload
#     uvicorn.run(app, host="0.0.0.0", port=8000)
