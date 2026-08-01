"""用户 & 角色模型 — 四角色权限体系"""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserRole(str, enum.Enum):
    """四角色 — 参考角色权限矩阵"""
    CORE_MANAGEMENT = "core_management"  # 核心管理层 — 全部门店
    MANAGER = "manager"                  # 馆长/店长 — 本馆全部
    RECEPTION = "reception"              # 前台 — 开单/查询
    COACH = "coach"                      # 教练 — 自己课程/学员
    CUSTOMER = "customer"                # 顾客 — 预约/查看


# 角色权限配置（API层根据此配置过滤数据）
ROLE_PERMISSIONS = {
    UserRole.CORE_MANAGEMENT: {
        "all_venues": True,        # 看全部门店
        "view_revenue": True,      # 看营收
        "manage_staff": True,      # 管理员工
        "manage_fields": True,     # 管理场地
        "manage_prices": True,     # 设置价格
        "quick_order": True,       # 快速开单
        "check_in": True,          # 签到消课
        "member_query": True,      # 会员查询
        "member_edit": True,       # 会员编辑
        "refund": True,            # 退款
    },
    UserRole.MANAGER: {
        "all_venues": False,
        "view_revenue": True,
        "manage_staff": False,
        "manage_fields": True,
        "manage_prices": True,
        "quick_order": True,
        "check_in": True,
        "member_query": True,
        "member_edit": True,
        "refund": True,
    },
    UserRole.RECEPTION: {
        "all_venues": False,
        "view_revenue": False,
        "manage_staff": False,
        "manage_fields": False,
        "manage_prices": False,
        "quick_order": True,
        "check_in": False,
        "member_query": True,
        "member_edit": False,
        "refund": False,
    },
    UserRole.COACH: {
        "all_venues": False,
        "view_revenue": False,
        "manage_staff": False,
        "manage_fields": False,
        "manage_prices": False,
        "quick_order": False,
        "check_in": True,          # 消课
        "member_query": False,
        "member_edit": False,
        "refund": False,
    },
    UserRole.CUSTOMER: {
        "all_venues": False,
        "view_revenue": False,
        "manage_staff": False,
        "manage_fields": False,
        "manage_prices": False,
        "quick_order": False,
        "check_in": False,
        "member_query": False,
        "member_edit": False,
        "refund": False,
    },
}


class User(Base):
    """用户（员工 + 顾客）"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    venue_id = Column(Integer, ForeignKey("venues.id"), comment="所属球馆（核心管理层为空）")
    username = Column(String(50), unique=True, nullable=False)
    phone = Column(String(20), unique=True, comment="手机号")
    hashed_password = Column(String(200), nullable=False)
    name = Column(String(50), comment="真实姓名")
    role = Column(SAEnum(UserRole), default=UserRole.CUSTOMER)
    avatar = Column(String(500))

    # WeChat
    openid = Column(String(100), unique=True, comment="微信OpenID")
    unionid = Column(String(100), comment="微信UnionID")

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime)

    venue = relationship("Venue", back_populates="users")

    @property
    def permissions(self) -> dict:
        return ROLE_PERMISSIONS.get(self.role, {})
