"""
基础数据模型
提供通用的模型基类和混合类
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from ..config.database import Base
from ..config.settings import settings


def generate_uuid():
    """生成UUID"""
    return str(uuid.uuid4())


class TimestampMixin:
    """时间戳混合类"""
    
    created_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间"
    )


class TenantMixin:
    """租户混合类"""
    
    tenant_id = Column(
        String(50),
        nullable=False,
        default=settings.default_tenant_id,
        comment="租户ID"
    )


class SoftDeleteMixin:
    """软删除混合类"""
    
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否已删除"
    )
    
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="删除时间"
    )
    
    deleted_by = Column(
        String(50),
        nullable=True,
        comment="删除者ID"
    )


class AuditMixin:
    """审计混合类"""
    
    created_by = Column(
        String(50),
        nullable=True,
        comment="创建者ID"
    )
    
    updated_by = Column(
        String(50),
        nullable=True,
        comment="更新者ID"
    )


class VersionMixin:
    """版本控制混合类"""
    
    version = Column(
        Integer,
        default=1,
        nullable=False,
        comment="版本号"
    )


class StatusMixin:
    """状态混合类"""
    
    status = Column(
        String(20),
        default="active",
        nullable=False,
        comment="状态"
    )


class BaseModel(Base, TimestampMixin, TenantMixin, SoftDeleteMixin, AuditMixin):
    """基础模型类"""
    
    __abstract__ = True
    
    id = Column(
        String(50),
        primary_key=True,
        default=generate_uuid,
        comment="主键ID"
    )
    
    @declared_attr
    def __tablename__(cls):
        # 自动生成表名（类名的小写+复数形式）
        return cls.__name__.lower() + 's'
    
    def __init__(self, **kwargs):
        # 从kwargs中提取租户ID
        tenant_id = kwargs.pop('tenant_id', None)
        if tenant_id:
            self.tenant_id = tenant_id
        
        # 从kwargs中提取创建者ID
        created_by = kwargs.pop('created_by', None)
        if created_by:
            self.created_by = created_by
        
        super().__init__(**kwargs)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    def update_from_dict(self, data: dict, exclude: set = None):
        """从字典更新属性"""
        exclude = exclude or {'id', 'created_at', 'tenant_id'}
        
        for key, value in data.items():
            if key not in exclude and hasattr(self, key):
                setattr(self, key, value)
        
        # 更新时间戳
        self.updated_at = func.now()
    
    def soft_delete(self, deleted_by: str = None):
        """软删除"""
        self.is_deleted = True
        self.deleted_at = func.now()
        if deleted_by:
            self.deleted_by = deleted_by
    
    def restore(self):
        """恢复软删除"""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
    
    @classmethod
    def get_active_query(cls, query):
        """获取未删除记录的查询"""
        return query.filter(cls.is_deleted == False)
    
    @classmethod
    def get_tenant_query(cls, query, tenant_id: str):
        """获取租户记录的查询"""
        if settings.tenant_isolation:
            return query.filter(cls.tenant_id == tenant_id)
        return query
    
    @classmethod
    def get_tenant_active_query(cls, query, tenant_id: str):
        """获取租户未删除记录的查询"""
        query = cls.get_tenant_query(query, tenant_id)
        return cls.get_active_query(query)
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"


class NamedBaseModel(BaseModel):
    """带名称的基础模型"""
    
    __abstract__ = True
    
    name = Column(
        String(100),
        nullable=False,
        comment="名称"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="描述"
    )
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, name={self.name})>"


class ConfigurableBaseModel(NamedBaseModel, StatusMixin):
    """可配置的基础模型"""
    
    __abstract__ = True
    
    config = Column(
        Text,  # 存储JSON格式的配置
        nullable=True,
        comment="配置信息"
    )
    
    def get_config(self) -> dict:
        """获取配置"""
        if self.config:
            import json
            try:
                return json.loads(self.config)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    def set_config(self, config: dict):
        """设置配置"""
        import json
        self.config = json.dumps(config, ensure_ascii=False)
    
    def update_config(self, updates: dict):
        """更新配置"""
        current_config = self.get_config()
        current_config.update(updates)
        self.set_config(current_config)


class TreeMixin:
    """树形结构混合类"""
    
    parent_id = Column(
        String(50),
        nullable=True,
        comment="父级ID"
    )
    
    level = Column(
        Integer,
        default=0,
        nullable=False,
        comment="层级"
    )
    
    sort_order = Column(
        Integer,
        default=0,
        nullable=False,
        comment="排序"
    )


class FileUploadMixin:
    """文件上传混合类"""
    
    file_path = Column(
        String(500),
        nullable=True,
        comment="文件路径"
    )
    
    file_name = Column(
        String(255),
        nullable=True,
        comment="文件名"
    )
    
    file_size = Column(
        Integer,
        nullable=True,
        comment="文件大小"
    )
    
    file_type = Column(
        String(50),
        nullable=True,
        comment="文件类型"
    )


class LocationMixin:
    """位置信息混合类"""
    
    latitude = Column(
        String(20),
        nullable=True,
        comment="纬度"
    )
    
    longitude = Column(
        String(20),
        nullable=True,
        comment="经度"
    )
    
    address = Column(
        String(500),
        nullable=True,
        comment="详细地址"
    )
    
    building = Column(
        String(100),
        nullable=True,
        comment="楼宇"
    )
    
    floor = Column(
        String(10),
        nullable=True,
        comment="楼层"
    )
    
    room = Column(
        String(20),
        nullable=True,
        comment="房间号"
    )
