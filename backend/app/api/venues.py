"""场馆 & 场地 API"""
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.models.venue import Venue, Field, FieldType, FieldTimeTemplate, VenueStatus
from app.models.order import Order
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
    parent_field_id: Optional[int] = None
    sort_order: int = 0
    duration: int = 1

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
    """列出球馆 — 核心管理层和顾客看全部，其他人只看自己馆"""
    if user.role in [UserRole.CORE_MANAGEMENT] or user.venue_id is None:
        venues = db.query(Venue).filter(Venue.is_active == True).all()
    else:
        venues = db.query(Venue).filter(Venue.id == user.venue_id, Venue.is_active == True).all()
    return {"venues": [
        {"id": v.id, "name": v.name, "address": v.address, "phone": v.phone,
         "status": v.status.value, "business_hours": v.business_hours,
         "description": v.description, "district": v.district}
        for v in venues
    ]}


@router.get("/{venue_id}")
def get_venue(venue_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    venue = db.query(Venue).get(venue_id)
    if not venue:
        raise HTTPException(status_code=404, detail="球馆不存在")
    # 权限检查：核心管理层和未绑定球馆的用户（顾客）可看任意馆
    if user.role != UserRole.CORE_MANAGEMENT and user.venue_id is not None and venue.id != user.venue_id:
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
         "capacity": f.capacity, "parent_field_id": f.parent_field_id,
         "duration": f.default_duration or 1}
        for f in fields
    ]}


