"""会员模型 — 平级会员制，可自定义卡种，支持人脸识别"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class MemberLevel(Base):
    """会员等级（参考球之道: 普通/银卡/金卡/钻石等）"""
    __tablename__ = "member_levels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, comment="等级名称")
    discount = Column(Float, default=1.0, comment="折扣率（1.0=无折扣）")
    min_recharge = Column(Float, default=0, comment="最低充值金额")
    min_consumption = Column(Float, default=0, comment="累计消费门槛")
    valid_months = Column(Integer, default=12, comment="有效期（月）")
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    description = Column(Text)

    members = relationship("Member", back_populates="level")


class Member(Base):
    """会员（参考球之道: 会员列表+通卡+资料配置）"""
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)
    level_id = Column(Integer, ForeignKey("member_levels.id"))

    # 基本信息
    name = Column(String(50), nullable=False, comment="姓名")
    phone = Column(String(20), nullable=False, comment="手机号（脱敏显示）")
    gender = Column(String(10), comment="性别")
    birthday = Column(DateTime, comment="生日")
    avatar = Column(String(500), comment="头像")

    # 账户信息（参考球之道扣费系统）
    balance = Column(Float, default=0, comment="账户余额")
    total_recharge = Column(Float, default=0, comment="累计充值")
    total_consumption = Column(Float, default=0, comment="累计消费")
    points = Column(Integer, default=0, comment="积分")

    # 通卡信息（参考球之道通卡会员）
    is_universal = Column(Boolean, default=False, comment="是否通卡会员")
    universal_expire = Column(DateTime, comment="通卡到期时间")

    # 人脸识别
    face_image = Column(Text, comment="人脸照片(base64)")
    face_descriptor = Column(Text, comment="人脸特征描述符(JSON)")

    # 状态
    is_active = Column(Boolean, default=True)
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    venue = relationship("Venue", back_populates="members")
    level = relationship("MemberLevel", back_populates="members")
    cards = relationship("MemberCard", back_populates="member", cascade="all, delete-orphan")


class MemberCard(Base):
    """会员卡（参考球之道: 办卡管理 —— 次卡/月卡/年卡等）"""
    __tablename__ = "member_cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    card_type = Column(String(30), nullable=False, comment="卡类型: times(次卡)/month(月卡)/year(年卡)")
    total_times = Column(Integer, default=0, comment="总次数（次卡）")
    used_times = Column(Integer, default=0, comment="已用次数")
    price = Column(Float, default=0, comment="购卡金额")
    start_date = Column(DateTime, comment="生效日期")
    end_date = Column(DateTime, comment="到期日期")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    member = relationship("Member", back_populates="cards")
