# app/api/v1/endpoints/parts.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from sqlmodel import Session

from app.db.session import get_db
from app.crud import parts as crud_parts
from app.models.part import MetalPart, MetalPartCreate, MetalPartRead, MetalPartUpdate

router = APIRouter()


@router.post("/", response_model=MetalPartRead, status_code=status.HTTP_201_CREATED)
def create_new_part(
    *,
    db: Session = Depends(get_db),
    part_in: MetalPartCreate
):
    """
    Создает новую металлическую деталь.
    Номер детали присваивается автоматически.
    """
    try:
        part = crud_parts.create_part(db=db, part_data=part_in)
        return part
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Общая ошибка сервера
        print(f"Error creating part: {e}")  # Логирование ошибки
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/next_part_number/", response_model=dict)
def get_next_part_number(db: Session = Depends(get_db)):
    """
    Возвращает следующий доступный номер детали.
    """
    next_number = crud_parts.get_next_available_part_number(db)
    if next_number is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Доступные номера деталей закончились")
    return {"next_part_number": next_number}


@router.get("/", response_model=List[MetalPartRead])
def read_parts(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Получает список деталей.
    """
    parts = crud_parts.get_parts(db=db, skip=skip, limit=limit)
    return parts


@router.get("/{part_id}", response_model=MetalPartRead)
def read_part_by_id(
    part_id: int,
    db: Session = Depends(get_db)
):
    """
    Получает деталь по её ID.
    """
    part = crud_parts.get_part_by_id(db=db, part_id=part_id)
    if not part:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Деталь не найдена")
    return part


@router.put("/{part_id}", response_model=MetalPartRead)
def update_existing_part(
    *,
    db: Session = Depends(get_db),
    part_id: int,
    part_in: MetalPartUpdate
):
    """
    Обновляет существующую деталь.
    """
    updated_part = crud_parts.update_part(
        db=db, part_id=part_id, part_update_data=part_in)
    if not updated_part:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Деталь для обновления не найдена")
    return updated_part


# Можно вернуть просто status_code=204
@router.delete("/{part_id}", response_model=MetalPartRead)
def delete_existing_part(
    *,
    db: Session = Depends(get_db),
    part_id: int,
):
    """
    Удаляет деталь по ID.
    """
    deleted_part = crud_parts.delete_part(db=db, part_id=part_id)
    if not deleted_part:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Деталь для удаления не найдена")
    # Возвращаем удаленный объект для подтверждения, или можно вернуть пустой ответ
    return deleted_part
