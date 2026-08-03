"""训练营学员模型 — 与会员数据分离"""
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, autoincrement=True)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)
    name = Column(String(50), nullable=False)
    phone = Column(String(20))
    gender = Column(String(10))
    birthday = Column(DateTime)
    face_image = Column(Text)
    face_descriptor = Column(Text)
    remark = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    venue = relationship("Venue", backref="stu_list")
