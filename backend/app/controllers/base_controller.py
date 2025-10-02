"""
基础控制器层
提供通用的API接口操作
"""

import logging
from typing import Type, TypeVar, Generic, Dict, Any, List, Optional
from abc import ABC, abstractmethod

from fastapi import HTTPException, status, Query, Path, Depends
from pydantic import BaseModel as PydanticBaseModel

from ..services.base_service import BaseService
from ..models.base import BaseModel
from ..core.dependencies import TenantContext, PaginationParams, FilterParams, get_tenant_context
from ..core.security import CurrentUser, get_current_user
from ..core.exceptions import BusinessLogicError, ValidationError, NotFoundError

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)
S = TypeVar('S', bound=BaseService)


class StandardResponse(PydanticBaseModel):
    """标准响应模型"""
    success: bool = True
    message: str = "操作成功"
    data: Any = None
    error: Optional[Dict[str, Any]] = None


class PaginatedResponse(PydanticBaseModel):
    """分页响应模型"""
    success: bool = True
    message: str = "获取成功"
    data: List[Any] = []
    pagination: Dict[str, Any] = {}


class BaseController(Generic[T, S], ABC):
    """基础控制器类"""
    
    def __init__(self, service: S):
        self.service = service
    
    @abstractmethod
    def _to_response_model(self, obj: T) -> Dict[str, Any]:
        """将数据库对象转换为响应模型"""
        pass
    
    @abstractmethod
    def _get_search_fields(self) -> List[str]:
        """获取搜索字段列表"""
        pass
    
    def _to_response_list(self, objects: List[T]) -> List[Dict[str, Any]]:
        """将对象列表转换为响应模型列表"""
        return [self._to_response_model(obj) for obj in objects]
    
    def _handle_service_error(self, e: Exception) -> HTTPException:
        """处理服务层异常"""
        if isinstance(e, NotFoundError):
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=e.message
            )
        elif isinstance(e, ValidationError):
            return HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=e.message
            )
        elif isinstance(e, BusinessLogicError):
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message
            )
        else:
            logger.error(f"未处理的服务异常: {e}")
            return HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="内部服务器错误"
            )
    
    async def create_item(
        self,
        data: Dict[str, Any],
        tenant_context: TenantContext = Depends(get_tenant_context),
        current_user: CurrentUser = Depends(get_current_user)
    ) -> StandardResponse:
        """创建记录"""
        try:
            obj = self.service.create(data, tenant_context, current_user.user_id)
            response_data = self._to_response_model(obj)
            
            return StandardResponse(
                message="创建成功",
                data=response_data
            )
            
        except Exception as e:
            raise self._handle_service_error(e)
    
    async def get_item_by_id(
        self,
        item_id: str = Path(..., description="记录ID"),
        tenant_context: TenantContext = Depends(get_tenant_context),
        current_user: CurrentUser = Depends(get_current_user)
    ) -> StandardResponse:
        """根据ID获取记录"""
        try:
            obj = self.service.get_by_id_or_404(item_id, tenant_context)
            response_data = self._to_response_model(obj)
            
            return StandardResponse(
                message="获取成功",
                data=response_data
            )
            
        except Exception as e:
            raise self._handle_service_error(e)
    
    async def get_item_list(
        self,
        pagination: PaginationParams = Depends(PaginationParams),
        filters: FilterParams = Depends(FilterParams),
        tenant_context: TenantContext = Depends(get_tenant_context),
        current_user: CurrentUser = Depends(get_current_user)
    ) -> PaginatedResponse:
        """获取记录列表"""
        try:
            # 构建过滤条件
            filter_dict = {}
            if filters.status:
                filter_dict['status'] = filters.status
            if filters.created_by:
                filter_dict['created_by'] = filters.created_by
            if filters.date_from:
                filter_dict['created_at'] = {'operator': 'gte', 'value': filters.date_from}
            if filters.date_to:
                if 'created_at' in filter_dict:
                    # 如果已有created_at过滤，需要使用AND条件
                    pass  # 这里简化处理，实际需要更复杂的逻辑
                else:
                    filter_dict['created_at'] = {'operator': 'lte', 'value': filters.date_to}
            
            result = self.service.get_list(
                tenant_context=tenant_context,
                filters=filter_dict,
                search=filters.search,
                search_fields=self._get_search_fields(),
                sort_by=pagination.sort_by,
                sort_order=pagination.sort_order,
                page=pagination.page,
                size=pagination.size
            )
            
            response_data = self._to_response_list(result['records'])
            
            return PaginatedResponse(
                message="获取成功",
                data=response_data,
                pagination=result['pagination']
            )
            
        except Exception as e:
            raise self._handle_service_error(e)
    
    async def update_item(
        self,
        item_id: str,
        data: Dict[str, Any],
        tenant_context: TenantContext = Depends(get_tenant_context),
        current_user: CurrentUser = Depends(get_current_user)
    ) -> StandardResponse:
        """更新记录"""
        try:
            obj = self.service.update(item_id, data, tenant_context, current_user.user_id)
            response_data = self._to_response_model(obj)
            
            return StandardResponse(
                message="更新成功",
                data=response_data
            )
            
        except Exception as e:
            raise self._handle_service_error(e)
    
    async def delete_item(
        self,
        item_id: str = Path(..., description="记录ID"),
        permanent: bool = Query(False, description="是否永久删除"),
        tenant_context: TenantContext = Depends(get_tenant_context),
        current_user: CurrentUser = Depends(get_current_user)
    ) -> StandardResponse:
        """删除记录"""
        try:
            soft_delete = not permanent
            self.service.delete(item_id, tenant_context, soft_delete, current_user.user_id)
            
            return StandardResponse(
                message="删除成功"
            )
            
        except Exception as e:
            raise self._handle_service_error(e)
    
    async def get_statistics(
        self,
        tenant_context: TenantContext = Depends(get_tenant_context),
        current_user: CurrentUser = Depends(get_current_user)
    ) -> StandardResponse:
        """获取统计信息"""
        try:
            stats = self.service.get_statistics(tenant_context)
            
            return StandardResponse(
                message="获取统计信息成功",
                data=stats
            )
            
        except Exception as e:
            raise self._handle_service_error(e)


