"""订单模型 — 参考球之道场地订单+散客消费"""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.core.database import Base


class OrderType(str, enum.Enum):
    FIELD_BOOK = "field_book"       # 场地预订
    WALK_IN = "walk_in"             # 散客消费
    CARD_RECHARGE = "card_recharge" # 办卡/充值
    COURSE_BOOK = "course_book"     # 课程报名


class OrderStatus(str, enum.Enum):
    PENDING = "pending"         # 待支付
    PAID = "paid"               # 已支付
    CONFIRMED = "confirmed"     # 已确认
    CHECKED_IN = "checked_in"   # 已签到
    CANCELLED = "cancelled"     # 已取消
    REFUNDED = "refunded"       # 已退款


class Order(Base):
    """订单"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_no = Column(String(32), unique=True, nullable=False, comment="订单号")
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), comment="会员ID（可为空，散客）")
    field_id = Column(Integer, ForeignKey("fields.id"), comment="场地ID")
    user_id = Column(Integer, ForeignKey("users.id"), comment="操作员工ID")

    order_type = Column(SAEnum(OrderType), nullable=False)
    status = Column(SAEnum(OrderStatus), default=OrderStatus.PENDING)

    # 场地预订字段
    book_date = Column(DateTime, comment="预订日期")
    start_time = Column(String(10), comment="开始时间 HH:MM")
    end_time = Column(String(10), comment="结束时间 HH:MM")
    duration = Column(Float, default=1.0, comment="时长（小时）")

    # 金额
    original_amount = Column(Float, default=0, comment="原价")
    discount_amount = Column(Float, default=0, comment="折扣金额")
    paid_amount = Column(Float, default=0, comment="实付金额")
    payment_method = Column(String(20), comment="支付方式: wechat/alipay/cash/card")

    # 备注
    remark = Column(String(500))
    cancel_reason = Column(String(200))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关联
    venue = relationship("Venue", back_populates="orders")
    field = relationship("Field", back_populates="orders")
    member = relationship("Member")
    operator = relationship("User", foreign_keys=[user_id])
