"""可自定义卡种 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.models.card_type import CardType
from app.models.user import User, UserRole
from app.api.auth import get_current_user

router = APIRouter(prefix="/card-types", tags=["卡种管理"])


class CardTypeCreate(BaseModel):
    category: str = "stored"
    total_times: int = 0
    price: float = 0
    valid_days: int = 30
    description: str = ""
    sort_order: int = 0


@router.get("")
def list_card_types(db: Session = Depends(get_db)):
    types = db.query(CardType).filter(CardType.is_active == True).order_by(CardType.sort_order).all()
    return {"card_types": [
        {"id": t.id, "name": t.name, "category": t.category, "total_times": t.total_times,
         "price": t.price, "valid_days": t.valid_days, "description": t.description}
        for t in types
    ]}


@router.post("")
def create_card_type(data: CardTypeCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role not in [UserRole.CORE_MANAGEMENT, UserRole.MANAGER]:
        raise HTTPException(status_code=403)
    ct = CardType(**data.model_dump())
    db.add(ct)
    db.commit()
    db.refresh(ct)
    return {"id": ct.id, "name": ct.name}


@router.put("/{type_id}")
def update_card_type(type_id: int, data: CardTypeCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ct = db.query(CardType).get(type_id)
    if not ct:
        raise HTTPException(status_code=404)
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(ct, k, v)
    db.commit()
    return {"message": "更新成功"}


@router.delete("/{type_id}")
def delete_card_type(type_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ct = db.query(CardType).get(type_id)
    if not ct:
        raise HTTPException(status_code=404)
    ct.is_active = False
    db.commit()
    return {"message": "已停用"}