class CRUDController(BaseController[T, S]):
    """CRUD控制器基类"""
    
    def __init__(self, service: S, resource_name: str):
        super().__init__(service)
        self.resource_name = resource_name
    
    def create_routes(self) -> List[Dict[str, Any]]:
        """创建路由配置"""
        return [
            {
                "path": f"/{self.resource_name}",
                "method": "POST",
                "endpoint": self.create_item,
                "summary": f"创建{self.resource_name}",
                "response_model": StandardResponse
            },
            {
                "path": f"/{self.resource_name}/{{item_id}}",
                "method": "GET",
                "endpoint": self.get_item_by_id,
                "summary": f"获取{self.resource_name}详情",
                "response_model": StandardResponse
            },
            {
                "path": f"/{self.resource_name}",
                "method": "GET", 
                "endpoint": self.get_item_list,
                "summary": f"获取{self.resource_name}列表",
                "response_model": PaginatedResponse
            },
            {
                "path": f"/{self.resource_name}/{{item_id}}",
                "method": "PUT",
                "endpoint": self.update_item,
                "summary": f"更新{self.resource_name}",
                "response_model": StandardResponse
            },
            {
                "path": f"/{self.resource_name}/{{item_id}}",
                "method": "DELETE",
                "endpoint": self.delete_item,
                "summary": f"删除{self.resource_name}",
                "response_model": StandardResponse
            },
            {
                "path": f"/{self.resource_name}/statistics",
                "method": "GET",
                "endpoint": self.get_statistics,
                "summary": f"获取{self.resource_name}统计信息",
                "response_model": StandardResponse
            }
        ]


class ReadOnlyController(BaseController[T, S]):
    """只读控制器基类"""
    
    def __init__(self, service: S, resource_name: str):
        super().__init__(service)
        self.resource_name = resource_name
    
    def create_routes(self) -> List[Dict[str, Any]]:
        """创建路由配置"""
        return [
            {
                "path": f"/{self.resource_name}/{{item_id}}",
                "method": "GET",
                "endpoint": self.get_item_by_id,
                "summary": f"获取{self.resource_name}详情",
                "response_model": StandardResponse
            },
            {
                "path": f"/{self.resource_name}",
                "method": "GET",
                "endpoint": self.get_item_list,
                "summary": f"获取{self.resource_name}列表",
                "response_model": PaginatedResponse
            },
            {
                "path": f"/{self.resource_name}/statistics",
                "method": "GET",
                "endpoint": self.get_statistics,
                "summary": f"获取{self.resource_name}统计信息",
                "response_model": StandardResponse
            }
        ]


