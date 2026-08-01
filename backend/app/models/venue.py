"""场馆 & 场地模型"""
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class VenueStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    MAINTENANCE = "maintenance"


class Venue(Base):
    """球馆"""
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="球馆名称")
    address = Column(String(500), comment="地址")
    phone = Column(String(20), comment="联系电话")
    description = Column(Text, comment="简介")
    cover_image = Column(String(500), comment="封面图")
    business_hours = Column(String(100), default="09:00-22:00", comment="营业时间")
    status = Column(SAEnum(VenueStatus), default=VenueStatus.OPEN)
    district = Column(String(50), comment="所在区/县（一照多址合规）")
    is_active = Column(Boolean, default=True)

    # 关联
    fields = relationship("Field", back_populates="venue", cascade="all, delete-orphan")
    users = relationship("User", back_populates="venue")
    members = relationship("Member", back_populates="venue")
    orders = relationship("Order", back_populates="venue")
    courses = relationship("Course", back_populates="venue")


class FieldType(str, enum.Enum):
    BADMINTON = "badminton"     # 羽毛球
    BASKETBALL = "basketball"   # 篮球
    TABLE_TENNIS = "pingpong"   # 乒乓球
    TENNIS = "tennis"           # 网球
    FOOTBALL = "football"       # 足球
    SWIMMING = "swimming"       # 游泳
    FITNESS = "fitness"         # 健身
    OTHER = "other"             # 其他


class Field(Base):
    """场地（每个球馆下的具体场地）"""
    __tablename__ = "fields"

    id = Column(Integer, primary_key=True, autoincrement=True)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)
    name = Column(String(100), nullable=False, comment="场地名称（如：A1场、VIP包场）")
    field_type = Column(SAEnum(FieldType), default=FieldType.OTHER, comment="场地类型")
    price_per_hour = Column(Float, default=0, comment="每小时价格")
    peak_price_per_hour = Column(Float, default=0, comment="高峰时段价格")
    capacity = Column(Integer, default=0, comment="容纳人数")
    description = Column(Text, comment="场地描述")
    cover_image = Column(String(500))
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0, comment="排序")

    venue = relationship("Venue", back_populates="fields")
    time_templates = relationship("FieldTimeTemplate", back_populates="field", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="field")


class FieldTimeTemplate(Base):
    """场地时段模板（用于快速设置可预约时段）"""
    __tablename__ = "field_time_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False)
    start_time = Column(String(10), nullable=False, comment="开始时间 HH:MM")
    end_time = Column(String(10), nullable=False, comment="结束时间 HH:MM")
    is_peak = Column(Boolean, default=False, comment="是否高峰时段")
    weekday = Column(Integer, default=0, comment="0=每天,1-7=周一到周日")

    field = relationship("Field", back_populates="time_templates")
