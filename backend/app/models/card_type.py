"""可自定义卡种模型 — 管理员自行创建，参考球之道开放度设计"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text
from app.core.database import Base


class CardType(Base):
    """卡种模板 — 管理员自行设计（次卡/月卡/年卡/任意自定义）"""
    __tablename__ = "card_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="卡种名称（如：羽毛球10次卡、篮球月卡）")
    category = Column(String(30), default="times", comment="类别: times(次卡)/month(月卡)/year(年卡)/custom(自定义)")

    total_times = Column(Integer, default=0, comment="总次数（次卡用）")
    price = Column(Float, default=0, comment="售价")
    valid_days = Column(Integer, default=30, comment="有效天数")

    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    description = Column(Text)
