"""
租户配置管理
支持多租户的配置和主题定制
"""

import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class TenantThemeConfig:
    """租户主题配置"""
    primary_color: str = "#1890ff"
    secondary_color: str = "#722ed1"
    success_color: str = "#52c41a"
    warning_color: str = "#faad14"
    error_color: str = "#f5222d"
    background_color: str = "#ffffff"
    text_color: str = "#000000"
    border_radius: str = "6px"
    font_family: str = "Arial, sans-serif"
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None


@dataclass
class TenantFeatureConfig:
    """租户功能配置"""
    enable_user_management: bool = True
    enable_device_management: bool = True
    enable_intercom: bool = True
    enable_alarm_system: bool = True
    enable_reports: bool = True
    enable_multi_language: bool = False
    enable_dark_mode: bool = True
    enable_notifications: bool = True
    enable_file_upload: bool = True
    max_users: int = 1000
    max_devices: int = 500
    max_concurrent_calls: int = 10


@dataclass
class TenantNotificationConfig:
    """租户通知配置"""
    email_enabled: bool = False
    sms_enabled: bool = False
    push_enabled: bool = True
    webhook_enabled: bool = False
    email_templates: Dict[str, str] = None
    webhook_url: Optional[str] = None
    notification_channels: List[str] = None
    
    def __post_init__(self):
        if self.email_templates is None:
            self.email_templates = {}
        if self.notification_channels is None:
            self.notification_channels = ["system", "alarm", "device"]


@dataclass
class TenantSecurityConfig:
    """租户安全配置"""
    password_policy: Dict[str, Any] = None
    session_timeout: int = 1800  # 30分钟
    max_login_attempts: int = 5
    lockout_duration: int = 900  # 15分钟
    two_factor_auth: bool = False
    ip_whitelist: List[str] = None
    api_rate_limit: Dict[str, int] = None
    
    def __post_init__(self):
        if self.password_policy is None:
            self.password_policy = {
                "min_length": 8,
                "require_uppercase": True,
                "require_lowercase": True,
                "require_numbers": True,
                "require_special_chars": True,
                "max_age_days": 90
            }
        if self.ip_whitelist is None:
            self.ip_whitelist = []
        if self.api_rate_limit is None:
            self.api_rate_limit = {
                "requests_per_minute": 60,
                "requests_per_hour": 1000
            }


@dataclass
class TenantConfig:
    """租户完整配置"""
    tenant_id: str
    tenant_name: str
    domain: Optional[str] = None
    active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    theme: TenantThemeConfig = None
    features: TenantFeatureConfig = None
    notifications: TenantNotificationConfig = None
    security: TenantSecurityConfig = None
    custom_settings: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.theme is None:
            self.theme = TenantThemeConfig()
        if self.features is None:
            self.features = TenantFeatureConfig()
        if self.notifications is None:
            self.notifications = TenantNotificationConfig()
        if self.security is None:
            self.security = TenantSecurityConfig()
        if self.custom_settings is None:
            self.custom_settings = {}


