"""
用户服务层
提供用户相关的业务逻辑操作
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .base_service import BaseService
from ..dao.user_dao import UserDAO, RoleDAO, UserRoleDAO
from ..models.user import User, Role, UserRole
from ..core.dependencies import TenantContext
from ..core.security import security_manager
from ..core.exceptions import BusinessLogicError, ValidationError, AuthenticationError
from ..config.settings import settings


class UserService(BaseService[User, UserDAO]):
    """用户服务"""
    
    def __init__(self):
        super().__init__(UserDAO())
        self.role_dao = RoleDAO()
        self.user_role_dao = UserRoleDAO()
    
    def _validate_create_data(self, data: Dict[str, Any], tenant_context: TenantContext = None) -> None:
        """验证创建用户数据"""
        # 验证必需字段
        self.validate_required_fields(data, ['username', 'email', 'password'])
        
        # 验证字段长度
        self.validate_field_length(data, {
            'username': 50,
            'email': 255,
            'real_name': 100,
            'phone': 20,
        })
        
        # 验证字段格式
        self.validate_field_format(data, {
            'username': r'^[a-zA-Z0-9_]{3,50}$',
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'phone': r'^1[3-9]\d{9}$' if data.get('phone') else r'.*',
        })
        
        # 验证唯一性
        self.validate_unique_field('username', data['username'], tenant_context)
        self.validate_unique_field('email', data['email'], tenant_context)
        
        if data.get('phone'):
            self.validate_unique_field('phone', data['phone'], tenant_context)
        
        # 验证密码强度
        self._validate_password_strength(data['password'], tenant_context)
        
        # 验证租户配额
        if tenant_context:
            self.validate_tenant_quota(tenant_context, 'users')
    
    def _validate_update_data(self, data: Dict[str, Any], obj: User = None, tenant_context: TenantContext = None) -> None:
        """验证更新用户数据"""
        # 验证字段长度
        self.validate_field_length(data, {
            'email': 255,
            'real_name': 100,
            'phone': 20,
        })
        
        # 验证字段格式
        if 'email' in data:
            self.validate_field_format(data, {
                'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            })
            # 验证邮箱唯一性（排除当前用户）
            self.validate_unique_field('email', data['email'], tenant_context, obj.id if obj else None)
        
        if 'phone' in data and data['phone']:
            self.validate_field_format(data, {
                'phone': r'^1[3-9]\d{9}$',
            })
            # 验证手机号唯一性（排除当前用户）
            self.validate_unique_field('phone', data['phone'], tenant_context, obj.id if obj else None)
        
        # 如果更新密码，验证密码强度
        if 'password' in data:
            self._validate_password_strength(data['password'], tenant_context)
    
    def _validate_password_strength(self, password: str, tenant_context: TenantContext = None) -> None:
        """验证密码强度"""
        if not password or len(password) < 8:
            raise ValidationError("密码长度不能少于8个字符")
        
        # 获取租户密码策略
        password_policy = {}
        if tenant_context and tenant_context.security:
            password_policy = tenant_context.security.password_policy
        
        # 默认密码策略
        min_length = password_policy.get('min_length', 8)
        require_uppercase = password_policy.get('require_uppercase', True)
        require_lowercase = password_policy.get('require_lowercase', True)
        require_numbers = password_policy.get('require_numbers', True)
        require_special_chars = password_policy.get('require_special_chars', False)
        
        if len(password) < min_length:
            raise ValidationError(f"密码长度不能少于{min_length}个字符")
        
        if require_uppercase and not re.search(r'[A-Z]', password):
            raise ValidationError("密码必须包含大写字母")
        
        if require_lowercase and not re.search(r'[a-z]', password):
            raise ValidationError("密码必须包含小写字母")
        
        if require_numbers and not re.search(r'\d', password):
            raise ValidationError("密码必须包含数字")
        
        if require_special_chars and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("密码必须包含特殊字符")
    
    def _pre_create(self, data: Dict[str, Any], tenant_context: TenantContext = None) -> Dict[str, Any]:
        """创建用户前处理"""
        data = super()._pre_create(data, tenant_context)
        
        # 处理密码加密
        if 'password' in data:
            data['password_hash'] = security_manager.create_password_hash(data['password'])
            data['password_changed_at'] = datetime.utcnow()
            del data['password']  # 删除明文密码
        
        # 设置默认值
        if 'is_active' not in data:
            data['is_active'] = True
        
        if 'language' not in data:
            data['language'] = 'zh-CN'
        
        if 'timezone' not in data:
            data['timezone'] = 'Asia/Shanghai'
        
        return data
    
    def _post_create(self, obj: User, tenant_context: TenantContext = None) -> User:
        """创建用户后处理"""
        # 分配默认角色
        default_role = self.role_dao.get_by_code('user', tenant_context.tenant_id if tenant_context else None)
        if default_role:
            self.assign_role(obj.id, default_role.id, tenant_context, obj.created_by)
        
        return obj
    
    def create_user(
        self,
        data: Dict[str, Any],
        tenant_context: TenantContext = None,
        created_by: str = None
    ) -> User:
        """创建用户"""
        return self.create(data, tenant_context, created_by)
    
    def authenticate_user(self, username: str, password: str, tenant_context: TenantContext = None) -> Optional[User]:
        """用户认证"""
        try:
            # 根据用户名或邮箱查找用户
            tenant_id = tenant_context.tenant_id if tenant_context else None
            user = self.dao.get_by_username(username, tenant_id)
            
            if not user:
                user = self.dao.get_by_email(username, tenant_id)
            
            if not user:
                raise AuthenticationError("用户名或密码错误")
            
            # 检查用户状态
            if not user.can_login():
                if user.is_account_locked():
                    raise AuthenticationError("账户已被锁定")
                elif not user.is_active:
                    raise AuthenticationError("账户未激活")
                else:
                    raise AuthenticationError("账户已被禁用")
            
            # 验证密码
            if not security_manager.verify_password(password, user.password_hash):
                # 增加失败登录次数
                failed_count = self.dao.increment_failed_login(user.id)
                
                # 检查是否需要锁定账户
                max_attempts = 5
                if tenant_context and tenant_context.security:
                    max_attempts = tenant_context.security.max_login_attempts
                
                if failed_count >= max_attempts:
                    # 锁定账户
                    lockout_duration = 15  # 15分钟
                    if tenant_context and tenant_context.security:
                        lockout_duration = tenant_context.security.lockout_duration // 60
                    
                    locked_until = datetime.utcnow() + timedelta(minutes=lockout_duration)
                    self.dao.lock_user(user.id, locked_until)
                    
                    raise AuthenticationError(f"密码错误次数过多，账户已被锁定{lockout_duration}分钟")
                
                raise AuthenticationError("用户名或密码错误")
            
            # 更新最后登录时间
            self.dao.update_last_login(user.id)
            
            return user
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"用户认证失败: {e}")
            raise AuthenticationError("认证过程发生错误")
    
    def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str,
        tenant_context: TenantContext = None
    ) -> bool:
        """修改密码"""
        user = self.get_by_id_or_404(user_id, tenant_context)
        
        # 验证旧密码
        if not security_manager.verify_password(old_password, user.password_hash):
            raise ValidationError("原密码错误")
        
        # 验证新密码强度
        self._validate_password_strength(new_password, tenant_context)
        
        # 更新密码
        password_hash = security_manager.create_password_hash(new_password)
        update_data = {
            'password_hash': password_hash,
            'password_changed_at': datetime.utcnow(),
            'failed_login_count': 0,  # 重置失败次数
            'locked_until': None  # 解锁账户
        }
        
        self.dao.update(user, update_data)
        return True
    
    def reset_password(
        self,
        user_id: str,
        new_password: str,
        tenant_context: TenantContext = None,
        reset_by: str = None
    ) -> bool:
        """重置密码（管理员操作）"""
        user = self.get_by_id_or_404(user_id, tenant_context)
        
        # 验证新密码强度
        self._validate_password_strength(new_password, tenant_context)
        
        # 更新密码
        password_hash = security_manager.create_password_hash(new_password)
        update_data = {
            'password_hash': password_hash,
            'password_changed_at': datetime.utcnow(),
            'failed_login_count': 0,  # 重置失败次数
            'locked_until': None,  # 解锁账户
            'updated_by': reset_by
        }
        
        self.dao.update(user, update_data)
        return True
    
    def lock_user(self, user_id: str, tenant_context: TenantContext = None, locked_by: str = None) -> bool:
        """锁定用户"""
        user = self.get_by_id_or_404(user_id, tenant_context)
        
        if user.is_superuser:
            raise BusinessLogicError("不能锁定超级用户")
        
        # 锁定24小时
        locked_until = datetime.utcnow() + timedelta(hours=24)
        update_data = {
            'locked_until': locked_until,
            'updated_by': locked_by
        }
        
        self.dao.update(user, update_data)
        return True
    
    def unlock_user(self, user_id: str, tenant_context: TenantContext = None, unlocked_by: str = None) -> bool:
        """解锁用户"""
        user = self.get_by_id_or_404(user_id, tenant_context)
        
        update_data = {
            'locked_until': None,
            'failed_login_count': 0,
            'updated_by': unlocked_by
        }
        
        self.dao.update(user, update_data)
        return True
    
    def activate_user(self, user_id: str, tenant_context: TenantContext = None, activated_by: str = None) -> bool:
        """激活用户"""
        update_data = {
            'is_active': True,
            'updated_by': activated_by
        }
        
        self.update(user_id, update_data, tenant_context, activated_by)
        return True
    
    def deactivate_user(self, user_id: str, tenant_context: TenantContext = None, deactivated_by: str = None) -> bool:
        """停用用户"""
        user = self.get_by_id_or_404(user_id, tenant_context)
        
        if user.is_superuser:
            raise BusinessLogicError("不能停用超级用户")
        
        update_data = {
            'is_active': False,
            'updated_by': deactivated_by
        }
        
        self.update(user_id, update_data, tenant_context, deactivated_by)
        return True
    
    def assign_role(
        self,
        user_id: str,
        role_id: str,
        tenant_context: TenantContext = None,
        assigned_by: str = None
    ) -> bool:
        """为用户分配角色"""
        # 检查用户和角色是否存在
        user = self.get_by_id_or_404(user_id, tenant_context)
        role = self.role_dao.get_by_id_or_404(role_id, tenant_context.tenant_id if tenant_context else None)
        
        # 分配角色
        self.user_role_dao.assign_role(
            user_id,
            role_id,
            tenant_context.tenant_id if tenant_context else None,
            assigned_by
        )
        
        return True
    
    def remove_role(
        self,
        user_id: str,
        role_id: str,
        tenant_context: TenantContext = None
    ) -> bool:
        """移除用户角色"""
        user = self.get_by_id_or_404(user_id, tenant_context)
        
        # 检查是否为超级用户的最后一个角色
        if user.is_superuser:
            user_roles = self.user_role_dao.get_user_roles(user_id, tenant_context.tenant_id if tenant_context else None)
            if len(user_roles) <= 1:
                raise BusinessLogicError("不能移除超级用户的最后一个角色")
        
        return self.user_role_dao.remove_role(user_id, role_id)
    
    def get_user_roles(self, user_id: str, tenant_context: TenantContext = None) -> List[Role]:
        """获取用户角色列表"""
        user_roles = self.user_role_dao.get_user_roles(user_id, tenant_context.tenant_id if tenant_context else None)
        return [ur.role for ur in user_roles]
    
    def get_user_permissions(self, user_id: str, tenant_context: TenantContext = None) -> List[str]:
        """获取用户权限列表"""
        return self.dao.get_user_permissions(user_id, tenant_context.tenant_id if tenant_context else None)
    
    def search_users(
        self,
        keyword: str,
        tenant_context: TenantContext = None,
        include_inactive: bool = False
    ) -> List[User]:
        """搜索用户"""
        return self.dao.search_users(
            keyword,
            tenant_context.tenant_id if tenant_context else None,
            include_inactive
        )
    
    def get_users_by_role(self, role_code: str, tenant_context: TenantContext = None) -> List[User]:
        """根据角色获取用户列表"""
        return self.dao.get_users_by_role(role_code, tenant_context.tenant_id if tenant_context else None)
    
    def check_password_expiry(self, user: User, tenant_context: TenantContext = None) -> Dict[str, Any]:
        """检查密码是否过期"""
        if not user.password_changed_at:
            return {"expired": False, "days_until_expiry": None}
        
        # 获取密码有效期
        max_age_days = 90  # 默认90天
        if tenant_context and tenant_context.security:
            max_age_days = tenant_context.security.password_policy.get('max_age_days', 90)
        
        if max_age_days <= 0:  # 0表示永不过期
            return {"expired": False, "days_until_expiry": None}
        
        # 计算过期时间
        expiry_date = user.password_changed_at + timedelta(days=max_age_days)
        now = datetime.utcnow()
        
        if now >= expiry_date:
            return {"expired": True, "days_until_expiry": 0}
        
        days_until_expiry = (expiry_date - now).days
        return {"expired": False, "days_until_expiry": days_until_expiry}
    
    def cleanup_inactive_users(self, tenant_context: TenantContext = None, days: int = 90) -> int:
        """清理非活跃用户"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # 获取长时间未登录的非活跃用户
        filters = {
            'is_active': False,
            'last_login': {'operator': 'lt', 'value': cutoff_date}
        }
        
        inactive_users = self.dao.get_list(
            tenant_id=tenant_context.tenant_id if tenant_context else None,
            filters=filters
        )
        
        # 软删除这些用户
        count = 0
        for user in inactive_users:
            if not user.is_superuser and not user.is_staff:  # 保护超级用户和员工
                self.dao.delete(user, soft_delete=True, deleted_by='system')
                count += 1
        
        return count
