"""
应用配置设置
支持多环境配置和租户配置
"""

import os
from typing import Optional, List, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    app_name: str = Field(default="Universal Security Intercom System", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")
    environment: str = Field(default="production", description="环境类型")
    
    # 服务器配置
    host: str = Field(default="0.0.0.0", description="服务器地址")
    port: int = Field(default=8000, description="服务器端口")
    reload: bool = Field(default=False, description="自动重载")
    
    # 数据库配置
    database_url: str = Field(default="sqlite:///./security_intercom.db", description="数据库URL")
    database_echo: bool = Field(default=False, description="数据库SQL日志")
    
    # 安全配置
    secret_key: str = Field(..., description="JWT密钥")
    algorithm: str = Field(default="HS256", description="JWT算法")
    access_token_expire_minutes: int = Field(default=30, description="访问令牌过期时间（分钟）")
    refresh_token_expire_days: int = Field(default=7, description="刷新令牌过期时间（天）")
    
    # CORS配置
    cors_origins: List[str] = Field(default=["http://localhost:3000"], description="CORS允许的源")
    cors_credentials: bool = Field(default=True, description="CORS允许凭据")
    cors_methods: List[str] = Field(default=["*"], description="CORS允许的方法")
    cors_headers: List[str] = Field(default=["*"], description="CORS允许的头部")
    
    # Redis配置（可选）
    redis_url: Optional[str] = Field(default=None, description="Redis连接URL")
    redis_password: Optional[str] = Field(default=None, description="Redis密码")
    
    # 文件上传配置
    max_file_size: int = Field(default=10 * 1024 * 1024, description="最大文件大小（字节）")  # 10MB
    upload_path: str = Field(default="./uploads", description="文件上传路径")
    allowed_extensions: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx"],
        description="允许的文件扩展名"
    )
    
    # WebSocket配置
    websocket_heartbeat_interval: int = Field(default=30, description="WebSocket心跳间隔（秒）")
    websocket_timeout: int = Field(default=60, description="WebSocket超时时间（秒）")
    
    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_file: Optional[str] = Field(default=None, description="日志文件路径")
    log_rotation: str = Field(default="1 day", description="日志轮转配置")
    log_retention: str = Field(default="30 days", description="日志保留时间")
    
    # 邮件配置（用于通知）
    smtp_server: Optional[str] = Field(default=None, description="SMTP服务器")
    smtp_port: int = Field(default=587, description="SMTP端口")
    smtp_username: Optional[str] = Field(default=None, description="SMTP用户名")
    smtp_password: Optional[str] = Field(default=None, description="SMTP密码")
    smtp_use_tls: bool = Field(default=True, description="SMTP使用TLS")
    
    # 多租户配置
    default_tenant_id: str = Field(default="default", description="默认租户ID")
    tenant_isolation: bool = Field(default=True, description="租户数据隔离")
    max_tenants: int = Field(default=100, description="最大租户数量")
    
    # 功能模块配置
    enable_user_registration: bool = Field(default=True, description="启用用户注册")
    enable_device_auto_discovery: bool = Field(default=False, description="启用设备自动发现")
    enable_real_time_monitoring: bool = Field(default=True, description="启用实时监控")
    enable_alarm_notifications: bool = Field(default=True, description="启用报警通知")
    enable_audit_logging: bool = Field(default=True, description="启用审计日志")
    
    # API配置
    api_v1_prefix: str = Field(default="/api/v1", description="API v1前缀")
    docs_url: str = Field(default="/docs", description="文档URL")
    redoc_url: str = Field(default="/redoc", description="ReDoc URL")
    openapi_url: str = Field(default="/openapi.json", description="OpenAPI URL")
    
    @validator('cors_origins', pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """处理CORS源配置"""
        if isinstance(v, str) and not v.startswith('['):
            return [i.strip() for i in v.split(',')]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @validator('secret_key', pre=True)
    def validate_secret_key(cls, v: str) -> str:
        """验证密钥"""
        if not v or len(v) < 32:
            raise ValueError('密钥长度不能少于32个字符')
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class DevelopmentSettings(Settings):
    """开发环境配置"""
    debug: bool = True
    reload: bool = True
    database_echo: bool = True
    log_level: str = "DEBUG"
    environment: str = "development"


class TestSettings(Settings):
    """测试环境配置"""
    debug: bool = True
    database_url: str = "sqlite:///./test_security_intercom.db"
    environment: str = "test"
    access_token_expire_minutes: int = 5  # 测试环境较短过期时间


class ProductionSettings(Settings):
    """生产环境配置"""
    debug: bool = False
    reload: bool = False
    database_echo: bool = False
    log_level: str = "WARNING"
    environment: str = "production"


def get_settings() -> Settings:
    """根据环境变量获取配置"""
    env = os.getenv("ENVIRONMENT", "production").lower()
    
    settings_map = {
        "development": DevelopmentSettings,
        "test": TestSettings,
        "production": ProductionSettings,
    }
    
    settings_class = settings_map.get(env, ProductionSettings)
    return settings_class()


# 全局配置实例
settings = get_settings()
