"""会员 API — 参考球之道会员体系"""
from datetime import datetime, timedelta
import secrets
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from app.core.database import get_db
from app.models.member import Member, MemberLevel, MemberCard, CardModificationLog
from app.models.order import Order, OrderType, OrderStatus
from app.models.user import User, UserRole
from app.models.card_type import CardType
from app.api.auth import get_current_user

router = APIRouter(prefix="/members", tags=["会员管理"])


# ════════════════════════════════════════════
# Schemas
# ════════════════════════════════════════════

class MemberCreate(BaseModel):
    venue_id: int
    name: str
    phone: str
    gender: str = ""
    birthday: Optional[str] = None
    balance: float = 0
    face_image: Optional[str] = None
    face_descriptor: Optional[str] = None

class MemberUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[str] = None
    balance: Optional[float] = None
    is_active: Optional[bool] = None
    remark: Optional[str] = None
    face_image: Optional[str] = None
    face_descriptor: Optional[str] = None
    venue_id: Optional[int] = None

class MemberLevelCreate(BaseModel):
    name: str
    discount: float = 1.0
    min_recharge: float = 0
    valid_months: int = 12

class CardCreate(BaseModel):
    member_id: int
    card_type: str
    total_times: int = 0
    stored_value: float = 0
    price: float = 0
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class ConsumeRequest(BaseModel):
    amount: float = 0
    use_card: bool = False
    card_id: Optional[int] = None
    remark: str = ""

class UpdateCardValidityRequest(BaseModel):
    end_date: Optional[str] = None
    days: Optional[int] = None
    remark: str = ""

class SelfMemberCreate(BaseModel):
    venue_id: int
    name: str
    gender: str = ""
    birthday: Optional[str] = None

class BuyCardRequest(BaseModel):
    card_type_id: int


# ════════════════════════════════════════════
# 静态路径路由（必须放在 /{member_id} 之前！）
# ════════════════════════════════════════════

@router.get("/logs")
def list_member_logs(limit: int = 200, db: Session = Depends(get_db)):
    result = db.execute(text(
        "SELECT id, member_id, member_name, user_name, action, old_value, new_value, remark, created_at "
        "FROM member_logs ORDER BY created_at DESC LIMIT :lim"
    ), {"lim": limit})
    return {"logs": [
        {"id": r[0], "member_id": r[1], "member_name": r[2], "user_name": r[3],
         "field": r[4], "old_value": r[5], "new_value": r[6], "remark": r[7],
         "created_at": str(r[8]) if r[8] else None}
        for r in result
    ]}

