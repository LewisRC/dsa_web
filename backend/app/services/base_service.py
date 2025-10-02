"""
基础服务层
提供通用的业务逻辑操作
"""

import logging
from typing import Type, TypeVar, Generic, Optional, List, Dict, Any, Union
from abc import ABC, abstractmethod

from ..dao.base_dao import BaseDAO
from ..models.base import BaseModel
from ..core.exceptions import BusinessLogicError, ValidationError, NotFoundError
from ..core.dependencies import TenantContext

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)
D = TypeVar('D', bound=BaseDAO)


class BaseService(Generic[T, D], ABC):
    """基础服务类"""
    
    def __init__(self, dao: D):
        self.dao = dao
    
    @abstractmethod
    def _validate_create_data(self, data: Dict[str, Any], tenant_context: TenantContext = None) -> None:
        """验证创建数据"""
        pass
    
    @abstractmethod
    def _validate_update_data(self, data: Dict[str, Any], obj: T = None, tenant_context: TenantContext = None) -> None:
        """验证更新数据"""
        pass
    
    def _pre_create(self, data: Dict[str, Any], tenant_context: TenantContext = None) -> Dict[str, Any]:
        """创建前处理"""
        # 设置租户信息
        if tenant_context:
            data['tenant_id'] = tenant_context.tenant_id
        
        return data
    
    def _post_create(self, obj: T, tenant_context: TenantContext = None) -> T:
        """创建后处理"""
        return obj
    
    def _pre_update(self, obj: T, data: Dict[str, Any], tenant_context: TenantContext = None) -> Dict[str, Any]:
        """更新前处理"""
        return data
    
    def _post_update(self, obj: T, tenant_context: TenantContext = None) -> T:
        """更新后处理"""
        return obj
    
    def _pre_delete(self, obj: T, tenant_context: TenantContext = None) -> bool:
        """删除前处理"""
        return True
    
    def _post_delete(self, obj: T, tenant_context: TenantContext = None) -> None:
        """删除后处理"""
        pass
    
    def create(
        self,
        data: Dict[str, Any],
        tenant_context: TenantContext = None,
        created_by: str = None
    ) -> T:
        """创建记录"""
        try:
            # 验证数据
            self._validate_create_data(data, tenant_context)
            
            # 前置处理
            processed_data = self._pre_create(data, tenant_context)
            
            # 设置创建者
            if created_by:
                processed_data['created_by'] = created_by
            
            # 创建对象
            obj = self.dao.model(**processed_data)
            
            # 保存到数据库
            created_obj = self.dao.create(obj)
            
            # 后置处理
            result = self._post_create(created_obj, tenant_context)
            
            logger.info(f"创建{self.dao.model.__name__}成功: {result.id}")
            return result
            
        except Exception as e:
            logger.error(f"创建{self.dao.model.__name__}失败: {e}")
            raise
    
    def get_by_id(self, id: str, tenant_context: TenantContext = None) -> Optional[T]:
        """根据ID获取记录"""
        tenant_id = tenant_context.tenant_id if tenant_context else None
        return self.dao.get_by_id(id, tenant_id)
    
    def get_by_id_or_404(self, id: str, tenant_context: TenantContext = None) -> T:
        """根据ID获取记录，不存在则抛出404异常"""
        tenant_id = tenant_context.tenant_id if tenant_context else None
        return self.dao.get_by_id_or_404(id, tenant_id)
    
    def get_list(
        self,
        tenant_context: TenantContext = None,
        filters: Dict[str, Any] = None,
        search: str = None,
        search_fields: List[str] = None,
        sort_by: str = None,
        sort_order: str = "asc",
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """获取记录列表"""
        tenant_id = tenant_context.tenant_id if tenant_context else None
        
        # 计算偏移量
        offset = (page - 1) * size
        
        # 获取记录列表
        records = self.dao.get_list(
            tenant_id=tenant_id,
            filters=filters,
            search=search,
            search_fields=search_fields,
            sort_by=sort_by,
            sort_order=sort_order,
            offset=offset,
            limit=size
        )
        
        # 获取总数
        total = self.dao.count(
            tenant_id=tenant_id,
            filters=filters,
            search=search,
            search_fields=search_fields
        )
        
        return {
            "records": records,
            "pagination": {
                "page": page,
                "size": size,
                "total": total,
                "pages": (total + size - 1) // size
            }
        }
    
    def update(
        self,
        id: str,
        data: Dict[str, Any],
        tenant_context: TenantContext = None,
        updated_by: str = None
    ) -> T:
        """更新记录"""
        try:
            # 获取现有记录
            obj = self.get_by_id_or_404(id, tenant_context)
            
            # 验证更新数据
            self._validate_update_data(data, obj, tenant_context)
            
            # 前置处理
            processed_data = self._pre_update(obj, data, tenant_context)
            
            # 设置更新者
            if updated_by:
                processed_data['updated_by'] = updated_by
            
            # 更新记录
            updated_obj = self.dao.update(obj, processed_data)
            
            # 后置处理
            result = self._post_update(updated_obj, tenant_context)
            
            logger.info(f"更新{self.dao.model.__name__}成功: {result.id}")
            return result
            
        except Exception as e:
            logger.error(f"更新{self.dao.model.__name__}失败: {e}")
            raise
    
    def delete(
        self,
        id: str,
        tenant_context: TenantContext = None,
        soft_delete: bool = True,
        deleted_by: str = None
    ) -> bool:
        """删除记录"""
        try:
            # 获取现有记录
            obj = self.get_by_id_or_404(id, tenant_context)
            
            # 前置处理
            if not self._pre_delete(obj, tenant_context):
                raise BusinessLogicError("无法删除该记录")
            
            # 删除记录
            result = self.dao.delete(obj, soft_delete, deleted_by)
            
            # 后置处理
            self._post_delete(obj, tenant_context)
            
            logger.info(f"删除{self.dao.model.__name__}成功: {obj.id}")
            return result
            
        except Exception as e:
            logger.error(f"删除{self.dao.model.__name__}失败: {e}")
            raise
    
    def exists(self, id: str, tenant_context: TenantContext = None) -> bool:
        """检查记录是否存在"""
        tenant_id = tenant_context.tenant_id if tenant_context else None
        return self.dao.exists(id, tenant_id)
    
    def exists_by_field(
        self,
        field: str,
        value: Any,
        tenant_context: TenantContext = None,
        exclude_id: str = None
    ) -> bool:
        """根据字段值检查记录是否存在"""
        tenant_id = tenant_context.tenant_id if tenant_context else None
        return self.dao.exists_by_field(field, value, tenant_id, exclude_id)
    
    def get_statistics(self, tenant_context: TenantContext = None) -> Dict[str, Any]:
        """获取统计信息"""
        tenant_id = tenant_context.tenant_id if tenant_context else None
        return self.dao.get_statistics(tenant_id)
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> None:
        """验证必需字段"""
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                missing_fields.append(field)
        
        if missing_fields:
            raise ValidationError(f"缺少必需字段: {', '.join(missing_fields)}")
    
    def validate_field_length(self, data: Dict[str, Any], field_limits: Dict[str, int]) -> None:
        """验证字段长度"""
        for field, max_length in field_limits.items():
            if field in data and data[field] and len(str(data[field])) > max_length:
                raise ValidationError(f"字段 {field} 长度不能超过 {max_length} 个字符")
    
    def validate_field_format(self, data: Dict[str, Any], field_patterns: Dict[str, str]) -> None:
        """验证字段格式"""
        import re
        
        for field, pattern in field_patterns.items():
            if field in data and data[field]:
                if not re.match(pattern, str(data[field])):
                    raise ValidationError(f"字段 {field} 格式不正确")
    
    def validate_unique_field(
        self,
        field: str,
        value: Any,
        tenant_context: TenantContext = None,
        exclude_id: str = None
    ) -> None:
        """验证字段唯一性"""
        if self.exists_by_field(field, value, tenant_context, exclude_id):
            raise ValidationError(f"{field} 已存在")
    
    def validate_tenant_quota(
        self,
        tenant_context: TenantContext,
        resource_type: str,
        increment: int = 1
    ) -> None:
        """验证租户配额"""
        if not tenant_context or not tenant_context.config:
            return
        
        # 获取当前使用量
        current_count = self.dao.count(tenant_id=tenant_context.tenant_id)
        
        # 获取配额限制
        quota_field = f"max_{resource_type}"
        if hasattr(tenant_context.config, quota_field):
            max_quota = getattr(tenant_context.config, quota_field)
            if current_count + increment > max_quota:
                raise BusinessLogicError(f"超出{resource_type}配额限制({max_quota})")
    
    def validate_feature_enabled(self, tenant_context: TenantContext, feature_name: str) -> None:
        """验证功能是否启用"""
        if not tenant_context or not tenant_context.has_feature(feature_name):
            raise BusinessLogicError(f"功能 {feature_name} 未启用")
    
    def _log_operation(
        self,
        operation: str,
        obj_id: str,
        operator_id: str = None,
        details: Dict[str, Any] = None
    ) -> None:
        """记录操作日志"""
        try:
            from ..services.log_service import LogService
            from ..models.log import OperationLog
            
            log_service = LogService()
            log_data = {
                "operation_type": operation.upper(),
                "operation_name": f"{operation} {self.dao.model.__name__}",
                "resource_type": self.dao.model.__name__.lower(),
                "resource_id": obj_id,
                "user_id": operator_id,
                "success": True,
                "details": details or {}
            }
            
            # 这里应该异步处理日志记录
            # log_service.create_operation_log(log_data)
            
        except Exception as e:
            logger.error(f"记录操作日志失败: {e}")


class CacheableService(BaseService[T, D]):
    """支持缓存的服务基类"""
    
    def __init__(self, dao: D):
        super().__init__(dao)
        self.cache_enabled = False  # 是否启用缓存
        self.cache_ttl = 300  # 缓存过期时间（秒）
    
    def _get_cache_key(self, key: str, tenant_id: str = None) -> str:
        """生成缓存键"""
        prefix = f"{self.dao.model.__name__.lower()}"
        if tenant_id:
            prefix = f"{prefix}:{tenant_id}"
        return f"{prefix}:{key}"
    
    def _get_from_cache(self, cache_key: str) -> Any:
        """从缓存获取数据"""
        # 这里应该实现Redis缓存逻辑
        return None
    
    def _set_to_cache(self, cache_key: str, value: Any, ttl: int = None) -> None:
        """设置缓存数据"""
        # 这里应该实现Redis缓存逻辑
        pass
    
    def _delete_from_cache(self, cache_key: str) -> None:
        """删除缓存数据"""
        # 这里应该实现Redis缓存逻辑
        pass
    
    def _clear_cache_pattern(self, pattern: str) -> None:
        """清除匹配模式的缓存"""
        # 这里应该实现Redis缓存逻辑
        pass
    
    def get_by_id(self, id: str, tenant_context: TenantContext = None) -> Optional[T]:
        """根据ID获取记录（支持缓存）"""
        if not self.cache_enabled:
            return super().get_by_id(id, tenant_context)
        
        tenant_id = tenant_context.tenant_id if tenant_context else None
        cache_key = self._get_cache_key(f"id:{id}", tenant_id)
        
        # 尝试从缓存获取
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        # 从数据库获取
        result = super().get_by_id(id, tenant_context)
        
        # 存入缓存
        if result:
            self._set_to_cache(cache_key, result, self.cache_ttl)
        
        return result
    
    def update(
        self,
        id: str,
        data: Dict[str, Any],
        tenant_context: TenantContext = None,
        updated_by: str = None
    ) -> T:
        """更新记录（清除缓存）"""
        result = super().update(id, data, tenant_context, updated_by)
        
        if self.cache_enabled:
            tenant_id = tenant_context.tenant_id if tenant_context else None
            cache_key = self._get_cache_key(f"id:{id}", tenant_id)
            self._delete_from_cache(cache_key)
        
        return result
    
    def delete(
        self,
        id: str,
        tenant_context: TenantContext = None,
        soft_delete: bool = True,
        deleted_by: str = None
    ) -> bool:
        """删除记录（清除缓存）"""
        result = super().delete(id, tenant_context, soft_delete, deleted_by)
        
        if self.cache_enabled:
            tenant_id = tenant_context.tenant_id if tenant_context else None
            cache_key = self._get_cache_key(f"id:{id}", tenant_id)
            self._delete_from_cache(cache_key)
        
        return result
