"""
依赖注入模块
提供通用的依赖注入功能
"""

import logging
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Query, Path

from ..config.database import get_db, SessionLocal
from ..config.tenant_config import get_tenant_config, TenantConfig
from .security import get_current_user, CurrentUser

logger = logging.getLogger(__name__)


class TenantContext:
    """租户上下文"""
    
    def __init__(self, tenant_id: str, config: TenantConfig):
        self.tenant_id = tenant_id
        self.config = config
        self.name = config.tenant_name
        self.active = config.active
        self.features = config.features
        self.theme = config.theme
        self.notifications = config.notifications
        self.security = config.security
        self.custom_settings = config.custom_settings
    
    def has_feature(self, feature_name: str) -> bool:
        """检查是否启用某个功能"""
        return getattr(self.features, f"enable_{feature_name}", False)
    
    def get_custom_setting(self, key: str, default: Any = None) -> Any:
        """获取自定义设置"""
        return self.custom_settings.get(key, default)


async def get_tenant_context(
    tenant_id: Optional[str] = Query(None, description="租户ID"),
    current_user: CurrentUser = Depends(get_current_user),
) -> TenantContext:
    """获取租户上下文"""
    # 如果未提供租户ID，使用当前用户的租户ID
    if tenant_id is None:
        tenant_id = current_user.tenant_id
    
    # 如果不是超级用户，只能访问自己的租户
    if not current_user.is_superuser and tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问其他租户的数据",
        )
    
    try:
        config = get_tenant_config(tenant_id)
        if config is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"租户 {tenant_id} 不存在",
            )
        
        if not config.active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="租户账户已禁用",
            )
        
        return TenantContext(tenant_id, config)
        
    except Exception as e:
        logger.error(f"获取租户上下文失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取租户信息失败",
        )


class PaginationParams:
    """分页参数"""
    
    def __init__(
        self,
        page: int = Query(1, ge=1, description="页码"),
        size: int = Query(20, ge=1, le=100, description="每页数量"),
        sort_by: Optional[str] = Query(None, description="排序字段"),
        sort_order: str = Query("asc", regex="^(asc|desc)$", description="排序方向"),
    ):
        self.page = page
        self.size = size
        self.sort_by = sort_by
        self.sort_order = sort_order
        self.offset = (page - 1) * size
    
    @property
    def is_desc(self) -> bool:
        """是否降序"""
        return self.sort_order.lower() == "desc"


def get_pagination_params() -> PaginationParams:
    """获取分页参数依赖"""
    return Depends(PaginationParams)


class FilterParams:
    """通用过滤参数"""
    
    def __init__(
        self,
        search: Optional[str] = Query(None, description="搜索关键词"),
        status: Optional[str] = Query(None, description="状态过滤"),
        date_from: Optional[str] = Query(None, description="开始日期"),
        date_to: Optional[str] = Query(None, description="结束日期"),
        created_by: Optional[str] = Query(None, description="创建者过滤"),
    ):
        self.search = search
        self.status = status
        self.date_from = date_from
        self.date_to = date_to
        self.created_by = created_by
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            k: v for k, v in {
                "search": self.search,
                "status": self.status,
                "date_from": self.date_from,
                "date_to": self.date_to,
                "created_by": self.created_by,
            }.items() if v is not None
        }


def get_filter_params() -> FilterParams:
    """获取过滤参数依赖"""
    return Depends(FilterParams)


class IDParams:
    """ID参数验证"""
    
    @staticmethod
    def validate_user_id(user_id: str = Path(..., description="用户ID")):
        """验证用户ID"""
        if not user_id or len(user_id) < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的用户ID",
            )
        return user_id
    
    @staticmethod
    def validate_device_id(device_id: str = Path(..., description="设备ID")):
        """验证设备ID"""
        if not device_id or len(device_id) < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的设备ID",
            )
        return device_id
    
    @staticmethod
    def validate_tenant_id(tenant_id: str = Path(..., description="租户ID")):
        """验证租户ID"""
        if not tenant_id or len(tenant_id) < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的租户ID",
            )
        return tenant_id


class DatabaseSession:
    """数据库会话管理"""
    
    @staticmethod
    def get_session():
        """获取数据库会话"""
        return Depends(get_db)
    
    @staticmethod
    def get_tenant_session(tenant_context: TenantContext = Depends(get_tenant_context)):
        """获取租户数据库会话"""
        def _get_session():
            db = SessionLocal()
            try:
                # 这里可以添加租户特定的数据库逻辑
                # 例如设置租户上下文变量
                yield db
            finally:
                db.close()
        return Depends(_get_session)


class FeatureGuard:
    """功能保护装饰器"""
    
    @staticmethod
    def require_feature(feature_name: str):
        """需要特定功能启用"""
        def feature_checker(tenant_context: TenantContext = Depends(get_tenant_context)):
            if not tenant_context.has_feature(feature_name):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"功能 {feature_name} 未启用",
                )
            return tenant_context
        return feature_checker
    
    @staticmethod
    def user_management_required():
        """需要用户管理功能"""
        return FeatureGuard.require_feature("user_management")
    
    @staticmethod
    def device_management_required():
        """需要设备管理功能"""
        return FeatureGuard.require_feature("device_management")
    
    @staticmethod
    def intercom_required():
        """需要对讲功能"""
        return FeatureGuard.require_feature("intercom")
    
    @staticmethod
    def alarm_system_required():
        """需要报警系统功能"""
        return FeatureGuard.require_feature("alarm_system")
    
    @staticmethod
    def reports_required():
        """需要报表功能"""
        return FeatureGuard.require_feature("reports")


class ResourceValidator:
    """资源验证器"""
    
    @staticmethod
    async def validate_user_access(
        user_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        tenant_context: TenantContext = Depends(get_tenant_context),
    ):
        """验证用户访问权限"""
        # 超级用户可以访问所有资源
        if current_user.is_superuser:
            return True
        
        # 用户只能访问自己的资源或同租户的资源（如果有相应权限）
        if user_id == current_user.user_id:
            return True
        
        # 检查是否有管理其他用户的权限
        if current_user.has_permission("user:manage"):
            return True
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该用户资源",
        )
    
    @staticmethod
    async def validate_device_access(
        device_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        tenant_context: TenantContext = Depends(get_tenant_context),
    ):
        """验证设备访问权限"""
        # 超级用户可以访问所有设备
        if current_user.is_superuser:
            return True
        
        # 检查是否有设备管理权限
        if current_user.has_permission("device:read") or current_user.has_permission("device:manage"):
            return True
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该设备资源",
        )


class ServiceDependency:
    """服务依赖注入"""
    
    @staticmethod
    def get_user_service():
        """获取用户服务"""
        from ..services.user_service import UserService
        return UserService()
    
    @staticmethod
    def get_device_service():
        """获取设备服务"""
        from ..services.device_service import DeviceService
        return DeviceService()
    
    @staticmethod
    def get_auth_service():
        """获取认证服务"""
        from ..services.auth_service import AuthService
        return AuthService()
    
    @staticmethod
    def get_alarm_service():
        """获取报警服务"""
        from ..services.alarm_service import AlarmService
        return AlarmService()
    
    @staticmethod
    def get_log_service():
        """获取日志服务"""
        from ..services.log_service import LogService
        return LogService()


# 便捷的依赖注入实例
pagination_params = get_pagination_params()
filter_params = get_filter_params()
tenant_context_dep = Depends(get_tenant_context)
db_session = DatabaseSession.get_session()
feature_guard = FeatureGuard()
resource_validator = ResourceValidator()
service_dep = ServiceDependency()