@router.get("/card-logs")
def list_card_logs(
    member_id: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """查询卡修改记录"""
    query = db.query(CardModificationLog).order_by(CardModificationLog.created_at.desc())
    if member_id:
        query = query.filter(CardModificationLog.member_id == member_id)
    logs = query.limit(limit).all()
    return {
        "logs": [
            {
                "id": l.id, "card_id": l.card_id, "member_id": l.member_id,
                "member_name": l.member.name if l.member else "",
                "user_name": l.user.name if l.user else "",
                "field": l.field, "old_value": l.old_value, "new_value": l.new_value,
                "remark": l.remark, "created_at": str(l.created_at),
            }
            for l in logs
        ]
    }


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


# ════════════════════════════════════════════
# 顾客自助接口 — /me 必须在 /{member_id} 之前
# ════════════════════════════════════════════

@router.get("/me")
def get_my_member(
    venue_id: Optional[int] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """顾客查看自己的会员信息"""
    if not user.phone:
        raise HTTPException(status_code=400, detail="账号未绑定手机号")

    query = db.query(Member).filter(Member.phone == user.phone, Member.is_active == True)
    if venue_id:
        query = query.filter(Member.venue_id == venue_id)
    member = query.first()
    if not member:
        raise HTTPException(status_code=404, detail="还未办理会员")

    cards = db.query(MemberCard).filter(MemberCard.member_id == member.id).all()
    return {
        "id": member.id, "venue_id": member.venue_id,
        "venue_name": member.venue.name if member.venue else "",
        "name": member.name, "phone": member.phone, "gender": member.gender,
        "birthday": str(member.birthday.date()) if member.birthday else None,
        "balance": member.balance,
        "total_recharge": member.total_recharge or 0,
        "total_consumption": member.total_consumption or 0,
        "points": member.points or 0,
        "level_name": member.level.name if member.level else None,
        "cards": [
            {
                "id": c.id, "card_type": c.card_type,
                "total_times": c.total_times, "used_times": c.used_times,
                "stored_value": c.stored_value, "used_value": c.used_value,
                "price": c.price,
                "start_date": str(c.start_date.date()) if c.start_date else None,
                "end_date": str(c.end_date.date()) if c.end_date else None,
                "is_active": c.is_active,
            }
            for c in cards
        ],
    }


@router.post("/me")
def create_my_member(
    data: SelfMemberCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """顾客自助办理会员 — 幂等"""
    if not user.phone:
        raise HTTPException(status_code=400, detail="账号未绑定手机号")

    existing = db.query(Member).filter(
        Member.phone == user.phone, Member.venue_id == data.venue_id, Member.is_active == True,
    ).first()
    if existing:
        return {"id": existing.id, "name": existing.name, "message": "已是会员"}

    member = Member(
        venue_id=data.venue_id, name=data.name, phone=user.phone,
        gender=data.gender, balance=0,
    )
    if data.birthday:
        member.birthday = datetime.strptime(data.birthday, "%Y-%m-%d")
    db.add(member)
    db.commit()
    db.refresh(member)
    return {"id": member.id, "name": member.name, "message": "会员办理成功"}


@router.post("/me/cards")
def buy_card(
    data: BuyCardRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """顾客自助购买会员卡"""
    if not user.phone:
        raise HTTPException(status_code=400, detail="账号未绑定手机号")

    member = db.query(Member).filter(Member.phone == user.phone, Member.is_active == True).first()
    if not member:
        raise HTTPException(status_code=400, detail="请先办理会员")

    ct = db.query(CardType).get(data.card_type_id)
    if not ct or not ct.is_active:
        raise HTTPException(status_code=400, detail="卡种不存在或已下架")

    now = datetime.now()
    card = MemberCard(
        member_id=member.id,
        card_type=ct.category.value if hasattr(ct.category, 'value') else ct.category,
        total_times=ct.total_times if ct.category != "stored" else 0,
        stored_value=ct.total_times if ct.category == "stored" else 0,
        used_value=0, price=ct.price, start_date=now,
        end_date=now + timedelta(days=ct.valid_days) if ct.valid_days else None,
        is_active=True,
    )
    db.add(card)
    db.flush()

    order_no = datetime.now().strftime("%Y%m%d%H%M%S") + secrets.token_hex(4).upper()
    order = Order(
        order_no=order_no, venue_id=member.venue_id, member_id=member.id,
        user_id=user.id, order_type=OrderType.CARD_RECHARGE, status=OrderStatus.PAID,
        original_amount=ct.price, paid_amount=ct.price, payment_method="wechat",
        remark=f"顾客自助购卡: {ct.name}",
    )
    db.add(order)
    db.commit()
    db.refresh(card)

    return {"card_id": card.id, "order_id": order.id, "order_no": order.order_no, "message": "购卡成功"}


# ════════════════════════════════════════════
# 动态路径路由 /{member_id}/...（必须在 /me 之后）
# ════════════════════════════════════════════

@router.get("")
def list_members(
    venue_id: Optional[int] = None,
    keyword: str = "",
    page: int = 1,
    page_size: int = 10,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """会员列表 — 按角色隔离，分页"""
    query = db.query(Member).filter(Member.is_active == True)
    if user.role == UserRole.CORE_MANAGEMENT:
        if venue_id:
            query = query.filter(Member.venue_id == venue_id)
    else:
        query = query.filter(Member.venue_id == user.venue_id)
    if keyword:
        query = query.filter((Member.name.contains(keyword)) | (Member.phone.contains(keyword)))
    total = query.count()
    members = query.order_by(Member.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "page": page, "page_size": page_size, "members": [_format_member(m) for m in members]}


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


@router.delete("/{member_id}")
def delete_member(member_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role not in [UserRole.CORE_MANAGEMENT, UserRole.MANAGER]:
        raise HTTPException(status_code=403)
    member = db.query(Member).get(member_id)
    if not member: raise HTTPException(status_code=404)
    member.is_active = False
    # 记录删除日志
    from datetime import datetime
    db.execute(text(
        "INSERT INTO member_logs (member_id, member_name, user_id, user_name, action, old_value, new_value, created_at) "
        "VALUES (:mid, :mname, :uid, :uname, '删除', '活跃', '已删除', :now)"
    ), {"mid": member.id, "mname": member.name, "uid": user.id, "uname": user.name, "now": datetime.now()})
    db.commit()
    return {"message": "已删除"}

@router.put("/{member_id}")
def update_member(member_id: int, data: MemberUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role not in [UserRole.CORE_MANAGEMENT, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="仅管理层可编辑会员")
    member = db.query(Member).get(member_id)
    if not member:
        raise HTTPException(status_code=404)
    for k, v in data.model_dump(exclude_none=True).items():
        if k == 'birthday' and v and isinstance(v, str):
            try: v = datetime.strptime(v, '%Y-%m-%d')
            except: pass
        setattr(member, k, v)
    db.commit()
    return {"message": "更新成功"}


@router.get("/{member_id}/cards")
def list_cards(member_id: int, db: Session = Depends(get_db)):
    cards = db.query(MemberCard).filter(MemberCard.member_id == member_id).all()
    return {"cards": [
        {"id": c.id, "card_type": c.card_type, "total_times": c.total_times,
         "used_times": c.used_times, "price": c.price,
         "stored_value": c.stored_value or 0, "used_value": c.used_value or 0,
         "end_date": str(c.end_date.date()) if c.end_date else None, "is_active": c.is_active}
        for c in cards
    ]}


@router.get("/{member_id}/orders")
def get_member_orders(member_id: int, limit: int = 50, db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.member_id == member_id).order_by(Order.created_at.desc()).limit(limit).all()
    return {"orders": [
        {"id": o.id, "order_no": o.order_no, "order_type": o.order_type.value,
         "status": o.status.value, "book_date": str(o.book_date.date()) if o.book_date else None,
         "start_time": o.start_time, "end_time": o.end_time,
         "original_amount": o.original_amount, "paid_amount": o.paid_amount,
         "payment_method": o.payment_method, "remark": o.remark, "created_at": str(o.created_at)}
        for o in orders
    ]}


@router.post("/{member_id}/consume")
def member_consume(member_id: int, data: ConsumeRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """会员签到扣费"""
    member = db.query(Member).get(member_id)
    if not member:
        raise HTTPException(status_code=404, detail="会员不存在")

    paid_amount = data.amount
    payment_method = "card"

    if data.use_card and data.card_id:
        card = db.query(MemberCard).filter(MemberCard.id == data.card_id, MemberCard.member_id == member_id).first()
        if not card:
            raise HTTPException(status_code=404, detail="会员卡不存在")
        if not card.is_active:
            raise HTTPException(status_code=400, detail="卡已失效")
        if card.card_type == "stored":
            remaining = (card.stored_value or 0) - (card.used_value or 0)
            if remaining < data.amount:
                raise HTTPException(status_code=400, detail=f"储值卡余额不足（剩余: ¥{remaining:.2f}）")
            card.used_value = (card.used_value or 0) + data.amount
        else:
            if card.used_times >= card.total_times:
                raise HTTPException(status_code=400, detail="卡次数已用完")
            card.used_times += 1
            paid_amount = 0
    else:
        if member.balance < data.amount:
            raise HTTPException(status_code=400, detail=f"余额不足（当前: ¥{member.balance:.2f}）")
        member.balance -= data.amount
        member.total_consumption = (member.total_consumption or 0) + data.amount

    order = Order(
        order_no=datetime.now().strftime("%Y%m%d%H%M%S") + secrets.token_hex(4).upper(),
        venue_id=member.venue_id, member_id=member.id, user_id=user.id,
        order_type="walk_in", status="checked_in",
        paid_amount=paid_amount, original_amount=data.amount,
        payment_method=payment_method, remark=data.remark or "签到扣费",
    )
    db.add(order)
    db.commit()
    db.refresh(member)
    return {"message": "签到成功", "balance": member.balance, "total_consumption": member.total_consumption}


@router.put("/{member_id}/cards/{card_id}/validity")
def update_card_validity(
    member_id: int, card_id: int, data: UpdateCardValidityRequest,
    user: User = Depends(get_current_user), db: Session = Depends(get_db),
):
    """手动修改卡有效期，自动记录修改日志"""
    card = db.query(MemberCard).filter(MemberCard.id == card_id, MemberCard.member_id == member_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="会员卡不存在")

    old_end = str(card.end_date.date()) if card.end_date else "无"

    if data.end_date:
        card.end_date = datetime.strptime(data.end_date, "%Y-%m-%d")
        new_end = data.end_date
    elif data.days is not None:
        base = card.end_date if card.end_date else datetime.now()
        card.end_date = base + timedelta(days=data.days)
        new_end = card.end_date.strftime("%Y-%m-%d")
    else:
        raise HTTPException(status_code=400, detail="请提供 end_date 或 days")

    log = CardModificationLog(
        card_id=card.id, member_id=member_id, user_id=user.id,
        field="end_date", old_value=old_end, new_value=new_end,
        remark=data.remark or f"手动修改有效期: {old_end} → {new_end}",
    )
    db.add(log)
    db.commit()
    return {"message": "有效期已更新", "old": old_end, "new": new_end}


# ════════════════════════════════════════════
# 辅助方法
# ════════════════════════════════════════════

def _format_member(m: Member) -> dict:
    from app.core.database import SessionLocal
    db = SessionLocal()
    last_order = db.query(Order).filter(
        Order.member_id == m.id, Order.status.in_(["paid", "confirmed", "checked_in"])
    ).order_by(Order.created_at.desc()).first()
    last_consume_time = str(last_order.created_at) if last_order else None
    active_cards = [c for c in m.cards if c.is_active and (not c.end_date or c.end_date > datetime.now())]
    primary_card = active_cards[0] if active_cards else None
    card_types_str = ", ".join(set(c.card_type for c in active_cards)) if active_cards else None
    db.close()

    return {
        "id": m.id, "name": m.name, "phone": m.phone, "gender": m.gender,
        "birthday": str(m.birthday.date()) if m.birthday else None,
        "balance": m.balance, "total_recharge": m.total_recharge,
        "total_consumption": m.total_consumption,
        "face_image": m.face_image, "face_descriptor": m.face_descriptor,
        "venue_id": m.venue_id, "is_active": m.is_active,
        "card_types": card_types_str,
        "card_remaining": (primary_card.total_times - primary_card.used_times) if primary_card and primary_card.card_type == "times" else None,
        "card_expire": str(primary_card.end_date.date()) if primary_card and primary_card.end_date else None,
        "card_end_date": str(primary_card.end_date) if primary_card and primary_card.end_date else None,
        "card_start_date": str(primary_card.start_date) if primary_card and primary_card.start_date else None,
        "last_consume_time": last_consume_time,
    }


def _format_member_detail(m: Member) -> dict:
    return {
        **{k: v for k, v in m.__dict__.items() if not k.startswith("_")},
        "level_name": m.level.name if m.level else None,
        "phone": m.phone[:3] + "****" + m.phone[-4:] if len(m.phone) >= 7 else m.phone,
    }
