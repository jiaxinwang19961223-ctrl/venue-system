"""订单 API"""
from datetime import datetime, timedelta
from typing import Optional
import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.models.order import Order, OrderType, OrderStatus
from app.models.user import User, UserRole
from app.models.member import Member
from app.models.venue import Field
from app.api.auth import get_current_user

router = APIRouter(prefix="/orders", tags=["订单管理"])


class OrderCreate(BaseModel):
    venue_id: int
    field_id: Optional[int] = None
    member_id: Optional[int] = None
    order_type: OrderType
    book_date: Optional[str] = None   # YYYY-MM-DD
    start_time: Optional[str] = None  # HH:MM
    end_time: Optional[str] = None    # HH:MM
    original_amount: float = 0
    discount_amount: float = 0
    paid_amount: float = 0
    payment_method: str = ""
    remark: str = ""


def generate_order_no() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S") + secrets.token_hex(4).upper()


@router.post("")
def create_order(data: OrderCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """创建订单 — 员工快速开单 / 顾客自助订场"""
    # 顾客只能订场
    if user.role == UserRole.CUSTOMER:
        if data.order_type != OrderType.FIELD_BOOK:
            raise HTTPException(status_code=403, detail="顾客只能预订场地")
        if not data.field_id or not data.book_date or not data.start_time:
            raise HTTPException(status_code=400, detail="缺少场地/日期/时段信息")

        field = db.query(Field).get(data.field_id)
        if not field:
            raise HTTPException(status_code=404, detail="场地不存在")

        # 冲突检测（含全场/半场互斥）
        try:
            book_date = datetime.strptime(data.book_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误")
        start_time = data.start_time
        end_h = int(start_time.split(":")[0]) + 1
        end_time = f"{end_h:02d}:00"

        # 需要检查的场地ID列表（本场地 + 父场地 + 子场地）
        conflict_field_ids = [data.field_id]
        if field.parent_field_id:
            conflict_field_ids.append(field.parent_field_id)
        # 子场地
        children = db.query(Field).filter(Field.parent_field_id == data.field_id, Field.is_active == True).all()
        conflict_field_ids.extend([c.id for c in children])

        conflict = db.query(Order).filter(
            Order.field_id.in_(conflict_field_ids),
            Order.book_date == book_date,
            Order.start_time < end_time,
            Order.end_time > start_time,
            ~Order.status.in_(["cancelled", "refunded"]),
        ).first()
        if conflict:
            raise HTTPException(status_code=400, detail="该时段已被预订")

        # 金额服务端计算
        price = field.price_per_hour
        # 查是否高峰时段
        from app.models.venue import FieldTimeTemplate
        weekday = book_date.isoweekday()
        peak_tpl = db.query(FieldTimeTemplate).filter(
            FieldTimeTemplate.field_id == data.field_id,
            (FieldTimeTemplate.weekday == 0) | (FieldTimeTemplate.weekday == weekday),
            FieldTimeTemplate.is_peak == True,
            FieldTimeTemplate.start_time <= start_time,
            FieldTimeTemplate.end_time >= end_time,
        ).first()
        if peak_tpl and (field.peak_price_per_hour or 0) > 0:
            price = field.peak_price_per_hour

        # 自动匹配会员
        member_id = None
        if user.phone:
            member = db.query(Member).filter(
                Member.phone == user.phone,
                Member.venue_id == data.venue_id,
                Member.is_active == True,
            ).first()
            if member:
                member_id = member.id

        order = Order(
            order_no=generate_order_no(),
            user_id=user.id,
            venue_id=data.venue_id,
            field_id=data.field_id,
            member_id=member_id,
            order_type=OrderType.FIELD_BOOK,
            book_date=book_date,
            start_time=start_time,
            end_time=end_time,
            duration=1.0,
            original_amount=price,
            paid_amount=0,
            payment_method="wechat",
            status=OrderStatus.PENDING,
            remark="顾客自助订场",
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        return {"id": order.id, "order_no": order.order_no, "amount": price, "end_time": end_time}

    # 教练无权
    if user.role == UserRole.COACH:
        raise HTTPException(status_code=403, detail="无权创建订单")

    # 员工正常开单（原逻辑）
    order = Order(
        order_no=generate_order_no(),
        user_id=user.id,
        **data.model_dump(),
    )
    if data.book_date:
        order.book_date = datetime.strptime(data.book_date, "%Y-%m-%d")

    db.add(order)
    db.commit()
    db.refresh(order)
    return {"id": order.id, "order_no": order.order_no}


@router.get("")
def list_orders(
    venue_id: Optional[int] = None,
    status: Optional[OrderStatus] = None,
    date: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """订单列表 — 根据角色过滤，分页"""
    query = db.query(Order)

    # 顾客只能看自己的订单
    if user.role == UserRole.CUSTOMER:
        query = query.filter(Order.user_id == user.id)
    # 多馆隔离
    elif user.role == UserRole.CORE_MANAGEMENT:
        if venue_id:
            query = query.filter(Order.venue_id == venue_id)
    else:
        query = query.filter(Order.venue_id == user.venue_id)

    if status:
        query = query.filter(Order.status == status)
    if date:
        query = query.filter(Order.book_date == datetime.strptime(date, "%Y-%m-%d"))

    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "orders": [
            {"id": o.id, "order_no": o.order_no, "order_type": o.order_type.value,
             "status": o.status.value, "book_date": str(o.book_date.date()) if o.book_date else None,
             "start_time": o.start_time, "end_time": o.end_time,
             "field_id": o.field_id,
             "field_name": o.field.name if o.field else None,
             "venue_name": o.venue.name if o.venue else None,
             "venue_id": o.venue_id,
             "paid_amount": o.paid_amount, "original_amount": o.original_amount,
             "payment_method": o.payment_method,
             "name": o.member.name if o.member else None,
             "phone": o.member.phone if o.member else None,
             "created_at": str(o.created_at)}
            for o in orders
        ]
    }


@router.put("/{order_id}/status")
def update_order_status(
    order_id: int,
    status: OrderStatus,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新订单状态 — 确认/签到/取消/顾客支付"""
    order = db.query(Order).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    # 顾客只能操作自己的订单
    if user.role == UserRole.CUSTOMER:
        if order.user_id != user.id:
            raise HTTPException(status_code=403, detail="无权操作此订单")
        # 顾客允许的操作：支付、取消自己的订单
        if status == OrderStatus.PAID:
            if order.status != OrderStatus.PENDING:
                raise HTTPException(status_code=400, detail="只能支付待付款订单")
            order.status = OrderStatus.PAID
            order.paid_amount = order.original_amount
            db.commit()
            return {"message": "支付成功"}
        elif status == OrderStatus.CANCELLED:
            if order.status not in [OrderStatus.PENDING, OrderStatus.PAID]:
                raise HTTPException(status_code=400, detail="只能取消待付款或已付款订单")
            order.status = OrderStatus.CANCELLED
            db.commit()
            return {"message": "订单已取消"}
        else:
            raise HTTPException(status_code=403, detail="无权执行此操作")

    # 权限：取消和退款需要管理层
    if status in [OrderStatus.CANCELLED, OrderStatus.REFUNDED]:
        if user.role not in [UserRole.CORE_MANAGEMENT, UserRole.MANAGER]:
            raise HTTPException(status_code=403, detail="仅管理层可取消/退款")

        # 自动退款：余额支付 → 退回余额（累计消费不扣回）
        if order.member_id and order.payment_method == "card" and order.paid_amount > 0:
            member = db.query(Member).get(order.member_id)
            if member:
                member.balance += order.paid_amount

    order.status = status
    db.commit()
    return {"message": f"订单状态已更新为{status.value}{'，已退回余额' if order.payment_method == 'card' and order.paid_amount > 0 else ''}"}


@router.get("/{order_id}")
def get_order(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(Order).get(order_id)
    if not order:
        raise HTTPException(status_code=404)
    # 顾客只能看自己的订单
    if user.role == UserRole.CUSTOMER and order.user_id != user.id:
        raise HTTPException(status_code=403, detail="无权查看此订单")
    return {
        "id": order.id, "order_no": order.order_no,
        "order_type": order.order_type.value, "status": order.status.value,
        "venue_id": order.venue_id, "field_id": order.field_id, "member_id": order.member_id,
        "book_date": str(order.book_date.date()) if order.book_date else None,
        "start_time": order.start_time, "end_time": order.end_time,
        "original_amount": order.original_amount, "paid_amount": order.paid_amount,
        "payment_method": order.payment_method, "remark": order.remark,
        "field_name": order.field.name if order.field else None,
        "venue_name": order.venue.name if order.venue else None,
    }
