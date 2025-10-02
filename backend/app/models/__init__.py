"""
数据模型模块
统一导入所有数据模型
"""

# 基础模型
from .base import (
    BaseModel,
    NamedBaseModel,
    ConfigurableBaseModel,
    TimestampMixin,
    TenantMixin,
    SoftDeleteMixin,
    AuditMixin,
    VersionMixin,
    StatusMixin,
    TreeMixin,
    FileUploadMixin,
    LocationMixin,
)

# 租户模型
from .tenant import (
    Tenant,
    TenantTheme,
    TenantSettings,
    TenantModule,
)

# 用户模型
from .user import (
    User,
    Role,
    Permission,
    UserRole,
    RolePermission,
    UserSession,
)

# 设备模型
from .device import (
    DeviceType,
    Device,
    DeviceGroup,
    DeviceGroupMember,
    DeviceLog,
    DeviceCommand,
    DeviceAlert,
)

# 对讲模型
from .intercom import (
    IntercomSession,
    IntercomParticipant,
    IntercomGroup,
    IntercomGroupMember,
    IntercomContact,
    IntercomSettings,
    IntercomRecord,
)

# 报警模型
from .alarm import (
    AlarmType,
    Alarm,
    AlarmRule,
    AlarmNotificationRule,
    AlarmNotification,
    AlarmEscalation,
    AlarmStatistics,
)

# 日志模型
from .log import (
    SystemLog,
    OperationLog,
    AccessLog,
    DeviceOperationLog,
    LoginLog,
    AuditTrail,
)

# 所有模型列表
__all__ = [
    # 基础模型
    "BaseModel",
    "NamedBaseModel",
    "ConfigurableBaseModel",
    "TimestampMixin",
    "TenantMixin",
    "SoftDeleteMixin",
    "AuditMixin",
    "VersionMixin",
    "StatusMixin",
    "TreeMixin",
    "FileUploadMixin",
    "LocationMixin",
    
    # 租户模型
    "Tenant",
    "TenantTheme",
    "TenantSettings",
    "TenantModule",
    
    # 用户模型
    "User",
    "Role",
    "Permission",
    "UserRole",
    "RolePermission",
    "UserSession",
    
    # 设备模型
    "DeviceType",
    "Device",
    "DeviceGroup",
    "DeviceGroupMember",
    "DeviceLog",
    "DeviceCommand",
    "DeviceAlert",
    
    # 对讲模型
    "IntercomSession",
    "IntercomParticipant",
    "IntercomGroup",
    "IntercomGroupMember",
    "IntercomContact",
    "IntercomSettings",
    "IntercomRecord",
    
    # 报警模型
    "AlarmType",
    "Alarm",
    "AlarmRule",
    "AlarmNotificationRule",
    "AlarmNotification",
    "AlarmEscalation",
    "AlarmStatistics",
    
    # 日志模型
    "SystemLog",
    "OperationLog",
    "AccessLog",
    "DeviceOperationLog",
    "LoginLog",
    "AuditTrail",
]