class TenantConfigManager:
    """租户配置管理器"""
    
    def __init__(self, config_dir: str = "./tenant_configs"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self._configs: Dict[str, TenantConfig] = {}
        self._load_all_configs()
    
    def _get_config_file_path(self, tenant_id: str) -> Path:
        """获取租户配置文件路径"""
        return self.config_dir / f"{tenant_id}.json"
    
    def _load_all_configs(self):
        """加载所有租户配置"""
        try:
            for config_file in self.config_dir.glob("*.json"):
                tenant_id = config_file.stem
                self._load_config(tenant_id)
            logger.info(f"加载了 {len(self._configs)} 个租户配置")
        except Exception as e:
            logger.error(f"加载租户配置失败: {e}")
    
    def _load_config(self, tenant_id: str) -> Optional[TenantConfig]:
        """加载单个租户配置"""
        config_file = self._get_config_file_path(tenant_id)
        if not config_file.exists():
            return None
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 转换嵌套配置对象
            if 'theme' in config_data and isinstance(config_data['theme'], dict):
                config_data['theme'] = TenantThemeConfig(**config_data['theme'])
            
            if 'features' in config_data and isinstance(config_data['features'], dict):
                config_data['features'] = TenantFeatureConfig(**config_data['features'])
            
            if 'notifications' in config_data and isinstance(config_data['notifications'], dict):
                config_data['notifications'] = TenantNotificationConfig(**config_data['notifications'])
            
            if 'security' in config_data and isinstance(config_data['security'], dict):
                config_data['security'] = TenantSecurityConfig(**config_data['security'])
            
            config = TenantConfig(**config_data)
            self._configs[tenant_id] = config
            return config
            
        except Exception as e:
            logger.error(f"加载租户配置 {tenant_id} 失败: {e}")
            return None
    
    def _save_config(self, config: TenantConfig):
        """保存租户配置"""
        config_file = self._get_config_file_path(config.tenant_id)
        
        try:
            # 转换为字典并处理嵌套对象
            config_dict = asdict(config)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, ensure_ascii=False, indent=2)
            
            logger.info(f"租户配置 {config.tenant_id} 保存成功")
            
        except Exception as e:
            logger.error(f"保存租户配置 {config.tenant_id} 失败: {e}")
            raise
    
    def get_config(self, tenant_id: str) -> Optional[TenantConfig]:
        """获取租户配置"""
        if tenant_id not in self._configs:
            config = self._load_config(tenant_id)
            if config is None:
                return self._create_default_config(tenant_id)
            return config
        return self._configs[tenant_id]
    
    def _create_default_config(self, tenant_id: str) -> TenantConfig:
        """创建默认租户配置"""
        config = TenantConfig(
            tenant_id=tenant_id,
            tenant_name=f"租户 {tenant_id}",
        )
        self._configs[tenant_id] = config
        self._save_config(config)
        return config
    
    def update_config(self, tenant_id: str, updates: Dict[str, Any]) -> TenantConfig:
        """更新租户配置"""
        config = self.get_config(tenant_id)
        if config is None:
            raise ValueError(f"租户 {tenant_id} 不存在")
        
        # 更新配置字段
        for key, value in updates.items():
            if hasattr(config, key):
                setattr(config, key, value)
            elif key in ['theme', 'features', 'notifications', 'security']:
                nested_config = getattr(config, key)
                if isinstance(value, dict) and nested_config:
                    for nested_key, nested_value in value.items():
                        if hasattr(nested_config, nested_key):
                            setattr(nested_config, nested_key, nested_value)
            else:
                config.custom_settings[key] = value
        
        self._save_config(config)
        return config
    
    def delete_config(self, tenant_id: str):
        """删除租户配置"""
        config_file = self._get_config_file_path(tenant_id)
        if config_file.exists():
            config_file.unlink()
        
        if tenant_id in self._configs:
            del self._configs[tenant_id]
        
        logger.info(f"租户配置 {tenant_id} 已删除")
    
    def list_tenants(self) -> List[str]:
        """列出所有租户ID"""
        return list(self._configs.keys())
    
    def get_active_tenants(self) -> List[TenantConfig]:
        """获取活跃租户配置"""
        return [config for config in self._configs.values() if config.active]
    
    def export_config(self, tenant_id: str) -> Dict[str, Any]:
        """导出租户配置"""
        config = self.get_config(tenant_id)
        if config is None:
            raise ValueError(f"租户 {tenant_id} 不存在")
        return asdict(config)
    
    def import_config(self, config_data: Dict[str, Any]) -> TenantConfig:
        """导入租户配置"""
        if 'tenant_id' not in config_data:
            raise ValueError("配置数据必须包含 tenant_id")
        
        tenant_id = config_data['tenant_id']
        
        # 转换嵌套配置对象
        if 'theme' in config_data and isinstance(config_data['theme'], dict):
            config_data['theme'] = TenantThemeConfig(**config_data['theme'])
        
        if 'features' in config_data and isinstance(config_data['features'], dict):
            config_data['features'] = TenantFeatureConfig(**config_data['features'])
        
        if 'notifications' in config_data and isinstance(config_data['notifications'], dict):
            config_data['notifications'] = TenantNotificationConfig(**config_data['notifications'])
        
        if 'security' in config_data and isinstance(config_data['security'], dict):
            config_data['security'] = TenantSecurityConfig(**config_data['security'])
        
        config = TenantConfig(**config_data)
        self._configs[tenant_id] = config
        self._save_config(config)
        
        return config


# 全局租户配置管理器实例
tenant_config_manager = TenantConfigManager()


def get_tenant_config(tenant_id: str) -> TenantConfig:
    """获取租户配置的便捷函数"""
    return tenant_config_manager.get_config(tenant_id)
