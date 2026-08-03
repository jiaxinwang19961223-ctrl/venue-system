"""训练营模型 — 课程/分班/消课/考勤"""
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, Time, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

class CourseStatus(str, enum.Enum):
    ACTIVE = "active"
    CLOSED = "closed"

class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    LEAVE = "leave"

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)
    name = Column(String(100), nullable=False, comment="课程名称")
    coach = Column(String(50), comment="教练")
    coach_face = Column(Text, comment="教练人脸照片(base64)")
    max_students = Column(Integer, default=20)
    price_per_session = Column(Float, default=0)
    total_sessions = Column(Integer, default=10)
    description = Column(Text)
    status = Column(SAEnum(CourseStatus), default=CourseStatus.ACTIVE)
    is_active = Column(Boolean, default=True)
    created_at = Column(String(30))
    venue = relationship("Venue", back_populates="courses")
    enrollments = relationship("CourseEnrollment", back_populates="course", cascade="all, delete-orphan")
    sessions = relationship("CourseSession", back_populates="course", cascade="all, delete-orphan")

class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    enrolled_date = Column(String(30))
    total_sessions = Column(Integer, default=0)
    used_sessions = Column(Integer, default=0)
    enrolled_age = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    course = relationship("Course", back_populates="enrollments")
    member = relationship("Member", backref="enrollments")

class CourseSession(Base):
    __tablename__ = "course_sessions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    session_date = Column(String(30))
    start_time = Column(String(10))
    end_time = Column(String(10))
    coach = Column(String(50))
    notes = Column(Text)
    created_at = Column(String(30))
    course = relationship("Course", back_populates="sessions")
    attendances = relationship("SessionAttendance", back_populates="session", cascade="all, delete-orphan")

class SessionAttendance(Base):
    __tablename__ = "session_attendances"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("course_sessions.id"), nullable=False)
    enrollment_id = Column(Integer, ForeignKey("course_enrollments.id"), nullable=False)
    status = Column(SAEnum(AttendanceStatus), default=AttendanceStatus.PRESENT)
    notes = Column(String(200))
    session = relationship("CourseSession", back_populates="attendances")
    enrollment = relationship("CourseEnrollment", backref="attendances")
