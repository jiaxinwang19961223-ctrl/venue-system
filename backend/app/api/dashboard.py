"""Dashboard API — 今日概览（员工小程序首页）"""
from datetime import datetime, date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.order import Order, OrderStatus
from app.models.member import Member
from app.models.user import User, UserRole
from app.models.venue import Venue, Field
from app.api.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["数据概览"])


@router.get("/today")
def get_today_dashboard(
    venue_id: Optional[int] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """今日概览 — 按角色返回当前球馆今日数据"""
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    # 确定查询范围
    if user.role == UserRole.CORE_MANAGEMENT:
        if venue_id:
            venue_ids = [venue_id]
        else:
            venues = db.query(Venue.id).filter(Venue.is_active == True).all()
            venue_ids = [v[0] for v in venues]
    elif user.role == UserRole.COACH:
        # 教练只看自己的课程（暂简化：看所属球馆）
        venue_ids = [user.venue_id] if user.venue_id else []
    else:
        venue_ids = [user.venue_id] if user.venue_id else []

    if not venue_ids:
        return _empty_dashboard()

    # 今日订单
    today_orders = db.query(Order).filter(
        Order.venue_id.in_(venue_ids),
        Order.created_at >= today_start,
        Order.created_at <= today_end,
    )

    order_count = today_orders.count()
    paid_total = db.query(func.coalesce(func.sum(Order.paid_amount), 0)).filter(
        Order.venue_id.in_(venue_ids),
        Order.created_at >= today_start,
        Order.created_at <= today_end,
        Order.status.in_([OrderStatus.PAID, OrderStatus.CONFIRMED, OrderStatus.CHECKED_IN]),
    ).scalar()

    # 今日场地预订数
    field_book_count = today_orders.filter(
        Order.order_type == "field_book",
        ~Order.status.in_(["cancelled", "refunded"]),
    ).count()

    # 今日散客消费
    walk_in_total = db.query(func.coalesce(func.sum(Order.paid_amount), 0)).filter(
        Order.venue_id.in_(venue_ids),
        Order.created_at >= today_start,
        Order.created_at <= today_end,
        Order.order_type == "walk_in",
        Order.status == OrderStatus.CHECKED_IN,
    ).scalar()

    # 场地占用率
    total_fields = db.query(func.count(Field.id)).filter(
        Field.venue_id.in_(venue_ids),
        Field.is_active == True,
    ).scalar() or 0

    booked_fields = db.query(func.count(func.distinct(Order.field_id))).filter(
        Order.venue_id.in_(venue_ids),
        Order.book_date == today,
        Order.field_id.isnot(None),
        ~Order.status.in_(["cancelled", "refunded"]),
    ).scalar() or 0

    occupancy = round(booked_fields / total_fields * 100) if total_fields > 0 else 0

    # 今日活跃会员（有过订单的）
    active_members = db.query(func.count(func.distinct(Order.member_id))).filter(
        Order.venue_id.in_(venue_ids),
        Order.created_at >= today_start,
        Order.created_at <= today_end,
        Order.member_id.isnot(None),
    ).scalar() or 0

    # 最近10条订单
    recent_orders = today_orders.order_by(Order.created_at.desc()).limit(10).all()

    return {
        "date": str(today),
        "venue_ids": venue_ids,
        "stats": {
            "order_count": order_count,
            "paid_total": round(paid_total, 2),
            "field_book_count": field_book_count,
            "walk_in_total": round(walk_in_total, 2),
            "occupancy": occupancy,
            "active_members": active_members,
            "total_fields": total_fields,
        },
        "recent_orders": [
            {
                "id": o.id, "order_no": o.order_no,
                "order_type": o.order_type.value,
                "status": o.status.value,
                "paid_amount": o.paid_amount,
                "field_name": o.field.name if o.field else None,
                "member_name": o.member.name if o.member else None,
                "start_time": o.start_time,
                "end_time": o.end_time,
                "created_at": str(o.created_at),
            }
            for o in recent_orders
        ],
    }


def _empty_dashboard():
    return {
        "date": str(date.today()),
        "venue_ids": [],
        "stats": {
            "order_count": 0, "paid_total": 0,
            "field_book_count": 0, "walk_in_total": 0,
            "occupancy": 0, "active_members": 0, "total_fields": 0,
        },
        "recent_orders": [],
    }
