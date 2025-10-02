"""
用户DAO层
提供用户相关的数据访问操作
"""

from typing import Optional, List, Dict, Any
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session, joinedload

from .base_dao import BaseDAO
from ..models.user import User, Role, Permission, UserRole, RolePermission, UserSession
from ..core.exceptions import NotFoundError, ValidationError


class UserDAO(BaseDAO[User]):
    """用户DAO"""
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_username(self, username: str, tenant_id: str = None, db: Session = None) -> Optional[User]:
        """根据用户名获取用户"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            query = self._get_base_query(_db, tenant_id)
            result = query.filter(User.username == username).first()
            return result
        finally:
            if close_session:
                _db.close()
    
    def get_by_email(self, email: str, tenant_id: str = None, db: Session = None) -> Optional[User]:
        """根据邮箱获取用户"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            query = self._get_base_query(_db, tenant_id)
            result = query.filter(User.email == email).first()
            return result
        finally:
            if close_session:
                _db.close()
    
    def get_with_roles(self, user_id: str, tenant_id: str = None, db: Session = None) -> Optional[User]:
        """获取用户及其角色信息"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            query = self._get_base_query(_db, tenant_id)
            result = query.options(
                joinedload(User.roles).joinedload(UserRole.role)
            ).filter(User.id == user_id).first()
            return result
        finally:
            if close_session:
                _db.close()
    
    def get_user_permissions(self, user_id: str, tenant_id: str = None, db: Session = None) -> List[str]:
        """获取用户权限列表"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            # 通过用户角色获取权限
            permissions = _db.query(Permission.code).distinct().join(
                RolePermission, Permission.id == RolePermission.permission_id
            ).join(
                Role, RolePermission.role_id == Role.id
            ).join(
                UserRole, Role.id == UserRole.role_id
            ).filter(
                and_(
                    UserRole.user_id == user_id,
                    Role.is_active == True,
                    Permission.is_active == True,
                    *([Role.tenant_id == tenant_id] if tenant_id else [])
                )
            ).all()
            
            return [perm.code for perm in permissions]
        finally:
            if close_session:
                _db.close()
    
    def get_users_by_role(self, role_code: str, tenant_id: str = None, db: Session = None) -> List[User]:
        """根据角色获取用户列表"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            query = self._get_base_query(_db, tenant_id)
            results = query.join(UserRole).join(Role).filter(
                Role.code == role_code
            ).all()
            return results
        finally:
            if close_session:
                _db.close()
    
    def search_users(
        self,
        keyword: str,
        tenant_id: str = None,
        include_inactive: bool = False,
        db: Session = None
    ) -> List[User]:
        """搜索用户"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            query = self._get_base_query(_db, tenant_id)
            
            # 添加搜索条件
            search_conditions = [
                User.username.like(f"%{keyword}%"),
                User.real_name.like(f"%{keyword}%"),
                User.email.like(f"%{keyword}%"),
                User.phone.like(f"%{keyword}%"),
            ]
            
            query = query.filter(or_(*search_conditions))
            
            # 是否包含非活跃用户
            if not include_inactive:
                query = query.filter(User.is_active == True)
            
            results = query.all()
            return results
        finally:
            if close_session:
                _db.close()
    
    def update_last_login(self, user_id: str, db: Session = None) -> bool:
        """更新最后登录时间"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            _db.query(User).filter(User.id == user_id).update({
                'last_login': func.now(),
                'login_count': User.login_count + 1,
                'failed_login_count': 0  # 重置失败次数
            })
            _db.commit()
            return True
        finally:
            if close_session:
                _db.close()
    
    def increment_failed_login(self, user_id: str, db: Session = None) -> int:
        """增加失败登录次数"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            user = _db.query(User).filter(User.id == user_id).first()
            if user:
                user.failed_login_count = (user.failed_login_count or 0) + 1
                _db.commit()
                return user.failed_login_count
            return 0
        finally:
            if close_session:
                _db.close()
    
    def lock_user(self, user_id: str, locked_until: Any, db: Session = None) -> bool:
        """锁定用户"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            _db.query(User).filter(User.id == user_id).update({
                'locked_until': locked_until
            })
            _db.commit()
            return True
        finally:
            if close_session:
                _db.close()
    
    def unlock_user(self, user_id: str, db: Session = None) -> bool:
        """解锁用户"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            _db.query(User).filter(User.id == user_id).update({
                'locked_until': None,
                'failed_login_count': 0
            })
            _db.commit()
            return True
        finally:
            if close_session:
                _db.close()


