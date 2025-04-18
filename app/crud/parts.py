# app/crud/parts.py
from sqlmodel import Session, select, func
from typing import List, Optional

from app.models.part import MetalPart, MetalPartCreate, MetalPartUpdate

# Диапазон номеров деталей
MIN_PART_NUMBER = 10000
MAX_PART_NUMBER = 100000


def get_next_available_part_number(db: Session) -> Optional[int]:
    """Находит следующий доступный номер детали в диапазоне."""
    # Находим максимальный существующий номер детали
    max_part_number = db.exec(
        select(func.max(MetalPart.part_number))).scalar_one_or_none()

    if max_part_number is None:
        # Если деталей нет, начинаем с минимального номера
        next_number = MIN_PART_NUMBER
    else:
        next_number = max_part_number + 1

    if next_number > MAX_PART_NUMBER:
        # Если превысили максимальный номер, свободных номеров нет
        return None
    elif next_number < MIN_PART_NUMBER:
        # Если вдруг максимальный был меньше минимального (не должно быть, но на всякий)
        return MIN_PART_NUMBER

    # В реальном приложении может потребоваться проверка на "дыры" в нумерации,
    # но для простоты пока предполагаем последовательную нумерацию.
    return next_number


def create_part(db: Session, part_data: MetalPartCreate) -> MetalPart:
    """Создает новую запись о детали с уникальным номером."""
    next_part_number = get_next_available_part_number(db)
    if next_part_number is None:
        raise ValueError("Нет доступных номеров деталей в заданном диапазоне.")

    # Создаем объект MetalPart с данными из part_data и присвоенным номером
    db_part = MetalPart(**part_data.model_dump(), part_number=next_part_number)

    db.add(db_part)
    db.commit()
    db.refresh(db_part)
    return db_part


def get_part_by_id(db: Session, part_id: int) -> Optional[MetalPart]:
    """Получает деталь по её ID."""
    part = db.get(MetalPart, part_id)
    return part


def get_parts(db: Session, skip: int = 0, limit: int = 100) -> List[MetalPart]:
    """Получает список деталей с пагинацией."""
    statement = select(MetalPart).offset(skip).limit(limit)
    parts = db.exec(statement).all()
    return parts


def update_part(db: Session, part_id: int, part_update_data: MetalPartUpdate) -> Optional[MetalPart]:
    """Обновляет данные существующей детали."""
    db_part = get_part_by_id(db, part_id)
    if not db_part:
        return None

    # Получаем данные для обновления, исключая неустановленные (None) значения
    update_data = part_update_data.model_dump(exclude_unset=True)

    # Обновляем поля объекта db_part
    for key, value in update_data.items():
        setattr(db_part, key, value)

    # Поле updated_at обновится автоматически благодаря onupdate в модели (если СУБД поддерживает)
    # или его можно установить вручную перед коммитом:
    # from datetime import datetime
    # db_part.updated_at = datetime.utcnow()

    db.add(db_part)
    db.commit()
    db.refresh(db_part)
    return db_part


def delete_part(db: Session, part_id: int) -> Optional[MetalPart]:
    """Удаляет деталь по ID."""
    db_part = get_part_by_id(db, part_id)
    if not db_part:
        return None

    db.delete(db_part)
    db.commit()
    # Возвращаем удаленный объект (или можно просто вернуть True/None)
    return db_part
