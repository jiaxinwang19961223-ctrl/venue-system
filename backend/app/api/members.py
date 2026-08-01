"""会员 API — 参考球之道会员体系"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.models.member import Member, MemberLevel, MemberCard
from app.models.order import Order
from app.models.user import User, UserRole
from app.api.auth import get_current_user

router = APIRouter(prefix="/members", tags=["会员管理"])


# ──── Schema ────
class MemberCreate(BaseModel):
    venue_id: int
    name: str
    phone: str
    gender: str = ""
    birthday: Optional[str] = None
    balance: float = 0

class MemberUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    balance: Optional[float] = None
    is_active: Optional[bool] = None
    remark: Optional[str] = None
    face_image: Optional[str] = None
    face_descriptor: Optional[str] = None

class MemberLevelCreate(BaseModel):
    name: str
    discount: float = 1.0
    min_recharge: float = 0
    valid_months: int = 12

class CardCreate(BaseModel):
    member_id: int
    card_type: str  # times/month/year
    total_times: int = 0
    price: float = 0
    start_date: Optional[str] = None
    end_date: Optional[str] = None


# ──── 会员 CRUD ────
@router.get("")
def list_members(
    venue_id: Optional[int] = None,
    keyword: str = "",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """会员列表 — 按角色隔离"""
    query = db.query(Member)

    if user.role == UserRole.CORE_MANAGEMENT:
        if venue_id:
            query = query.filter(Member.venue_id == venue_id)
    else:
        query = query.filter(Member.venue_id == user.venue_id)

    if keyword:
        query = query.filter(
            (Member.name.contains(keyword)) | (Member.phone.contains(keyword))
        )

    members = query.order_by(Member.created_at.desc()).limit(100).all()
    return {"members": [_format_member(m) for m in members]}


@router.get("/{member_id}")
def get_member(member_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    member = db.query(Member).get(member_id)
    if not member:
        raise HTTPException(status_code=404, detail="会员不存在")
    return _format_member_detail(member)


@router.post("")
def create_member(data: MemberCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role not in [UserRole.CORE_MANAGEMENT, UserRole.MANAGER, UserRole.RECEPTION]:
        raise HTTPException(status_code=403, detail="无权创建会员")

    member = Member(**data.model_dump())
    if data.birthday:
        member.birthday = datetime.strptime(data.birthday, "%Y-%m-%d")
    db.add(member)
    db.commit()
    db.refresh(member)
    return {"id": member.id, "name": member.name}


@router.put("/{member_id}")
def update_member(member_id: int, data: MemberUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role not in [UserRole.CORE_MANAGEMENT, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="仅管理层可编辑会员")
    member = db.query(Member).get(member_id)
    if not member:
        raise HTTPException(status_code=404)
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(member, k, v)
    db.commit()
    return {"message": "更新成功"}


# ──── 会员等级 ────
@router.get("/levels/list")
def list_levels(db: Session = Depends(get_db)):
    levels = db.query(MemberLevel).filter(MemberLevel.is_active == True).order_by(MemberLevel.sort_order).all()
    return {"levels": [{"id": l.id, "name": l.name, "discount": l.discount} for l in levels]}


@router.post("/levels")
def create_level(data: MemberLevelCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role not in [UserRole.CORE_MANAGEMENT, UserRole.MANAGER]:
        raise HTTPException(status_code=403)
    level = MemberLevel(**data.model_dump())
    db.add(level)
    db.commit()
    return {"id": level.id, "name": level.name}


# ──── 办卡 ────
@router.post("/cards")
def create_card(data: CardCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role not in [UserRole.CORE_MANAGEMENT, UserRole.MANAGER, UserRole.RECEPTION]:
        raise HTTPException(status_code=403)
    card = MemberCard(**data.model_dump())
    if data.start_date:
        card.start_date = datetime.strptime(data.start_date, "%Y-%m-%d")
    if data.end_date:
        card.end_date = datetime.strptime(data.end_date, "%Y-%m-%d")
    db.add(card)
    db.commit()
    return {"id": card.id, "card_type": card.card_type}


@router.get("/{member_id}/cards")
def list_cards(member_id: int, db: Session = Depends(get_db)):
    cards = db.query(MemberCard).filter(MemberCard.member_id == member_id).all()
    return {"cards": [
        {"id": c.id, "card_type": c.card_type, "total_times": c.total_times,
         "used_times": c.used_times, "price": c.price,
         "end_date": str(c.end_date.date()) if c.end_date else None,
         "is_active": c.is_active}
        for c in cards
    ]}


# ──── 消费记录 ────
@router.get("/{member_id}/orders")
def get_member_orders(member_id: int, limit: int = 50, db: Session = Depends(get_db)):
    orders = db.query(Order).filter(
        Order.member_id == member_id
    ).order_by(Order.created_at.desc()).limit(limit).all()
    return {"orders": [
        {"id": o.id, "order_no": o.order_no, "order_type": o.order_type.value,
         "status": o.status.value, "book_date": str(o.book_date.date()) if o.book_date else None,
         "start_time": o.start_time, "end_time": o.end_time,
         "original_amount": o.original_amount, "paid_amount": o.paid_amount,
         "payment_method": o.payment_method, "remark": o.remark,
         "created_at": str(o.created_at)}
        for o in orders
    ]}


class ConsumeRequest(BaseModel):
    amount: float = 0
    use_card: bool = False
    card_id: Optional[int] = None
    remark: str = ""


@router.post("/{member_id}/consume")
def member_consume(member_id: int, data: ConsumeRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """会员签到扣费"""
    member = db.query(Member).get(member_id)
    if not member:
        raise HTTPException(status_code=404, detail="会员不存在")

    order_type = "walk_in"
    paid_amount = data.amount
    payment_method = "card"

    if data.use_card and data.card_id:
        card = db.query(MemberCard).filter(MemberCard.id == data.card_id, MemberCard.member_id == member_id).first()
        if not card:
            raise HTTPException(status_code=404, detail="会员卡不存在")
        if not card.is_active:
            raise HTTPException(status_code=400, detail="卡已失效")

        if card.card_type == "stored":
            # 储值卡：扣自定义金额
            remaining = (card.stored_value or 0) - (card.used_value or 0)
            if remaining < data.amount:
                raise HTTPException(status_code=400, detail=f"储值卡余额不足（剩余: ¥{remaining:.2f}）")
            card.used_value = (card.used_value or 0) + data.amount
            paid_amount = data.amount
        else:
            # 次卡/月卡：扣次
            if card.used_times >= card.total_times:
                raise HTTPException(status_code=400, detail="卡次数已用完")
            card.used_times += 1
            paid_amount = 0
    else:
        # 余额扣费
        if member.balance < data.amount:
            raise HTTPException(status_code=400, detail=f"余额不足（当前: ¥{member.balance:.2f}）")
        member.balance -= data.amount
        member.total_consumption = (member.total_consumption or 0) + data.amount
        payment_method = "card"

    import secrets
    from datetime import datetime
    order = Order(
        order_no=datetime.now().strftime("%Y%m%d%H%M%S") + secrets.token_hex(4).upper(),
        venue_id=member.venue_id,
        member_id=member.id,
        user_id=user.id,
        order_type=order_type,
        status="checked_in",
        paid_amount=paid_amount,
        original_amount=data.amount,
        payment_method=payment_method,
        remark=data.remark or "签到扣费",
    )
    db.add(order)
    db.commit()
    db.refresh(member)
    return {"message": "签到成功", "balance": member.balance, "total_consumption": member.total_consumption}


def _format_member(m: Member) -> dict:
    # 获取最近消费时间
    from app.models.order import Order
    from app.core.database import SessionLocal
    db = SessionLocal()
    last_order = db.query(Order).filter(Order.member_id == m.id, Order.status.in_(["paid","confirmed","checked_in"])).order_by(Order.created_at.desc()).first()
    last_consume_time = str(last_order.created_at) if last_order else None
    # 获取有效卡信息
    active_cards = [c for c in m.cards if c.is_active and (not c.end_date or c.end_date > datetime.now())]
    primary_card = active_cards[0] if active_cards else None
    card_types_str = ", ".join(set(c.card_type for c in active_cards)) if active_cards else None
    db.close()

    return {
        "id": m.id, "name": m.name,
        "phone": m.phone,
        "gender": m.gender,
        "balance": m.balance, "total_recharge": m.total_recharge,
        "total_consumption": m.total_consumption,
        "face_image": m.face_image,
        "face_descriptor": m.face_descriptor,
        "venue_id": m.venue_id,
        "is_active": m.is_active,
        # 球之道风格额外字段
        "card_types": card_types_str,
        "card_remaining": (primary_card.total_times - primary_card.used_times) if primary_card and primary_card.card_type == "times" else None,
        "card_expire": str(primary_card.end_date.date()) if primary_card and primary_card.end_date else None,
        "last_consume_time": last_consume_time,
    }


def _format_member_detail(m: Member) -> dict:
    return {
        **{k: v for k, v in m.__dict__.items() if not k.startswith("_")},
        "level_name": m.level.name if m.level else None,
        "phone": m.phone[:3] + "****" + m.phone[-4:] if len(m.phone) >= 7 else m.phone,
    }
