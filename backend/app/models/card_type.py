"""可自定义卡种模型 — 管理员自行创建，参考球之道开放度设计"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class CardType(Base):
    """卡种模板 — 管理员自行设计（次卡/月卡/年卡/任意自定义）"""
    __tablename__ = "card_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=True, comment="所属球馆")
    name = Column(String(100), nullable=True, comment="卡种名称（空则自动生成）")
    category = Column(String(30), default="stored", comment="类别: stored(储值卡)/month(月卡)/season(季卡)/year(年卡)/custom(自定义)")
    total_times = Column(Integer, default=0, comment="总次数（储值卡=储值金额）")
    bonus_amount = Column(Float, default=0, comment="赠送金额（储值卡）")
    price = Column(Float, default=0, comment="售价（储值卡=储值金额）")
    valid_days = Column(Integer, default=30, comment="有效天数")
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    description = Column(Text)

    venue = relationship("Venue", backref="card_types")

    @property
    def display_name(self):
        """自动生成显示名称"""
        if self.name:
            return self.name
        cat_names = {'stored': '储值卡', 'month': '月卡', 'season': '季卡', 'year': '年卡', 'custom': '定制'}
        cat = cat_names.get(self.category, self.category)
        if self.category in ('stored', 'custom'):
            return f'{cat} ¥{int(self.total_times)}'
        return f'{cat} ¥{int(self.price)}'
