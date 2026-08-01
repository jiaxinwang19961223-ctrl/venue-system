"""场馆 & 场地 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.models.venue import Venue, Field, FieldType, FieldTimeTemplate, VenueStatus
from app.models.user import User, UserRole
from app.api.auth import get_current_user

router = APIRouter(prefix="/venues", tags=["场馆管理"])


# ──── Schema ────
class VenueCreate(BaseModel):
    name: str
    address: str = ""
    phone: str = ""
    description: str = ""
    business_hours: str = "09:00-22:00"
    district: str = ""

class VenueUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    business_hours: Optional[str] = None
    status: Optional[VenueStatus] = None

class FieldCreate(BaseModel):
    venue_id: int
    name: str
    field_type: FieldType = FieldType.OTHER
    price_per_hour: float = 0
    peak_price_per_hour: float = 0
    capacity: int = 0
    description: str = ""

class TimeTemplateCreate(BaseModel):
    field_id: int
    start_time: str
    end_time: str
    is_peak: bool = False
    weekday: int = 0


# ──── 球馆 CRUD ────
@router.get("")
def list_venues(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """列出球馆 — 核心管理层看全部，其他人只看自己馆"""
    if user.role in [UserRole.CORE_MANAGEMENT]:
        venues = db.query(Venue).filter(Venue.is_active == True).all()
    else:
        venues = db.query(Venue).filter(Venue.id == user.venue_id, Venue.is_active == True).all()
    return {"venues": [{"id": v.id, "name": v.name, "address": v.address, "status": v.status.value} for v in venues]}


@router.get("/{venue_id}")
def get_venue(venue_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    venue = db.query(Venue).get(venue_id)
    if not venue:
        raise HTTPException(status_code=404, detail="球馆不存在")
    # 权限检查
    if user.role != UserRole.CORE_MANAGEMENT and venue.id != user.venue_id:
        raise HTTPException(status_code=403, detail="无权访问该球馆")
    return venue_detail(venue, db)


@router.post("")
def create_venue(data: VenueCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != UserRole.CORE_MANAGEMENT:
        raise HTTPException(status_code=403, detail="仅核心管理层可创建球馆")
    venue = Venue(**data.model_dump())
    db.add(venue)
    db.commit()
    db.refresh(venue)
    return {"id": venue.id, "name": venue.name}


@router.put("/{venue_id}")
def update_venue(venue_id: int, data: VenueUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    venue = db.query(Venue).get(venue_id)
    if not venue:
        raise HTTPException(status_code=404, detail="球馆不存在")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(venue, k, v)
    db.commit()
    return {"message": "更新成功"}


# ──── 场地 CRUD ────
@router.get("/{venue_id}/fields")
def list_fields(venue_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    fields = db.query(Field).filter(Field.venue_id == venue_id, Field.is_active == True).order_by(Field.sort_order).all()
    return {"fields": [
        {"id": f.id, "name": f.name, "field_type": f.field_type.value,
         "price_per_hour": f.price_per_hour, "peak_price_per_hour": f.peak_price_per_hour,
         "capacity": f.capacity}
        for f in fields
    ]}


@router.post("/fields")
def create_field(data: FieldCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role not in [UserRole.CORE_MANAGEMENT, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="仅管理层可管理场地")
    field = Field(**data.model_dump())
    db.add(field)
    db.commit()
    db.refresh(field)
    return {"id": field.id, "name": field.name}


@router.put("/fields/{field_id}")
def update_field(field_id: int, data: FieldCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    field = db.query(Field).get(field_id)
    if not field:
        raise HTTPException(status_code=404)
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(field, k, v)
    db.commit()
    return {"message": "更新成功"}


# ──── 时段模板 ────
@router.get("/fields/{field_id}/time-templates")
def list_time_templates(field_id: int, db: Session = Depends(get_db)):
    templates = db.query(FieldTimeTemplate).filter(FieldTimeTemplate.field_id == field_id).all()
    return {"templates": [{"id": t.id, "start_time": t.start_time, "end_time": t.end_time, "is_peak": t.is_peak, "weekday": t.weekday} for t in templates]}


@router.post("/fields/time-templates")
def create_time_template(data: TimeTemplateCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    template = FieldTimeTemplate(**data.model_dump())
    db.add(template)
    db.commit()
    return {"id": template.id}


def venue_detail(venue: Venue, db: Session) -> dict:
    """组装球馆详情（含场地列表）"""
    fields = db.query(Field).filter(Field.venue_id == venue.id, Field.is_active == True).all()
    return {
        "id": venue.id,
        "name": venue.name,
        "address": venue.address,
        "phone": venue.phone,
        "description": venue.description,
        "business_hours": venue.business_hours,
        "status": venue.status.value,
        "district": venue.district,
        "fields": [
            {"id": f.id, "name": f.name, "field_type": f.field_type.value, "price_per_hour": f.price_per_hour}
            for f in fields
        ]
    }
