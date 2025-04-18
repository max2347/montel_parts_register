# app/crud/parts.py
from sqlmodel import Session, select, func
from typing import List, Optional

from app.models.part import MetalPart, MetalPartCreate, MetalPartUpdate

# Диапазон номеров деталей
MIN_PART_NUMBER = 10000
MAX_PART_NUMBER = 100000


def get_next_available_part_number(db: Session) -> Optional[int]:
    """Находит следующий доступный номер детали в диапазоне."""

    statement = select(func.max(MetalPart.part_number))
    result = db.exec(statement)  # Выполняем запрос

    # --- Используем .first() так как .scalar_one_or_none() недоступен ---
    first_row = result.first()  # Получаем первую строку (кортеж) или None
    if first_row:
        # Проверяем, что first_row не пустой и содержит хотя бы один элемент (сам максимум)
        if first_row[0] is not None:
            # Берем первый элемент из строки и преобразуем в int
            # func.max() может вернуть Decimal или другой тип в некоторых БД, int() безопаснее
            try:
                 max_part_number = int(first_row[0])
            except (ValueError, TypeError):
                 # Обработка случая, если значение не может быть преобразовано в int
                 print(
                     f"Warning: Could not convert max part number '{first_row[0]}' to int.")
                 # Решите, как обрабатывать эту ошибку - возможно, вернуть None или 0
                 max_part_number = None  # Или другое значение по умолчанию
        else:
            max_part_number = None # Если в базе максимальное значение NULL (столбец пуст)
    else:
        max_part_number = None  # Если строк нет (таблица пуста)
    # --- Конец блока с .first() ---

    if max_part_number is None:
        # Если деталей нет или была ошибка конвертации, начинаем с минимального номера
        next_number = MIN_PART_NUMBER
    else:
        next_number = max_part_number + 1

    # Проверяем выход за границы диапазона
    if next_number > MAX_PART_NUMBER:
        return None  # Номера закончились
    # Эту проверку можно убрать, если max_part_number всегда >= 0 или None
    # elif next_number < MIN_PART_NUMBER:
    #      return MIN_PART_NUMBER

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
