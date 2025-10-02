"""
租户数据模型
"""

from sqlalchemy import Column, String, Boolean, Integer, Text, DateTime
from sqlalchemy.orm import relationship

from .base import BaseModel, ConfigurableBaseModel, FileUploadMixin


class Tenant(ConfigurableBaseModel, FileUploadMixin):
    """租户模型"""
    
    __tablename__ = "tenants"
    
    # 基本信息
    code = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="租户编码"
    )
    
    domain = Column(
        String(255),
        nullable=True,
        comment="域名"
    )
    
    contact_person = Column(
        String(100),
        nullable=True,
        comment="联系人"
    )
    
    contact_phone = Column(
        String(20),
        nullable=True,
        comment="联系电话"
    )
    
    contact_email = Column(
        String(255),
        nullable=True,
        comment="联系邮箱"
    )
    
    # 业务信息
    industry = Column(
        String(100),
        nullable=True,
        comment="行业"
    )
    
    scale = Column(
        String(20),
        nullable=True,
        comment="规模"
    )
    
    # 配额限制
    max_users = Column(
        Integer,
        default=1000,
        nullable=False,
        comment="最大用户数"
    )
    
    max_devices = Column(
        Integer,
        default=500,
        nullable=False,
        comment="最大设备数"
    )
    
    max_concurrent_calls = Column(
        Integer,
        default=10,
        nullable=False,
        comment="最大并发通话数"
    )
    
    # 功能开关
    enable_user_management = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="启用用户管理"
    )
    
    enable_device_management = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="启用设备管理"
    )
    
    enable_intercom = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="启用对讲功能"
    )
    
    enable_alarm_system = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="启用报警系统"
    )
    
    enable_reports = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="启用报表功能"
    )
    
    # 服务信息
    service_start_date = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="服务开始日期"
    )
    
    service_end_date = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="服务结束日期"
    )
    
    subscription_type = Column(
        String(20),
        default="basic",
        nullable=False,
        comment="订阅类型"
    )
    
    def is_feature_enabled(self, feature: str) -> bool:
        """检查功能是否启用"""
        feature_map = {
            "user_management": self.enable_user_management,
            "device_management": self.enable_device_management,
            "intercom": self.enable_intercom,
            "alarm_system": self.enable_alarm_system,
            "reports": self.enable_reports,
        }
        return feature_map.get(feature, False)
    
    def get_quota_usage(self) -> dict:
        """获取配额使用情况"""
        # 这里可以通过关联查询获取实际使用情况
        return {
            "users": {
                "limit": self.max_users,
                "used": 0,  # 实际使用数量
                "available": self.max_users,
            },
            "devices": {
                "limit": self.max_devices,
                "used": 0,  # 实际使用数量
                "available": self.max_devices,
            },
            "concurrent_calls": {
                "limit": self.max_concurrent_calls,
                "used": 0,  # 实际使用数量
                "available": self.max_concurrent_calls,
            },
        }


class TenantTheme(BaseModel):
    """租户主题配置模型"""
    
    __tablename__ = "tenant_themes"
    
    # 主色调
    primary_color = Column(
        String(20),
        default="#1890ff",
        nullable=False,
        comment="主色调"
    )
    
    secondary_color = Column(
        String(20),
        default="#722ed1",
        nullable=False,
        comment="辅助色"
    )
    
    success_color = Column(
        String(20),
        default="#52c41a",
        nullable=False,
        comment="成功色"
    )
    
    warning_color = Column(
        String(20),
        default="#faad14",
        nullable=False,
        comment="警告色"
    )
    
    error_color = Column(
        String(20),
        default="#f5222d",
        nullable=False,
        comment="错误色"
    )
    
    # 背景和文字
    background_color = Column(
        String(20),
        default="#ffffff",
        nullable=False,
        comment="背景色"
    )
    
    text_color = Column(
        String(20),
        default="#000000",
        nullable=False,
        comment="文字色"
    )
    
    # 样式设置
    border_radius = Column(
        String(10),
        default="6px",
        nullable=False,
        comment="圆角大小"
    )
    
    font_family = Column(
        String(200),
        default="Arial, sans-serif",
        nullable=False,
        comment="字体"
    )
    
    # Logo和图标
    logo_url = Column(
        String(500),
        nullable=True,
        comment="Logo URL"
    )
    
    favicon_url = Column(
        String(500),
        nullable=True,
        comment="Favicon URL"
    )
    
    # 自定义CSS
    custom_css = Column(
        Text,
        nullable=True,
        comment="自定义CSS"
    )


class TenantSettings(BaseModel):
    """租户设置模型"""
    
    __tablename__ = "tenant_settings"
    
    # 设置分类
    category = Column(
        String(50),
        nullable=False,
        comment="设置分类"
    )
    
    # 设置键
    setting_key = Column(
        String(100),
        nullable=False,
        comment="设置键"
    )
    
    # 设置值
    setting_value = Column(
        Text,
        nullable=True,
        comment="设置值"
    )
    
    # 设置类型
    value_type = Column(
        String(20),
        default="string",
        nullable=False,
        comment="值类型"
    )
    
    # 设置描述
    description = Column(
        Text,
        nullable=True,
        comment="设置描述"
    )
    
    # 是否加密存储
    is_encrypted = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否加密存储"
    )
    
    def get_typed_value(self):
        """获取类型化的值"""
        if not self.setting_value:
            return None
        
        try:
            if self.value_type == "int":
                return int(self.setting_value)
            elif self.value_type == "float":
                return float(self.setting_value)
            elif self.value_type == "bool":
                return self.setting_value.lower() in ("true", "1", "yes", "on")
            elif self.value_type == "json":
                import json
                return json.loads(self.setting_value)
            else:
                return self.setting_value
        except (ValueError, TypeError):
            return self.setting_value
    
    def set_typed_value(self, value):
        """设置类型化的值"""
        if value is None:
            self.setting_value = None
            return
        
        if self.value_type == "json":
            import json
            self.setting_value = json.dumps(value, ensure_ascii=False)
        else:
            self.setting_value = str(value)


class TenantModule(BaseModel):
    """租户模块配置模型"""
    
    __tablename__ = "tenant_modules"
    
    # 模块代码
    module_code = Column(
        String(50),
        nullable=False,
        comment="模块代码"
    )
    
    # 模块名称
    module_name = Column(
        String(100),
        nullable=False,
        comment="模块名称"
    )
    
    # 是否启用
    is_enabled = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否启用"
    )
    
    # 配置信息
    configuration = Column(
        Text,
        nullable=True,
        comment="模块配置"
    )
    
    # 权限列表
    permissions = Column(
        Text,
        nullable=True,
        comment="模块权限列表"
    )
    
    # 排序
    sort_order = Column(
        Integer,
        default=0,
        nullable=False,
        comment="排序"
    )
    
    def get_configuration(self) -> dict:
        """获取模块配置"""
        if self.configuration:
            import json
            try:
                return json.loads(self.configuration)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    def get_permissions(self) -> list:
        """获取模块权限列表"""
        if self.permissions:
            import json
            try:
                return json.loads(self.permissions)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
