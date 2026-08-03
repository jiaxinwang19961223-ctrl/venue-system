"""训练营 API — 课程/分班/消课/考勤"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.core.database import get_db
from app.models.course import Course, CourseEnrollment, CourseSession, SessionAttendance, CourseStatus, AttendanceStatus
from app.models.member import Member
from app.models.user import User, UserRole
from app.api.auth import get_current_user

router = APIRouter(prefix="/courses", tags=["训练营"])

# ═══════ Schemas ═══════
class CourseCreate(BaseModel):
    venue_id: int
    name: str
    coach: str = ""
    coach_face: Optional[str] = None
    max_students: int = 20
    price_per_session: float = 0
    total_sessions: int = 10
    description: str = ""

class CourseUpdate(BaseModel):
    name: Optional[str] = None
    coach: Optional[str] = None
    coach_face: Optional[str] = None
    max_students: Optional[int] = None
    price_per_session: Optional[float] = None
    total_sessions: Optional[int] = None
    description: Optional[str] = None
    status: Optional[CourseStatus] = None

class EnrollStudent(BaseModel):
    course_id: int = 0
    member_id: int = 0
    total_sessions: int = 10

class SessionCreate(BaseModel):
    course_id: int
    session_date: str
    start_time: str = "09:00"
    end_time: str = "10:00"
    coach: str = ""
    notes: str = ""

class AttendanceUpdate(BaseModel):
    session_id: int
    attendances: List[dict] = []  # [{enrollment_id, status}]

# ═══════ 课程 CRUD ═══════
@router.get("")
def list_courses(
    venue_id: Optional[int] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Course).filter(Course.is_active == True)
    if venue_id:
        query = query.filter(Course.venue_id == venue_id)
    elif user.role not in [UserRole.CORE_MANAGEMENT] and user.venue_id:
        query = query.filter(Course.venue_id == user.venue_id)
    courses = query.order_by(Course.id.desc()).all()
    return {"courses": [
        {"id": c.id, "venue_id": c.venue_id, "name": c.name, "coach": c.coach,
         "coach_face": c.coach_face,
         "max_students": c.max_students, "price_per_session": c.price_per_session,
         "total_sessions": c.total_sessions, "description": c.description,
         "status": c.status.value if c.status else "active",
         "student_count": len([e for e in c.enrollments if e.is_active])}
        for c in courses
    ]}

@router.post("")
def create_course(data: CourseCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    course = Course(**data.model_dump(), created_at=datetime.now().strftime("%Y-%m-%d %H:%M"))
    db.add(course); db.commit(); db.refresh(course)
    return {"id": course.id, "name": course.name}

@router.put("/{course_id}")
def update_course(course_id: int, data: CourseUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    course = db.query(Course).get(course_id)
    if not course: raise HTTPException(404)
    for k, v in data.model_dump(exclude_none=True).items(): setattr(course, k, v)
    db.commit()
    return {"message": "更新成功"}

@router.delete("/{course_id}")
def delete_course(course_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    course = db.query(Course).get(course_id)
    if not course: raise HTTPException(404)
    course.is_active = False; db.commit()
    return {"message": "已停用"}

# ═══════ 学员报名 ═══════
@router.get("/{course_id}/students")
def list_students(course_id: int, db: Session = Depends(get_db)):
    enrollments = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course_id, CourseEnrollment.is_active == True
    ).all()
    return {"students": [
        {"id": e.id, "member_id": e.member_id, "member_name": e.member.name,
         "member_phone": e.member.phone, "member_birthday": e.member.birthday,
         "member_gender": e.member.gender, "member_face": e.member.face_image,
         "enrolled_age": e.enrolled_age or 0,
         "total_sessions": e.total_sessions,
         "used_sessions": e.used_sessions, "enrolled_date": e.enrolled_date}
        for e in enrollments
    ]}

@router.post("/enroll")
def enroll_student(data: EnrollStudent, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 检查是否已报名
    existing = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == data.course_id,
        CourseEnrollment.member_id == data.member_id,
        CourseEnrollment.is_active == True,
    ).first()
    if existing: raise HTTPException(status_code=400, detail="该学员已报名此课程")
    # 计算入营年龄
    member = db.query(Member).get(data.member_id)
    enrolled_age = 0
    if member and member.birthday:
        try:
            bd = datetime.strptime(member.birthday, "%Y-%m-%d")
            today = datetime.now()
            enrolled_age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
        except: pass

    enroll = CourseEnrollment(
        course_id=data.course_id, member_id=data.member_id,
        total_sessions=data.total_sessions,
        enrolled_age=enrolled_age,
        enrolled_date=datetime.now().strftime("%Y-%m-%d"),
    )
    db.add(enroll); db.commit(); db.refresh(enroll)
    return {"id": enroll.id, "member_name": enroll.member.name}

@router.put("/enroll/{enrollment_id}")
def update_enrollment(enrollment_id: int, data: EnrollStudent, db: Session = Depends(get_db)):
    enroll = db.query(CourseEnrollment).get(enrollment_id)
    if not enroll: raise HTTPException(404)
    if data.total_sessions: enroll.total_sessions = data.total_sessions
    db.commit()
    return {"message": "已更新"}

@router.delete("/enroll/{enrollment_id}")
def unenroll(enrollment_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    enroll = db.query(CourseEnrollment).get(enrollment_id)
    if not enroll: raise HTTPException(404)
    enroll.is_active = False; db.commit()
    return {"message": "已移出"}

# ═══════ 上课记录 ═══════
@router.get("/{course_id}/sessions")
def list_sessions(course_id: int, db: Session = Depends(get_db)):
    sessions = db.query(CourseSession).filter(
        CourseSession.course_id == course_id
    ).order_by(CourseSession.session_date.desc()).all()
    return {"sessions": [
        {"id": s.id, "session_date": s.session_date, "start_time": s.start_time,
         "end_time": s.end_time, "coach": s.coach, "notes": s.notes,
         "attendance_count": len(s.attendances),
         "attendance_rate": f"{len([a for a in s.attendances if a.status == AttendanceStatus.PRESENT])}/{len(s.attendances)}" if s.attendances else "0/0"}
        for s in sessions
    ]}

@router.post("/sessions")
def create_session(data: SessionCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = CourseSession(**data.model_dump(), created_at=datetime.now().strftime("%Y-%m-%d %H:%M"))
    db.add(session); db.commit(); db.refresh(session)
    # 自动为所有报名学员生成签到记录
    enrollments = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == data.course_id, CourseEnrollment.is_active == True
    ).all()
    for e in enrollments:
        att = SessionAttendance(session_id=session.id, enrollment_id=e.id, status=AttendanceStatus.ABSENT)
        db.add(att)
    db.commit()
    return {"id": session.id, "attendance_count": len(enrollments)}

@router.get("/sessions/{session_id}/attendance")
def get_attendance(session_id: int, db: Session = Depends(get_db)):
    records = db.query(SessionAttendance).filter(SessionAttendance.session_id == session_id).all()
    return {"attendances": [
        {"id": a.id, "enrollment_id": a.enrollment_id,
         "member_name": a.enrollment.member.name if a.enrollment else "",
         "member_birthday": a.enrollment.member.birthday if a.enrollment and a.enrollment.member else None,
         "member_face": a.enrollment.member.face_image if a.enrollment and a.enrollment.member else None,
         "status": a.status.value, "notes": a.notes or ""}
        for a in records
    ]}

@router.put("/sessions/{session_id}/attendance")
def update_attendance(session_id: int, data: AttendanceUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    for item in data.attendances:
        att = db.query(SessionAttendance).filter(
            SessionAttendance.session_id == session_id,
            SessionAttendance.enrollment_id == item.get("enrollment_id"),
        ).first()
        if att:
            att.status = item.get("status", AttendanceStatus.PRESENT)
            att.notes = item.get("notes", "")
    db.commit()
    # 消课：为到场学员扣课时
    present_records = db.query(SessionAttendance).filter(
        SessionAttendance.session_id == session_id,
        SessionAttendance.status == AttendanceStatus.PRESENT,
    ).all()
    for a in present_records:
        enroll = db.query(CourseEnrollment).get(a.enrollment_id)
        if enroll and enroll.used_sessions < enroll.total_sessions:
            enroll.used_sessions += 1
    db.commit()
    return {"message": "签到已更新，已自动消课"}

@router.delete("/sessions/{session_id}")
def delete_session(session_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(CourseSession).get(session_id)
    if not session: raise HTTPException(404)
    db.delete(session); db.commit()
    return {"message": "已删除"}

# ═══════ 学员管理（独立数据）═══════
class StudentCreate(BaseModel):
    venue_id: int
    name: str
    phone: str = ""
    gender: str = "男"
    birthday: Optional[str] = None
    face_image: Optional[str] = None
    face_descriptor: Optional[str] = None

@router.get("/students/list")
def list_students_all(venue_id: Optional[int] = None, db: Session = Depends(get_db)):
    from app.models.student import Student
    from datetime import datetime
    query = db.query(Student).filter(Student.is_active == True)
    if venue_id: query = query.filter(Student.venue_id == venue_id)
    students = query.order_by(Student.id.desc()).limit(200).all()
    return {"students": [
        {"id": s.id, "name": s.name, "phone": s.phone, "gender": s.gender,
         "birthday": str(s.birthday.date()) if s.birthday else None,
         "face_image": s.face_image, "created_at": str(s.created_at)}
        for s in students
    ]}

@router.post("/students")
def create_student(data: StudentCreate, db: Session = Depends(get_db)):
    from app.models.student import Student
    from datetime import datetime
    s = Student(**data.model_dump(exclude={'birthday'}))
    if data.birthday:
        try: s.birthday = datetime.strptime(data.birthday, "%Y-%m-%d")
        except: pass
    db.add(s); db.commit(); db.refresh(s)
    return {"id": s.id, "name": s.name}

@router.put("/students/{student_id}")
def update_student(student_id: int, data: StudentCreate, db: Session = Depends(get_db)):
    from app.models.student import Student
    from datetime import datetime
    s = db.query(Student).get(student_id)
    if not s: raise HTTPException(status_code=404)
    for k, v in data.model_dump(exclude_none=True).items():
        if k == 'birthday' and v:
            try: v = datetime.strptime(v, "%Y-%m-%d")
            except: continue
        if k != 'venue_id': setattr(s, k, v)
    db.commit()
    return {"message": "更新成功"}

@router.get("/students/{student_id}")
def get_student(student_id: int, db: Session = Depends(get_db)):
    from app.models.student import Student
    s = db.query(Student).get(student_id)
    if not s: raise HTTPException(status_code=404)
    return {"id": s.id, "name": s.name, "phone": s.phone, "gender": s.gender,
            "birthday": str(s.birthday.date()) if s.birthday else None,
            "face_image": s.face_image, "face_descriptor": s.face_descriptor}
