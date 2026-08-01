"""订单 API"""
from datetime import datetime
from typing import Optional
import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.models.order import Order, OrderType, OrderStatus
from app.models.user import User, UserRole
from app.models.member import Member
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
    """创建订单 — 参考球之道快速开单"""
    # 权限检查
    if user.role in [UserRole.COACH, UserRole.CUSTOMER]:
        raise HTTPException(status_code=403, detail="无权创建订单")

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
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """订单列表 — 根据角色过滤"""
    query = db.query(Order)

    # 多馆隔离
    if user.role == UserRole.CORE_MANAGEMENT:
        if venue_id:
            query = query.filter(Order.venue_id == venue_id)
    else:
        query = query.filter(Order.venue_id == user.venue_id)

    if status:
        query = query.filter(Order.status == status)
    if date:
        query = query.filter(Order.book_date == datetime.strptime(date, "%Y-%m-%d"))

    orders = query.order_by(Order.created_at.desc()).limit(100).all()
    return {"orders": [
        {"id": o.id, "order_no": o.order_no, "order_type": o.order_type.value,
         "status": o.status.value, "book_date": str(o.book_date.date()) if o.book_date else None,
         "start_time": o.start_time, "end_time": o.end_time,
         "field_id": o.field_id,
         "paid_amount": o.paid_amount, "payment_method": o.payment_method,
         "name": o.member.name if o.member else None,
         "phone": o.member.phone if o.member else None}
        for o in orders
    ]}


@router.put("/{order_id}/status")
def update_order_status(
    order_id: int,
    status: OrderStatus,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新订单状态 — 确认/签到/取消"""
    order = db.query(Order).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

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
    return {
        "id": order.id, "order_no": order.order_no,
        "order_type": order.order_type.value, "status": order.status.value,
        "venue_id": order.venue_id, "field_id": order.field_id, "member_id": order.member_id,
        "book_date": str(order.book_date.date()) if order.book_date else None,
        "start_time": order.start_time, "end_time": order.end_time,
        "original_amount": order.original_amount, "paid_amount": order.paid_amount,
        "payment_method": order.payment_method, "remark": order.remark,
    }
