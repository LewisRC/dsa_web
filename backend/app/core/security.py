"""
安全认证模块
提供JWT认证、密码加密、权限验证等功能
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..config.settings import settings
from ..config.tenant_config import get_tenant_config

logger = logging.getLogger(__name__)

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer认证
security = HTTPBearer()


class SecurityManager:
    """安全管理器"""
    
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        self.refresh_token_expire_days = settings.refresh_token_expire_days
    
    def create_password_hash(self, password: str) -> str:
        """创建密码哈希"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )
        
        to_encode.update({
            "exp": expire,
            "type": "access",
            "iat": datetime.utcnow(),
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """创建刷新令牌"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                days=self.refresh_token_expire_days
            )
        
        to_encode.update({
            "exp": expire,
            "type": "refresh",
            "iat": datetime.utcnow(),
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 检查令牌类型
            token_type = payload.get("type")
            if not token_type:
                return None
            
            # 检查过期时间
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                return None
            
            return payload
            
        except JWTError as e:
            logger.warning(f"JWT验证失败: {e}")
            return None
    
    def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证访问令牌"""
        payload = self.verify_token(token)
        if payload and payload.get("type") == "access":
            return payload
        return None
    
    def verify_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证刷新令牌"""
        payload = self.verify_token(token)
        if payload and payload.get("type") == "refresh":
            return payload
        return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """使用刷新令牌获取新的访问令牌"""
        payload = self.verify_refresh_token(refresh_token)
        if not payload:
            return None
        
        # 提取用户信息
        user_data = {
            "sub": payload.get("sub"),
            "tenant_id": payload.get("tenant_id"),
            "roles": payload.get("roles", []),
        }
        
        # 创建新的访问令牌
        return self.create_access_token(user_data)


# 全局安全管理器实例
security_manager = SecurityManager()


class CurrentUser:
    """当前用户信息"""
    
    def __init__(
        self,
        user_id: str,
        username: str,
        email: str,
        tenant_id: str,
        roles: list = None,
        permissions: list = None,
        is_active: bool = True,
        is_superuser: bool = False,
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.tenant_id = tenant_id
        self.roles = roles or []
        self.permissions = permissions or []
        self.is_active = is_active
        self.is_superuser = is_superuser
    
    def has_permission(self, permission: str) -> bool:
        """检查是否有指定权限"""
        return self.is_superuser or permission in self.permissions
    
    def has_role(self, role: str) -> bool:
        """检查是否有指定角色"""
        return self.is_superuser or role in self.roles
    
    def has_any_role(self, roles: list) -> bool:
        """检查是否有任意指定角色"""
        return self.is_superuser or any(role in self.roles for role in roles)
    
    def has_all_roles(self, roles: list) -> bool:
        """检查是否有所有指定角色"""
        return self.is_superuser or all(role in self.roles for role in roles)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = None,
) -> CurrentUser:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 验证访问令牌
        payload = security_manager.verify_access_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        # 提取用户信息
        user_id: str = payload.get("sub")
        tenant_id: str = payload.get("tenant_id")
        username: str = payload.get("username")
        email: str = payload.get("email")
        roles: list = payload.get("roles", [])
        permissions: list = payload.get("permissions", [])
        is_active: bool = payload.get("is_active", True)
        is_superuser: bool = payload.get("is_superuser", False)
        
        if user_id is None or tenant_id is None:
            raise credentials_exception
        
        # 检查用户是否活跃
        if not is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户账户已禁用",
            )
        
        # 检查租户配置
        tenant_config = get_tenant_config(tenant_id)
        if not tenant_config.active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="租户账户已禁用",
            )
        
        return CurrentUser(
            user_id=user_id,
            username=username,
            email=email,
            tenant_id=tenant_id,
            roles=roles,
            permissions=permissions,
            is_active=is_active,
            is_superuser=is_superuser,
        )
        
    except JWTError:
        raise credentials_exception


async def get_current_active_user(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="用户账户未激活"
        )
    return current_user


def require_permission(permission: str):
    """权限装饰器"""
    def permission_checker(current_user: CurrentUser = Depends(get_current_user)):
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"缺少所需权限: {permission}",
            )
        return current_user
    return permission_checker


def require_role(role: str):
    """角色装饰器"""
    def role_checker(current_user: CurrentUser = Depends(get_current_user)):
        if not current_user.has_role(role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"缺少所需角色: {role}",
            )
        return current_user
    return role_checker


def require_any_role(*roles: str):
    """任意角色装饰器"""
    def role_checker(current_user: CurrentUser = Depends(get_current_user)):
        if not current_user.has_any_role(list(roles)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"缺少所需角色之一: {', '.join(roles)}",
            )
        return current_user
    return role_checker


def require_superuser():
    """超级用户装饰器"""
    def superuser_checker(current_user: CurrentUser = Depends(get_current_user)):
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要超级用户权限",
            )
        return current_user
    return superuser_checker


class RateLimiter:
    """API频率限制器"""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """检查是否允许请求"""
        now = datetime.utcnow()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # 清理过期请求
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if (now - req_time).total_seconds() < window
        ]
        
        # 检查是否超过限制
        if len(self.requests[key]) >= limit:
            return False
        
        # 记录新请求
        self.requests[key].append(now)
        return True


# 全局频率限制器
rate_limiter = RateLimiter()


def create_rate_limit_dependency(requests_per_minute: int = 60):
    """创建频率限制依赖"""
    async def rate_limit_checker(request: Request):
        # 使用IP地址作为键
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"
        
        if not rate_limiter.is_allowed(key, requests_per_minute, 60):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="请求频率过高，请稍后再试",
            )
        
        return True
    
    return rate_limit_checker
