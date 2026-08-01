"""初始化数据库 — 创建默认球馆和管理员"""
from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.venue import Venue, Field, FieldType
from app.models.member import MemberLevel

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 检查是否已初始化
    if db.query(User).first():
        print("数据库已初始化，跳过")
        db.close()
        return

    # 创建默认球馆
    venue = Venue(
        name="默认球馆",
        address="",
        phone="",
        business_hours="09:00-22:00",
        district="",
    )
    db.add(venue)
    db.flush()

    # 创建默认场地
    fields = [
        Field(venue_id=venue.id, name="A1场", field_type=FieldType.BADMINTON, price_per_hour=80, capacity=4, sort_order=1),
        Field(venue_id=venue.id, name="A2场", field_type=FieldType.BADMINTON, price_per_hour=80, capacity=4, sort_order=2),
        Field(venue_id=venue.id, name="B1场", field_type=FieldType.BASKETBALL, price_per_hour=200, capacity=20, sort_order=3),
    ]
    db.add_all(fields)

    # 创建默认管理员
    admin = User(
        username="admin",
        phone="13800000000",
        name="系统管理员",
        hashed_password=hash_password("admin123"),
        role=UserRole.CORE_MANAGEMENT,
    )
    db.add(admin)

    # 创建店员账号
    staff = User(
        venue_id=venue.id,
        username="staff",
        phone="13800000001",
        name="前台小王",
        hashed_password=hash_password("staff123"),
        role=UserRole.RECEPTION,
    )
    db.add(staff)

    # 创建默认会员等级
    levels = [
        MemberLevel(name="普通会员", discount=1.0, min_recharge=0, valid_months=12, sort_order=1),
        MemberLevel(name="银卡会员", discount=0.9, min_recharge=1000, valid_months=12, sort_order=2),
        MemberLevel(name="金卡会员", discount=0.8, min_recharge=5000, valid_months=12, sort_order=3),
    ]
    db.add_all(levels)

    venue_name = venue.name
    fields_count = len(fields)
    levels_count = len(levels)
    db.commit()
    db.close()
    print("数据库初始化完成！")
    print("  管理员: admin / admin123 (核心管理层)")
    print("  店员:   staff / staff123 (前台)")
    print(f"  默认球馆: {venue_name}")
    print(f"  场地: {fields_count} 个")
    print(f"  会员等级: {levels_count} 个")


if __name__ == "__main__":
    init_db()
