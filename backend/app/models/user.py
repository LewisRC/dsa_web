"""
用户数据模型
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import BaseModel, FileUploadMixin


class User(BaseModel, FileUploadMixin):
    """用户模型"""
    
    __tablename__ = "users"
    
    # 基本信息
    username = Column(
        String(50),
        nullable=False,
        comment="用户名"
    )
    
    email = Column(
        String(255),
        nullable=False,
        comment="邮箱"
    )
    
    phone = Column(
        String(20),
        nullable=True,
        comment="手机号"
    )
    
    # 认证信息
    password_hash = Column(
        String(255),
        nullable=False,
        comment="密码哈希"
    )
    
    salt = Column(
        String(50),
        nullable=True,
        comment="密码盐值"
    )
    
    # 个人信息
    real_name = Column(
        String(100),
        nullable=True,
        comment="真实姓名"
    )
    
    nickname = Column(
        String(100),
        nullable=True,
        comment="昵称"
    )
    
    gender = Column(
        String(10),
        nullable=True,
        comment="性别"
    )
    
    birthday = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="生日"
    )
    
    # 状态信息
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否激活"
    )
    
    is_superuser = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否超级用户"
    )
    
    is_staff = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否员工"
    )
    
    # 登录信息
    last_login = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="最后登录时间"
    )
    
    login_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="登录次数"
    )
    
    failed_login_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="失败登录次数"
    )
    
    locked_until = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="锁定到期时间"
    )
    
    # 密码相关
    password_changed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="密码修改时间"
    )
    
    password_reset_token = Column(
        String(255),
        nullable=True,
        comment="密码重置令牌"
    )
    
    password_reset_expires = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="密码重置过期时间"
    )
    
    # 两步验证
    two_factor_enabled = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否启用两步验证"
    )
    
    two_factor_secret = Column(
        String(100),
        nullable=True,
        comment="两步验证密钥"
    )
    
    # 偏好设置
    language = Column(
        String(10),
        default="zh-CN",
        nullable=False,
        comment="语言"
    )
    
    timezone = Column(
        String(50),
        default="Asia/Shanghai",
        nullable=False,
        comment="时区"
    )
    
    theme = Column(
        String(20),
        default="light",
        nullable=False,
        comment="主题"
    )
    
    # 工作信息
    department = Column(
        String(100),
        nullable=True,
        comment="部门"
    )
    
    position = Column(
        String(100),
        nullable=True,
        comment="职位"
    )
    
    employee_id = Column(
        String(50),
        nullable=True,
        comment="工号"
    )
    
    # 联系信息
    office_phone = Column(
        String(20),
        nullable=True,
        comment="办公电话"
    )
    
    extension = Column(
        String(10),
        nullable=True,
        comment="分机号"
    )
    
    # 备注
    notes = Column(
        Text,
        nullable=True,
        comment="备注"
    )
    
    def is_account_locked(self) -> bool:
        """检查账户是否被锁定"""
        if self.locked_until:
            return func.now() < self.locked_until
        return False
    
    def can_login(self) -> bool:
        """检查是否可以登录"""
        return self.is_active and not self.is_deleted and not self.is_account_locked()
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        return self.real_name or self.nickname or self.username
    
    def has_permission(self, permission: str) -> bool:
        """检查是否有权限（通过角色）"""
        if self.is_superuser:
            return True
        
        # 通过用户角色检查权限
        for user_role in self.roles:
            if user_role.role.has_permission(permission):
                return True
        
        return False
    
    def get_permissions(self) -> set:
        """获取所有权限"""
        if self.is_superuser:
            # 超级用户拥有所有权限
            return set()  # 这里可以返回所有权限的集合
        
        permissions = set()
        for user_role in self.roles:
            permissions.update(user_role.role.get_permissions())
        
        return permissions


class Role(BaseModel):
    """角色模型"""
    
    __tablename__ = "roles"
    
    # 角色信息
    name = Column(
        String(50),
        nullable=False,
        comment="角色名称"
    )
    
    code = Column(
        String(50),
        nullable=False,
        comment="角色代码"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="角色描述"
    )
    
    # 状态
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否激活"
    )
    
    is_system = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否系统角色"
    )
    
    # 排序
    sort_order = Column(
        Integer,
        default=0,
        nullable=False,
        comment="排序"
    )
    
    def has_permission(self, permission: str) -> bool:
        """检查角色是否有权限"""
        for role_permission in self.permissions:
            if role_permission.permission.code == permission:
                return True
        return False
    
    def get_permissions(self) -> set:
        """获取角色的所有权限"""
        return {rp.permission.code for rp in self.permissions}


class Permission(BaseModel):
    """权限模型"""
    
    __tablename__ = "permissions"
    
    # 权限信息
    name = Column(
        String(100),
        nullable=False,
        comment="权限名称"
    )
    
    code = Column(
        String(100),
        nullable=False,
        comment="权限代码"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="权限描述"
    )
    
    # 权限分组
    module = Column(
        String(50),
        nullable=False,
        comment="权限模块"
    )
    
    category = Column(
        String(50),
        nullable=True,
        comment="权限分类"
    )
    
    # 状态
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否激活"
    )
    
    # 排序
    sort_order = Column(
        Integer,
        default=0,
        nullable=False,
        comment="排序"
    )


class UserRole(BaseModel):
    """用户角色关联模型"""
    
    __tablename__ = "user_roles"
    
    # 关联字段
    user_id = Column(
        String(50),
        ForeignKey("users.id"),
        nullable=False,
        comment="用户ID"
    )
    
    role_id = Column(
        String(50),
        ForeignKey("roles.id"),
        nullable=False,
        comment="角色ID"
    )
    
    # 有效期
    start_date = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="生效时间"
    )
    
    end_date = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="失效时间"
    )
    
    # 关联关系
    user = relationship("User", backref="roles")
    role = relationship("Role", backref="users")
    
    def is_valid(self) -> bool:
        """检查角色分配是否有效"""
        now = func.now()
        if self.end_date:
            return self.start_date <= now <= self.end_date
        return self.start_date <= now


class RolePermission(BaseModel):
    """角色权限关联模型"""
    
    __tablename__ = "role_permissions"
    
    # 关联字段
    role_id = Column(
        String(50),
        ForeignKey("roles.id"),
        nullable=False,
        comment="角色ID"
    )
    
    permission_id = Column(
        String(50),
        ForeignKey("permissions.id"),
        nullable=False,
        comment="权限ID"
    )
    
    # 关联关系
    role = relationship("Role", backref="permissions")
    permission = relationship("Permission", backref="roles")


class UserSession(BaseModel):
    """用户会话模型"""
    
    __tablename__ = "user_sessions"
    
    # 会话信息
    user_id = Column(
        String(50),
        ForeignKey("users.id"),
        nullable=False,
        comment="用户ID"
    )
    
    session_token = Column(
        String(255),
        nullable=False,
        comment="会话令牌"
    )
    
    refresh_token = Column(
        String(255),
        nullable=True,
        comment="刷新令牌"
    )
    
    # 设备信息
    device_id = Column(
        String(255),
        nullable=True,
        comment="设备ID"
    )
    
    device_type = Column(
        String(50),
        nullable=True,
        comment="设备类型"
    )
    
    user_agent = Column(
        Text,
        nullable=True,
        comment="用户代理"
    )
    
    # 网络信息
    ip_address = Column(
        String(50),
        nullable=True,
        comment="IP地址"
    )
    
    location = Column(
        String(200),
        nullable=True,
        comment="地理位置"
    )
    
    # 状态信息
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否活跃"
    )
    
    last_activity = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="最后活动时间"
    )
    
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="过期时间"
    )
    
    # 关联关系
    user = relationship("User", backref="sessions")
    
    def is_expired(self) -> bool:
        """检查会话是否过期"""
        return func.now() > self.expires_at
    
    def is_valid(self) -> bool:
        """检查会话是否有效"""
        return self.is_active and not self.is_expired()