@router.post("/fields")
def create_field(data: FieldCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role not in [UserRole.CORE_MANAGEMENT, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="仅管理层可管理场地")
    payload = data.model_dump()
    payload["default_duration"] = payload.pop("duration", 1)
    field = Field(**payload)
    db.add(field)
    db.commit()
    db.refresh(field)
    return {"id": field.id, "name": field.name}


@router.put("/fields/{field_id}")
def update_field(field_id: int, data: FieldCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    field = db.query(Field).get(field_id)
    if not field:
        raise HTTPException(status_code=404)
    payload = data.model_dump(exclude_none=True)
    if "duration" in payload:
        payload["default_duration"] = payload.pop("duration")
    for k, v in payload.items():
        setattr(field, k, v)
    db.commit()
    return {"message": "更新成功"}


@router.delete("/fields/{field_id}")
def delete_field(field_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """删除场地（软删除，设为不可用）"""
    if user.role not in [UserRole.CORE_MANAGEMENT, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="仅管理层可删除场地")
    field = db.query(Field).get(field_id)
    if not field:
        raise HTTPException(status_code=404)
    field.is_active = False
    db.commit()
    return {"message": "已删除"}


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


class TimeConfigUpdate(BaseModel):
    usage_start: str = "09:00"
    usage_end: str = "22:00"
    peak_start: str = "18:00"
    peak_end: str = "21:00"


@router.put("/fields/{field_id}/time-config")
def update_time_config(
    field_id: int,
    data: TimeConfigUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """一键更新场地时段配置：删除旧模板，按新时段生成"""
    if user.role not in [UserRole.CORE_MANAGEMENT, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="仅管理层可修改时段")
    field = db.query(Field).get(field_id)
    if not field:
        raise HTTPException(status_code=404, detail="场地不存在")

    # 删除旧模板
    db.query(FieldTimeTemplate).filter(FieldTimeTemplate.field_id == field_id).delete()

    # 按营业时段生成逐小时模板
    start_h = int(data.usage_start.split(":")[0])
    end_h = int(data.usage_end.split(":")[0])
    peak_start_h = int(data.peak_start.split(":")[0])
    peak_end_h = int(data.peak_end.split(":")[0])

    for h in range(start_h, end_h):
        t = FieldTimeTemplate(
            field_id=field_id,
            start_time=f"{h:02d}:00",
            end_time=f"{h+1:02d}:00",
            is_peak=(peak_start_h <= h < peak_end_h),
            weekday=0,
        )
        db.add(t)

    db.commit()
    return {"message": f"已更新时段配置: {data.usage_start}-{data.usage_end}, 高峰{data.peak_start}-{data.peak_end}"}


# ──── 场地可用时段查询 ────
@router.get("/fields/{field_id}/availability")
def get_field_availability(
    field_id: int,
    date: str = Query(..., description="日期 YYYY-MM-DD"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """查询场地某天的可预约时段"""
    field = db.query(Field).get(field_id)
    if not field:
        raise HTTPException(status_code=404, detail="场地不存在")

    venue = field.venue
    try:
        book_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，应为 YYYY-MM-DD")

    # 查时段模板
    weekday = book_date.isoweekday()  # 1=Mon ... 7=Sun
    templates = db.query(FieldTimeTemplate).filter(
        FieldTimeTemplate.field_id == field_id,
        (FieldTimeTemplate.weekday == 0) | (FieldTimeTemplate.weekday == weekday),
    ).all()

    # 生成时段
    slots = []
    if templates:
        for t in templates:
            start_h = int(t.start_time.split(":")[0])
            end_h = int(t.end_time.split(":")[0])
            for h in range(start_h, end_h):
                slot_time = f"{h:02d}:00"
                slot_end = f"{h+1:02d}:00"
                is_peak = t.is_peak
                price = field.peak_price_per_hour if (is_peak and (field.peak_price_per_hour or 0) > 0) else field.price_per_hour
                # 去重（多个模板覆盖同一时段，peak 优先）
                existing = next((s for s in slots if s["time"] == slot_time), None)
                if existing:
                    if is_peak and not existing["is_peak"]:
                        existing["is_peak"] = True
                        existing["price"] = price
                    continue
                slots.append({"time": slot_time, "end_time": slot_end, "is_peak": is_peak, "price": price})
    else:
        # 无模板：用球馆营业时间，每小时一段
        hours_str = venue.business_hours or "09:00-22:00"
        parts = hours_str.split("-")
        try:
            open_h = int(parts[0].split(":")[0])
            close_h = int(parts[1].split(":")[0])
        except (IndexError, ValueError):
            open_h, close_h = 9, 22
        for h in range(open_h, close_h):
            slot_time = f"{h:02d}:00"
            slot_end = f"{h+1:02d}:00"
            slots.append({"time": slot_time, "end_time": slot_end, "is_peak": False, "price": field.price_per_hour})

    # 查已占用时段（含父子场地）
    conflict_field_ids = [field_id]
    if field.parent_field_id:
        conflict_field_ids.append(field.parent_field_id)
    children = db.query(Field).filter(Field.parent_field_id == field_id, Field.is_active == True).all()
    conflict_field_ids.extend([c.id for c in children])

    booked_orders = db.query(Order).filter(
        Order.field_id.in_(conflict_field_ids),
        Order.book_date == book_date,
        ~Order.status.in_(["cancelled", "refunded"]),
    ).all()

    booked_slots = set()
    for o in booked_orders:
        if o.start_time and o.end_time:
            sh = int(o.start_time.split(":")[0])
            eh = int(o.end_time.split(":")[0])
            for h in range(sh, eh):
                booked_slots.add(f"{h:02d}:00")

    # 标记已占 + 过期
    now = datetime.now()
    today = now.date()
    current_hour = now.hour
    for s in slots:
        s["booked"] = s["time"] in booked_slots
        s["expired"] = (book_date < today) or (book_date == today and int(s["time"].split(":")[0]) <= current_hour)

    return {
        "date": date,
        "field_id": field_id,
        "field_name": field.name,
        "price_per_hour": field.price_per_hour,
        "peak_price_per_hour": field.peak_price_per_hour,
        "slots": slots,
    }


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
            {"id": f.id, "name": f.name, "field_type": f.field_type.value,
             "price_per_hour": f.price_per_hour, "capacity": f.capacity,
             "duration": f.default_duration or 1}
            for f in fields
        ]
    }
