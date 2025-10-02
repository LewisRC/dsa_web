"""
认证控制器
提供用户登录、登出、令牌刷新等认证相关API
"""

from typing import Dict, Any
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status, Body
from pydantic import BaseModel, Field, EmailStr

from .base_controller import StandardResponse
from ..services.user_service import UserService
from ..core.dependencies import TenantContext, get_tenant_context
from ..core.security import CurrentUser, get_current_user, security_manager
from ..core.exceptions import AuthenticationError


class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")
    remember_me: bool = Field(False, description="记住我")


class LoginResponse(BaseModel):
    """登录响应模型"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    user_info: Dict[str, Any]


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模型"""
    refresh_token: str = Field(..., description="刷新令牌")


class AuthController:
    """认证控制器"""
    
    def __init__(self):
        self.user_service = UserService()
    
    async def login(
        self,
        login_data: LoginRequest = Body(...),
        tenant_context: TenantContext = Depends(get_tenant_context)
    ) -> StandardResponse:
        """用户登录"""
        try:
            # 用户认证
            user = self.user_service.authenticate_user(
                login_data.username,
                login_data.password,
                tenant_context
            )
            
            if not user:
                raise AuthenticationError("用户名或密码错误")
            
            # 获取用户角色和权限
            roles = self.user_service.get_user_roles(user.id, tenant_context)
            permissions = self.user_service.get_user_permissions(user.id, tenant_context)
            
            # 生成JWT令牌
            token_data = {
                "sub": user.id,
                "username": user.username,
                "email": user.email,
                "tenant_id": user.tenant_id,
                "roles": [role.code for role in roles],
                "permissions": permissions,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
            }
            
            # 设置令牌过期时间
            access_token_expires = timedelta(minutes=security_manager.access_token_expire_minutes)
            if login_data.remember_me:
                access_token_expires = timedelta(days=7)  # 记住我：7天
            
            refresh_token_expires = timedelta(days=security_manager.refresh_token_expire_days)
            
            # 创建令牌
            access_token = security_manager.create_access_token(token_data, access_token_expires)
            refresh_token = security_manager.create_refresh_token(
                {"sub": user.id, "tenant_id": user.tenant_id}, 
                refresh_token_expires
            )
            
            # 用户信息
            user_info = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "real_name": user.real_name,
                "nickname": user.nickname,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
                "roles": [{"code": role.code, "name": role.name} for role in roles],
                "permissions": permissions,
                "last_login": user.last_login.isoformat() if user.last_login else None,
            }
            
            response_data = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                "expires_in": int(access_token_expires.total_seconds()),
                "user_info": user_info
            }
            
            # 记录登录日志
            # TODO: 实现登录日志记录
            
            return StandardResponse(
                message="登录成功",
                data=response_data
            )
            
        except AuthenticationError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="登录过程发生错误"
            )
    
    async def logout(
        self,
        current_user: CurrentUser = Depends(get_current_user)
    ) -> StandardResponse:
        """用户登出"""
        try:
            # TODO: 实现令牌黑名单或会话管理
            # 这里可以将令牌加入黑名单，或者清理用户会话
            
            # 记录登出日志
            # TODO: 实现登出日志记录
            
            return StandardResponse(
                message="登出成功"
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="登出过程发生错误"
            )
    
    async def refresh_token(
        self,
        refresh_data: RefreshTokenRequest = Body(...),
        tenant_context: TenantContext = Depends(get_tenant_context)
    ) -> StandardResponse:
        """刷新访问令牌"""
        try:
            # 验证刷新令牌
            payload = security_manager.verify_refresh_token(refresh_data.refresh_token)
            
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的刷新令牌"
                )
            
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="令牌格式错误"
                )
            
            # 获取用户信息
            user = self.user_service.get_by_id(user_id, tenant_context)
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户账户已禁用"
                )
            
            # 获取用户角色和权限
            roles = self.user_service.get_user_roles(user.id, tenant_context)
            permissions = self.user_service.get_user_permissions(user.id, tenant_context)
            
            # 生成新的访问令牌
            token_data = {
                "sub": user.id,
                "username": user.username,
                "email": user.email,
                "tenant_id": user.tenant_id,
                "roles": [role.code for role in roles],
                "permissions": permissions,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
            }
            
            access_token_expires = timedelta(minutes=security_manager.access_token_expire_minutes)
            new_access_token = security_manager.create_access_token(token_data, access_token_expires)
            
            response_data = {
                "access_token": new_access_token,
                "token_type": "Bearer",
                "expires_in": int(access_token_expires.total_seconds())
            }
            
            return StandardResponse(
                message="令牌刷新成功",
                data=response_data
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="令牌刷新失败"
            )
    
    async def get_current_user_info(
        self,
        current_user: CurrentUser = Depends(get_current_user),
        tenant_context: TenantContext = Depends(get_tenant_context)
    ) -> StandardResponse:
        """获取当前用户信息"""
        try:
            user = self.user_service.get_by_id_or_404(current_user.user_id, tenant_context)
            
            user_info = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "real_name": user.real_name,
                "nickname": user.nickname,
                "phone": user.phone,
                "department": user.department,
                "position": user.position,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
                "roles": [{"code": role, "name": role} for role in current_user.roles],
                "permissions": list(current_user.permissions),
                "language": user.language,
                "timezone": user.timezone,
                "theme": user.theme,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            }
            
            return StandardResponse(
                message="获取用户信息成功",
                data=user_info
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取用户信息失败"
            )
