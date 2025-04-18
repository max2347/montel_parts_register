# app/db/session.py
import os
from typing import Generator
from sqlmodel import create_engine, Session, SQLModel
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("Необходимо установить переменную окружения DATABASE_URL")

# Используем connect_args для SQLite
connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

# Функция для создания таблиц (но лучше использовать Alembic)


def create_db_and_tables():
    # В реальном проекте лучше использовать Alembic для управления схемой БД
    # Эту функцию можно вызвать один раз для первоначального создания,
    # но для всех последующих изменений используется Alembic.
    # SQLModel.metadata.create_all(engine) # Закомментировано, т.к. используем Alembic
    print("Создание таблиц пропущено, используйте 'alembic upgrade head'.")


# Зависимость FastAPI для получения сессии БД
def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