class BatchController(BaseController[T, S]):
    """批量操作控制器基类"""
    
    async def batch_create(
        self,
        data_list: List[Dict[str, Any]],
        tenant_context: TenantContext = Depends(get_tenant_context),
        current_user: CurrentUser = Depends(get_current_user)
    ) -> StandardResponse:
        """批量创建记录"""
        try:
            created_objects = []
            
            for data in data_list:
                obj = self.service.create(data, tenant_context, current_user.user_id)
                created_objects.append(obj)
            
            response_data = self._to_response_list(created_objects)
            
            return StandardResponse(
                message=f"批量创建成功，共创建{len(created_objects)}条记录",
                data=response_data
            )
            
        except Exception as e:
            raise self._handle_service_error(e)
    
    async def batch_update(
        self,
        updates: List[Dict[str, Any]],  # [{"id": "xxx", "data": {...}}, ...]
        tenant_context: TenantContext = Depends(get_tenant_context),
        current_user: CurrentUser = Depends(get_current_user)
    ) -> StandardResponse:
        """批量更新记录"""
        try:
            updated_objects = []
            
            for update in updates:
                obj = self.service.update(
                    update['id'], 
                    update['data'], 
                    tenant_context, 
                    current_user.user_id
                )
                updated_objects.append(obj)
            
            response_data = self._to_response_list(updated_objects)
            
            return StandardResponse(
                message=f"批量更新成功，共更新{len(updated_objects)}条记录",
                data=response_data
            )
            
        except Exception as e:
            raise self._handle_service_error(e)
    
    async def batch_delete(
        self,
        item_ids: List[str],
        permanent: bool = Query(False, description="是否永久删除"),
        tenant_context: TenantContext = Depends(get_tenant_context),
        current_user: CurrentUser = Depends(get_current_user)
    ) -> StandardResponse:
        """批量删除记录"""
        try:
            deleted_count = 0
            soft_delete = not permanent
            
            for item_id in item_ids:
                if self.service.delete(item_id, tenant_context, soft_delete, current_user.user_id):
                    deleted_count += 1
            
            return StandardResponse(
                message=f"批量删除成功，共删除{deleted_count}条记录"
            )
            
        except Exception as e:
            raise self._handle_service_error(e)
    
    def create_batch_routes(self) -> List[Dict[str, Any]]:
        """创建批量操作路由配置"""
        return [
            {
                "path": f"/{self.resource_name}/batch",
                "method": "POST",
                "endpoint": self.batch_create,
                "summary": f"批量创建{self.resource_name}",
                "response_model": StandardResponse
            },
            {
                "path": f"/{self.resource_name}/batch",
                "method": "PUT",
                "endpoint": self.batch_update,
                "summary": f"批量更新{self.resource_name}",
                "response_model": StandardResponse
            },
            {
                "path": f"/{self.resource_name}/batch",
                "method": "DELETE",
                "endpoint": self.batch_delete,
                "summary": f"批量删除{self.resource_name}",
                "response_model": StandardResponse
            }
        ]


class ExportController(BaseController[T, S]):
    """导出控制器基类"""
    
    async def export_csv(
        self,
        filters: FilterParams = Depends(FilterParams),
        tenant_context: TenantContext = Depends(get_tenant_context),
        current_user: CurrentUser = Depends(get_current_user)
    ):
        """导出CSV格式"""
        from fastapi.responses import StreamingResponse
        import csv
        import io
        
        try:
            # 获取所有数据（不分页）
            result = self.service.get_list(
                tenant_context=tenant_context,
                filters=filters.to_dict(),
                search=filters.search,
                search_fields=self._get_search_fields(),
                page=1,
                size=10000  # 设置一个较大的限制
            )
            
            # 生成CSV数据
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 写入表头
            if result['records']:
                headers = list(self._to_response_model(result['records'][0]).keys())
                writer.writerow(headers)
                
                # 写入数据行
                for record in result['records']:
                    row_data = self._to_response_model(record)
                    writer.writerow([str(row_data.get(h, '')) for h in headers])
            
            output.seek(0)
            
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode('utf-8-sig')),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={self.resource_name}.csv"}
            )
            
        except Exception as e:
            raise self._handle_service_error(e)
    
    async def export_excel(
        self,
        filters: FilterParams = Depends(FilterParams),
        tenant_context: TenantContext = Depends(get_tenant_context),
        current_user: CurrentUser = Depends(get_current_user)
    ):
        """导出Excel格式"""
        from fastapi.responses import StreamingResponse
        import pandas as pd
        import io
        
        try:
            # 获取所有数据
            result = self.service.get_list(
                tenant_context=tenant_context,
                filters=filters.to_dict(),
                search=filters.search,
                search_fields=self._get_search_fields(),
                page=1,
                size=10000
            )
            
            # 转换为DataFrame
            if result['records']:
                data = [self._to_response_model(record) for record in result['records']]
                df = pd.DataFrame(data)
            else:
                df = pd.DataFrame()
            
            # 生成Excel文件
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name=self.resource_name)
            
            output.seek(0)
            
            return StreamingResponse(
                output,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename={self.resource_name}.xlsx"}
            )
            
        except Exception as e:
            raise self._handle_service_error(e)
    
    def create_export_routes(self) -> List[Dict[str, Any]]:
        """创建导出路由配置"""
        return [
            {
                "path": f"/{self.resource_name}/export/csv",
                "method": "GET",
                "endpoint": self.export_csv,
                "summary": f"导出{self.resource_name}为CSV格式"
            },
            {
                "path": f"/{self.resource_name}/export/excel",
                "method": "GET",
                "endpoint": self.export_excel,
                "summary": f"导出{self.resource_name}为Excel格式"
            }
        ]