class RoleDAO(BaseDAO[Role]):
    """角色DAO"""
    
    def __init__(self):
        super().__init__(Role)
    
    def get_by_code(self, code: str, tenant_id: str = None, db: Session = None) -> Optional[Role]:
        """根据角色代码获取角色"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            query = self._get_base_query(_db, tenant_id)
            result = query.filter(Role.code == code).first()
            return result
        finally:
            if close_session:
                _db.close()
    
    def get_with_permissions(self, role_id: str, tenant_id: str = None, db: Session = None) -> Optional[Role]:
        """获取角色及其权限信息"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            query = self._get_base_query(_db, tenant_id)
            result = query.options(
                joinedload(Role.permissions).joinedload(RolePermission.permission)
            ).filter(Role.id == role_id).first()
            return result
        finally:
            if close_session:
                _db.close()
    
    def get_role_permissions(self, role_id: str, tenant_id: str = None, db: Session = None) -> List[str]:
        """获取角色权限列表"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            permissions = _db.query(Permission.code).join(
                RolePermission, Permission.id == RolePermission.permission_id
            ).filter(
                and_(
                    RolePermission.role_id == role_id,
                    Permission.is_active == True,
                    *([Permission.tenant_id == tenant_id] if tenant_id else [])
                )
            ).all()
            
            return [perm.code for perm in permissions]
        finally:
            if close_session:
                _db.close()
    
    def assign_permissions(self, role_id: str, permission_ids: List[str], tenant_id: str = None, created_by: str = None, db: Session = None) -> bool:
        """为角色分配权限"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            # 删除现有权限
            _db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
            
            # 添加新权限
            for permission_id in permission_ids:
                role_permission = RolePermission(
                    role_id=role_id,
                    permission_id=permission_id,
                    tenant_id=tenant_id,
                    created_by=created_by
                )
                _db.add(role_permission)
            
            _db.commit()
            return True
        finally:
            if close_session:
                _db.close()


class UserRoleDAO(BaseDAO[UserRole]):
    """用户角色关联DAO"""
    
    def __init__(self):
        super().__init__(UserRole)
    
    def assign_role(self, user_id: str, role_id: str, tenant_id: str = None, created_by: str = None, db: Session = None) -> UserRole:
        """为用户分配角色"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            # 检查是否已存在
            existing = _db.query(UserRole).filter(
                and_(
                    UserRole.user_id == user_id,
                    UserRole.role_id == role_id
                )
            ).first()
            
            if existing:
                return existing
            
            # 创建新关联
            user_role = UserRole(
                user_id=user_id,
                role_id=role_id,
                tenant_id=tenant_id,
                created_by=created_by
            )
            
            _db.add(user_role)
            _db.commit()
            _db.refresh(user_role)
            
            return user_role
        finally:
            if close_session:
                _db.close()
    
    def remove_role(self, user_id: str, role_id: str, db: Session = None) -> bool:
        """移除用户角色"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            deleted_count = _db.query(UserRole).filter(
                and_(
                    UserRole.user_id == user_id,
                    UserRole.role_id == role_id
                )
            ).delete()
            
            _db.commit()
            return deleted_count > 0
        finally:
            if close_session:
                _db.close()
    
    def get_user_roles(self, user_id: str, tenant_id: str = None, db: Session = None) -> List[UserRole]:
        """获取用户所有角色"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            query = self._get_base_query(_db, tenant_id)
            results = query.options(joinedload(UserRole.role)).filter(
                UserRole.user_id == user_id
            ).all()
            return results
        finally:
            if close_session:
                _db.close()


class UserSessionDAO(BaseDAO[UserSession]):
    """用户会话DAO"""
    
    def __init__(self):
        super().__init__(UserSession)
    
    def get_by_token(self, session_token: str, db: Session = None) -> Optional[UserSession]:
        """根据会话令牌获取会话"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            result = _db.query(UserSession).filter(
                and_(
                    UserSession.session_token == session_token,
                    UserSession.is_active == True
                )
            ).first()
            return result
        finally:
            if close_session:
                _db.close()
    
    def get_active_sessions(self, user_id: str, db: Session = None) -> List[UserSession]:
        """获取用户的活跃会话"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            results = _db.query(UserSession).filter(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.is_active == True,
                    UserSession.expires_at > func.now()
                )
            ).all()
            return results
        finally:
            if close_session:
                _db.close()
    
    def deactivate_session(self, session_token: str, db: Session = None) -> bool:
        """停用会话"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            updated_count = _db.query(UserSession).filter(
                UserSession.session_token == session_token
            ).update({'is_active': False})
            
            _db.commit()
            return updated_count > 0
        finally:
            if close_session:
                _db.close()
    
    def deactivate_user_sessions(self, user_id: str, exclude_token: str = None, db: Session = None) -> int:
        """停用用户的所有会话（可排除指定令牌）"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            query = _db.query(UserSession).filter(UserSession.user_id == user_id)
            
            if exclude_token:
                query = query.filter(UserSession.session_token != exclude_token)
            
            updated_count = query.update({'is_active': False})
            _db.commit()
            
            return updated_count
        finally:
            if close_session:
                _db.close()
    
    def cleanup_expired_sessions(self, db: Session = None) -> int:
        """清理过期会话"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            updated_count = _db.query(UserSession).filter(
                UserSession.expires_at < func.now()
            ).update({'is_active': False})
            
            _db.commit()
            return updated_count
        finally:
            if close_session:
                _db.close()
