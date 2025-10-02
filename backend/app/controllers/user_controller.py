"""
用户控制器层
提供用户相关的API接口
"""

from typing import Dict, Any, List
from datetime import datetime

from fastapi import Depends, HTTPException, status, Query, Path, Body
from pydantic import BaseModel, Field, EmailStr

from .base_controller import CRUDController, BatchController, ExportController, StandardResponse
from ..services.user_service import UserService
from ..models.user import User, Role
from ..core.dependencies import TenantContext, get_tenant_context
from ..core.security import CurrentUser, get_current_user, require_permission, require_role


# Pydantic模型定义
class UserCreateRequest(BaseModel):
    """创建用户请求模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=8, description="密码")
    real_name: str = Field(None, max_length=100, description="真实姓名")
    phone: str = Field(None, max_length=20, description="手机号")
    department: str = Field(None, max_length=100, description="部门")
    position: str = Field(None, max_length=100, description="职位")
    is_active: bool = Field(True, description="是否激活")


class UserUpdateRequest(BaseModel):
    """更新用户请求模型"""
    email: EmailStr = Field(None, description="邮箱地址")
    real_name: str = Field(None, max_length=100, description="真实姓名")
    phone: str = Field(None, max_length=20, description="手机号")
    department: str = Field(None, max_length=100, description="部门")
    position: str = Field(None, max_length=100, description="职位")
    is_active: bool = Field(None, description="是否激活")


class PasswordChangeRequest(BaseModel):
    """修改密码请求模型"""
    old_password: str = Field(..., description="原密码")
    new_password: str = Field(..., min_length=8, description="新密码")


class PasswordResetRequest(BaseModel):
    """重置密码请求模型"""
    new_password: str = Field(..., min_length=8, description="新密码")


class RoleAssignRequest(BaseModel):
    """角色分配请求模型"""
    role_ids: List[str] = Field(..., description="角色ID列表")


class UserResponse(BaseModel):
    """用户响应模型"""
    id: str
    username: str
    email: str
    real_name: str = None
    phone: str = None
    department: str = None
    position: str = None
    is_active: bool
    is_superuser: bool
    is_staff: bool
    last_login: datetime = None
    login_count: int = 0
    created_at: datetime
    updated_at: datetime


class UserController(CRUDController[User, UserService], BatchController, ExportController):
    """用户控制器"""
    
    def __init__(self):
        super().__init__(UserService(), "users")
    
    def _to_response_model(self, obj: User) -> Dict[str, Any]:
        """将用户对象转换为响应模型"""
        return {
            "id": obj.id,
            "username": obj.username,
            "email": obj.email,
            "real_name": obj.real_name,
            "nickname": obj.nickname,
            "phone": obj.phone,
            "gender": obj.gender,
            "department": obj.department,
            "position": obj.position,
            "employee_id": obj.employee_id,
            "is_active": obj.is_active,
            "is_superuser": obj.is_superuser,
            "is_staff": obj.is_staff,
            "last_login": obj.last_login.isoformat() if obj.last_login else None,
            "login_count": obj.login_count,
            "failed_login_count": obj.failed_login_count,
            "locked_until": obj.locked_until.isoformat() if obj.locked_until else None,
            "language": obj.language,
            "timezone": obj.timezone,
            "theme": obj.theme,
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
        }
    
    def _get_search_fields(self) -> List[str]:
        """获取搜索字段列表"""
        return ["username", "real_name", "email", "phone", "department", "position"]
    
    async def create_user(
        self,
        user_data: UserCreateRequest,
        tenant_context: TenantContext = Depends(get_tenant_context),
        current_user: CurrentUser = Depends(require_permission("user:create"))
    ) -> StandardResponse:
        """创建用户"""
        return await self.create_item(user_data.dict(), tenant_context, current_user)
    
    async def update_user(
        self,
        user_id: str = Path(..., description="用户ID"),
        user_data: UserUpdateRequest = Body(...),
        tenant_context: TenantContext = Depends(get_tenant_context),
        current_user: CurrentUser = Depends(require_permission("user:update"))
    ) -> StandardResponse:
        """更新用户"""
        # 过滤掉None值
        update_data = {k: v for k, v in user_data.dict().items() if v is not None}
        return await self.update_item(user_id, update_data, tenant_context, current_user)
    
    async def change_password(
        self,
        user_id: str = Path(..., description="用户ID"),
        password_data: PasswordChangeRequest = Body(...),
        tenant_context: TenantContext = Depends(get_tenant_context),
        current_user: CurrentUser = Depends(get_current_user)
    ) -> StandardResponse:
        """修改密码"""
        try:
            # 只能修改自己的密码，除非有管理权限
            if user_id != current_user.user_id and not current_user.has_permission("user:manage"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权修改其他用户的密码"
                )
            
            success = self.service.change_password(
                user_id,
                password_data.old_password,
                password_data.new_password,
                tenant_context
            )
            
            if success:
                return StandardResponse(message="密码修改成功")
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="密码修改失败"
                )
                
        except Exception as e:
            raise self._handle_service_error(e)
    
    async def reset_password(
        self,
        user_id: str = Path(..., description="用户ID"),
        password_data: PasswordResetRequest = Body(...),
        tenant_context: TenantContext = Depends(get_tenant_context),
        current_user: CurrentUser = Depends(require_permission("user:manage"))
    ) -> StandardResponse:
        """重置密码（管理员操作）"""
        try:
            success = self.service.reset_password(
                user_id,
                password_data.new_password,
                tenant_context,
                current_user.user_id
            )
            
            if success:
                return StandardResponse(message="密码重置成功")
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="密码重置失败"
                )
                
        except Exception as e:
            raise self._handle_service_error(e)
    
    async def lock_user(
        self,
        user_id: str = Path(..., description="用户ID"),
        tenant_context: TenantContext = Depends(get_tenant_context),
        current_user: CurrentUser = Depends(require_permission("user:manage"))
    ) -> StandardResponse:
        """锁定用户"""
        try:
            success = self.service.lock_user(user_id, tenant_context, current_user.user_id)
            
            if success:
                return StandardResponse(message="用户锁定成功")
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户锁定失败"
                )
                
        except Exception as e:
            raise self._handle_service_error(e)
    
    async def unlock_user(
        self,
        user_id: str = Path(..., description="用户ID"),
        tenant_context: TenantContext = Depends(get_tenant_context),
        current_user: CurrentUser = Depends(require_permission("user:manage"))
    ) -> StandardResponse:
        """解锁用户"""
        try:
            success = self.service.unlock_user(user_id, tenant_context, current_user.user_id)
            
            if success:
                return StandardResponse(message="用户解锁成功")
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户解锁失败"
                )
                
        except Exception as e:
            raise self._handle_service_error(e)
    
    async def activate_user(
        self,
        user_id: str = Path(..., description="用户ID"),
        tenant_context: TenantContext = Depends(get_tenant_context),
        current_user: CurrentUser = Depends(require_permission("user:manage"))
    ) -> StandardResponse:
        """激活用户"""
        try:
            success = self.service.activate_user(user_id, tenant_context, current_user.user_id)
            
            if success:
                return StandardResponse(message="用户激活成功")
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户激活失败"
                )
                
        except Exception as e:
            raise self._handle_service_error(e)
    
    async def deactivate_user(
        self,
        user_id: str = Path(..., description="用户ID"),
        tenant_context: TenantContext = Depends(get_tenant_context),
        current_user: CurrentUser = Depends(require_permission("user:manage"))
    ) -> StandardResponse:
        """停用用户"""
        try:
            success = self.service.deactivate_user(user_id, tenant_context, current_user.user_id)
            
            if success:
                return StandardResponse(message="用户停用成功")
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户停用失败"
                )
                
        except Exception as e:
            raise self._handle_service_error(e)
    
    async def get_user_roles(
        self,
        user_id: str = Path(..., description="用户ID"),
        tenant_context: TenantContext = Depends(get_tenant_context),
        current_user: CurrentUser = Depends(get_current_user)
    ) -> StandardResponse:
        """获取用户角色列表"""
        try:
            # 只能查看自己的角色，除非有管理权限
            if user_id != current_user.user_id and not current_user.has_permission("user:read"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权查看其他用户的角色"
                )
            
            roles = self.service.get_user_roles(user_id, tenant_context)
            
            role_data = [
                {
                    "id": role.id,
                    "name": role.name,
                    "code": role.code,
                    "description": role.description,
                    "is_active": role.is_active,
                    "is_system": role.is_system
                }
                for role in roles
            ]
            
            return StandardResponse(
                message="获取用户角色成功",
                data=role_data
            )
            
        except Exception as e:
            raise self._handle_service_error(e)
    
    async def assign_roles(
        self,
        user_id: str = Path(..., description="用户ID"),
        role_data: RoleAssignRequest = Body(...),
        tenant_context: TenantContext = Depends(get_tenant_context),
        current_user: CurrentUser = Depends(require_permission("user:manage"))
    ) -> StandardResponse:
        """为用户分配角色"""
        try:
            success_count = 0
            
            for role_id in role_data.role_ids:
                if self.service.assign_role(user_id, role_id, tenant_context, current_user.user_id):
                    success_count += 1
            
            return StandardResponse(
                message=f"角色分配成功，共分配{success_count}个角色"
            )
            
        except Exception as e:
            raise self._handle_service_error(e)
    
    async def remove_role(
        self,
        user_id: str = Path(..., description="用户ID"),
        role_id: str = Path(..., description="角色ID"),
        tenant_context: TenantContext = Depends(get_tenant_context),
        current_user: CurrentUser = Depends(require_permission("user:manage"))
    ) -> StandardResponse:
        """移除用户角色"""
        try:
            success = self.service.remove_role(user_id, role_id, tenant_context)
            
            if success:
                return StandardResponse(message="角色移除成功")
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="角色移除失败"
                )
                
        except Exception as e:
            raise self._handle_service_error(e)
    
    async def get_user_permissions(
        self,
        user_id: str = Path(..., description="用户ID"),
        tenant_context: TenantContext = Depends(get_tenant_context),
        current_user: CurrentUser = Depends(get_current_user)
    ) -> StandardResponse:
        """获取用户权限列表"""
        try:
            # 只能查看自己的权限，除非有管理权限
            if user_id != current_user.user_id and not current_user.has_permission("user:read"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权查看其他用户的权限"
                )
            
            permissions = self.service.get_user_permissions(user_id, tenant_context)
            
            return StandardResponse(
                message="获取用户权限成功",
                data=permissions
            )
            
        except Exception as e:
            raise self._handle_service_error(e)
    
    async def search_users(
        self,
        keyword: str = Query(..., description="搜索关键词"),
        include_inactive: bool = Query(False, description="是否包含非活跃用户"),
        tenant_context: TenantContext = Depends(get_tenant_context),
        current_user: CurrentUser = Depends(require_permission("user:read"))
    ) -> StandardResponse:
        """搜索用户"""
        try:
            users = self.service.search_users(keyword, tenant_context, include_inactive)
            response_data = self._to_response_list(users)
            
            return StandardResponse(
                message="搜索用户成功",
                data=response_data
            )
            
        except Exception as e:
            raise self._handle_service_error(e)
    
    async def get_users_by_role(
        self,
        role_code: str = Query(..., description="角色代码"),
        tenant_context: TenantContext = Depends(get_tenant_context),
        current_user: CurrentUser = Depends(require_permission("user:read"))
    ) -> StandardResponse:
        """根据角色获取用户列表"""
        try:
            users = self.service.get_users_by_role(role_code, tenant_context)
            response_data = self._to_response_list(users)
            
            return StandardResponse(
                message="获取角色用户成功",
                data=response_data
            )
            
        except Exception as e:
            raise self._handle_service_error(e)
    
    async def get_current_user_info(
        self,
        current_user: CurrentUser = Depends(get_current_user),
        tenant_context: TenantContext = Depends(get_tenant_context)
    ) -> StandardResponse:
        """获取当前用户信息"""
        try:
            user = self.service.get_by_id_or_404(current_user.user_id, tenant_context)
            response_data = self._to_response_model(user)
            
            # 添加角色和权限信息
            response_data["roles"] = [
                {"code": role, "name": role}
                for role in current_user.roles
            ]
            response_data["permissions"] = list(current_user.permissions)
            
            return StandardResponse(
                message="获取当前用户信息成功",
                data=response_data
            )
            
        except Exception as e:
            raise self._handle_service_error(e)
    
    async def update_current_user_info(
        self,
        user_data: UserUpdateRequest = Body(...),
        current_user: CurrentUser = Depends(get_current_user),
        tenant_context: TenantContext = Depends(get_tenant_context)
    ) -> StandardResponse:
        """更新当前用户信息"""
        # 过滤掉None值和敏感字段
        update_data = {k: v for k, v in user_data.dict().items() if v is not None}
        # 普通用户不能修改自己的激活状态
        update_data.pop('is_active', None)
        
        return await self.update_item(current_user.user_id, update_data, tenant_context, current_user)
    
    async def check_password_expiry(
        self,
        user_id: str = Path(..., description="用户ID"),
        tenant_context: TenantContext = Depends(get_tenant_context),
        current_user: CurrentUser = Depends(get_current_user)
    ) -> StandardResponse:
        """检查密码是否过期"""
        try:
            # 只能检查自己的密码过期状态，除非有管理权限
            if user_id != current_user.user_id and not current_user.has_permission("user:read"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权检查其他用户的密码状态"
                )
            
            user = self.service.get_by_id_or_404(user_id, tenant_context)
            password_info = self.service.check_password_expiry(user, tenant_context)
            
            return StandardResponse(
                message="获取密码状态成功",
                data=password_info
            )
            
        except Exception as e:
            raise self._handle_service_error(e)
