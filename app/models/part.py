# app/models/part.py
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class MetalPartBase(SQLModel):
    # Общие поля, которые используются и для создания, и для чтения
    author: str = Field(index=True)
    file_path: str
    creation_program: str
    # Добавим поле material позже для демонстрации миграции

# Модель таблицы в базе данных


class MetalPart(MetalPartBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # Уникальный номер детали
    part_number: int = Field(unique=True, index=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        # Автоматическое обновление при изменении записи
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )

# Схема для создания новой записи (входные данные API)
# Не включает id, part_number, created_at, updated_at, которые генерируются автоматически или сервером


class MetalPartCreate(MetalPartBase):
    pass  # Наследует все поля от MetalPartBase

# Схема для чтения записи (выходные данные API)
# Включает все поля, включая генерируемые


class MetalPartRead(MetalPartBase):
    id: int
    part_number: int
    created_at: datetime
    updated_at: datetime

# Схема для обновления записи (входные данные API)
# Все поля опциональны


class MetalPartUpdate(SQLModel):
    author: Optional[str] = None
    file_path: Optional[str] = None
    creation_program: Optional[str] = None
    # part_number не обновляем через этот эндпоинт, чтобы избежать конфликтов
    # created_at не обновляем
    # updated_at обновится автоматически
