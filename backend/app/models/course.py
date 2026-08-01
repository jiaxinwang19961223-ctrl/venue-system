"""课程模型 — 参考球之道教务体系"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class CoursePackage(Base):
    """课程套餐（参考球之道套餐管理: 次卡/月卡/季卡/年卡）"""
    __tablename__ = "course_packages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="套餐名称")
    total_sessions = Column(Integer, nullable=False, comment="总课时")
    price = Column(Float, nullable=False, comment="价格")
    valid_days = Column(Integer, default=365, comment="有效天数")
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)


class Course(Base):
    """课程"""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)
    name = Column(String(100), nullable=False, comment="课程名称")
    coach_id = Column(Integer, ForeignKey("users.id"), comment="教练")
    package_id = Column(Integer, ForeignKey("course_packages.id"), comment="关联套餐")

    max_students = Column(Integer, default=10, comment="最大学员数")
    description = Column(Text)
    cover_image = Column(String(500))

    # 时间安排
    schedule_desc = Column(String(200), comment="上课时间描述（如：每周六 14:00-16:00）")

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    venue = relationship("Venue", back_populates="courses")
    coach = relationship("User", foreign_keys=[coach_id])
    package = relationship("CoursePackage")
    bookings = relationship("CourseBooking", back_populates="course", cascade="all, delete-orphan")


class CourseBooking(Base):
    """课程报名/消课记录（参考球之道销课系统）"""
    __tablename__ = "course_bookings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    package_id = Column(Integer, ForeignKey("course_packages.id"))

    total_sessions = Column(Integer, default=0, comment="购买课时数")
    used_sessions = Column(Integer, default=0, comment="已消课时")
    remaining_sessions = Column(Integer, default=0, comment="剩余课时")

    status = Column(String(20), default="active", comment="active/finished/refunded")
    start_date = Column(DateTime, comment="开始日期")
    end_date = Column(DateTime, comment="到期日期")
    created_at = Column(DateTime, default=datetime.now)

    course = relationship("Course", back_populates="bookings")
    member = relationship("Member")

    # 消课记录
    checkins = relationship("CourseCheckin", back_populates="booking", cascade="all, delete-orphan")


class CourseCheckin(Base):
    """消课签到记录（参考球之道销课明细）"""
    __tablename__ = "course_checkins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey("course_bookings.id"), nullable=False)
    checkin_time = Column(DateTime, default=datetime.now, comment="签到时间")
    remark = Column(String(200))

    booking = relationship("CourseBooking", back_populates="checkins")
