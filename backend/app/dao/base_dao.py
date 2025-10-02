"""
基础DAO层
提供通用的数据访问操作
"""

import logging
from typing import Type, TypeVar, Generic, Optional, List, Dict, Any, Union
from sqlalchemy import and_, or_, desc, asc, func, text
from sqlalchemy.orm import Session, Query
from sqlalchemy.exc import SQLAlchemyError

from ..config.database import db_manager
from ..config.settings import settings
from ..models.base import BaseModel
from ..core.exceptions import DatabaseError, NotFoundError, ValidationError

logger = logging.getLogger(__name__)

# 泛型类型变量
T = TypeVar('T', bound=BaseModel)


class BaseDAO(Generic[T]):
    """基础DAO类"""
    
    def __init__(self, model: Type[T]):
        self.model = model
        self.db_manager = db_manager
    
    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.db_manager.get_sync_session()
    
    def _get_base_query(self, db: Session, tenant_id: str = None) -> Query:
        """获取基础查询对象"""
        query = db.query(self.model)
        
        # 添加租户过滤
        if tenant_id and hasattr(self.model, 'tenant_id') and settings.tenant_isolation:
            query = query.filter(self.model.tenant_id == tenant_id)
        
        # 添加软删除过滤
        if hasattr(self.model, 'is_deleted'):
            query = query.filter(self.model.is_deleted == False)
        
        return query
    
    def create(self, obj: T, db: Session = None) -> T:
        """创建记录"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            _db.add(obj)
            _db.commit()
            _db.refresh(obj)
            logger.info(f"创建{self.model.__name__}记录成功: {obj.id}")
            return obj
            
        except SQLAlchemyError as e:
            _db.rollback()
            logger.error(f"创建{self.model.__name__}记录失败: {e}")
            raise DatabaseError(f"创建记录失败", operation="create", details={"error": str(e)})
        
        finally:
            if close_session:
                _db.close()
    
    def get_by_id(self, id: str, tenant_id: str = None, db: Session = None) -> Optional[T]:
        """根据ID获取记录"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            query = self._get_base_query(_db, tenant_id)
            result = query.filter(self.model.id == id).first()
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"查询{self.model.__name__}记录失败: {e}")
            raise DatabaseError(f"查询记录失败", operation="get_by_id", details={"error": str(e)})
        
        finally:
            if close_session:
                _db.close()
    
    def get_by_id_or_404(self, id: str, tenant_id: str = None, db: Session = None) -> T:
        """根据ID获取记录，不存在则抛出404异常"""
        result = self.get_by_id(id, tenant_id, db)
        if result is None:
            raise NotFoundError(self.model.__name__, id)
        return result
    
    def get_all(self, tenant_id: str = None, db: Session = None) -> List[T]:
        """获取所有记录"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            query = self._get_base_query(_db, tenant_id)
            results = query.all()
            return results
            
        except SQLAlchemyError as e:
            logger.error(f"查询{self.model.__name__}列表失败: {e}")
            raise DatabaseError(f"查询列表失败", operation="get_all", details={"error": str(e)})
        
        finally:
            if close_session:
                _db.close()
    
    def get_list(
        self,
        tenant_id: str = None,
        filters: Dict[str, Any] = None,
        search: str = None,
        search_fields: List[str] = None,
        sort_by: str = None,
        sort_order: str = "asc",
        offset: int = 0,
        limit: int = None,
        db: Session = None
    ) -> List[T]:
        """获取记录列表（支持过滤、搜索、排序、分页）"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            query = self._get_base_query(_db, tenant_id)
            
            # 添加过滤条件
            if filters:
                query = self._apply_filters(query, filters)
            
            # 添加搜索条件
            if search and search_fields:
                query = self._apply_search(query, search, search_fields)
            
            # 添加排序
            if sort_by:
                query = self._apply_sorting(query, sort_by, sort_order)
            
            # 添加分页
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            
            results = query.all()
            return results
            
        except SQLAlchemyError as e:
            logger.error(f"查询{self.model.__name__}列表失败: {e}")
            raise DatabaseError(f"查询列表失败", operation="get_list", details={"error": str(e)})
        
        finally:
            if close_session:
                _db.close()
    
    def count(
        self,
        tenant_id: str = None,
        filters: Dict[str, Any] = None,
        search: str = None,
        search_fields: List[str] = None,
        db: Session = None
    ) -> int:
        """计算记录数量"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            query = self._get_base_query(_db, tenant_id)
            
            # 添加过滤条件
            if filters:
                query = self._apply_filters(query, filters)
            
            # 添加搜索条件
            if search and search_fields:
                query = self._apply_search(query, search, search_fields)
            
            count = query.count()
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"统计{self.model.__name__}数量失败: {e}")
            raise DatabaseError(f"统计数量失败", operation="count", details={"error": str(e)})
        
        finally:
            if close_session:
                _db.close()
    
    def update(self, obj: T, data: Dict[str, Any], db: Session = None) -> T:
        """更新记录"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            # 更新字段
            obj.update_from_dict(data)
            
            _db.commit()
            _db.refresh(obj)
            logger.info(f"更新{self.model.__name__}记录成功: {obj.id}")
            return obj
            
        except SQLAlchemyError as e:
            _db.rollback()
            logger.error(f"更新{self.model.__name__}记录失败: {e}")
            raise DatabaseError(f"更新记录失败", operation="update", details={"error": str(e)})
        
        finally:
            if close_session:
                _db.close()
    
    def update_by_id(self, id: str, data: Dict[str, Any], tenant_id: str = None, db: Session = None) -> T:
        """根据ID更新记录"""
        obj = self.get_by_id_or_404(id, tenant_id, db)
        return self.update(obj, data, db)
    
    def delete(self, obj: T, soft_delete: bool = True, deleted_by: str = None, db: Session = None) -> bool:
        """删除记录"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            if soft_delete and hasattr(obj, 'soft_delete'):
                # 软删除
                obj.soft_delete(deleted_by)
            else:
                # 硬删除
                _db.delete(obj)
            
            _db.commit()
            logger.info(f"删除{self.model.__name__}记录成功: {obj.id}")
            return True
            
        except SQLAlchemyError as e:
            _db.rollback()
            logger.error(f"删除{self.model.__name__}记录失败: {e}")
            raise DatabaseError(f"删除记录失败", operation="delete", details={"error": str(e)})
        
        finally:
            if close_session:
                _db.close()
    
    def delete_by_id(self, id: str, tenant_id: str = None, soft_delete: bool = True, deleted_by: str = None, db: Session = None) -> bool:
        """根据ID删除记录"""
        obj = self.get_by_id_or_404(id, tenant_id, db)
        return self.delete(obj, soft_delete, deleted_by, db)
    
    def bulk_create(self, objects: List[T], db: Session = None) -> List[T]:
        """批量创建记录"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            _db.add_all(objects)
            _db.commit()
            
            # 刷新对象以获取ID
            for obj in objects:
                _db.refresh(obj)
            
            logger.info(f"批量创建{self.model.__name__}记录成功: {len(objects)}条")
            return objects
            
        except SQLAlchemyError as e:
            _db.rollback()
            logger.error(f"批量创建{self.model.__name__}记录失败: {e}")
            raise DatabaseError(f"批量创建记录失败", operation="bulk_create", details={"error": str(e)})
        
        finally:
            if close_session:
                _db.close()
    
    def bulk_update(self, updates: List[Dict[str, Any]], db: Session = None) -> int:
        """批量更新记录"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            result = _db.bulk_update_mappings(self.model, updates)
            _db.commit()
            logger.info(f"批量更新{self.model.__name__}记录成功: {len(updates)}条")
            return len(updates)
            
        except SQLAlchemyError as e:
            _db.rollback()
            logger.error(f"批量更新{self.model.__name__}记录失败: {e}")
            raise DatabaseError(f"批量更新记录失败", operation="bulk_update", details={"error": str(e)})
        
        finally:
            if close_session:
                _db.close()
    
    def exists(self, id: str, tenant_id: str = None, db: Session = None) -> bool:
        """检查记录是否存在"""
        return self.get_by_id(id, tenant_id, db) is not None
    
    def exists_by_field(self, field: str, value: Any, tenant_id: str = None, exclude_id: str = None, db: Session = None) -> bool:
        """根据字段值检查记录是否存在"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            query = self._get_base_query(_db, tenant_id)
            
            # 添加字段过滤
            if hasattr(self.model, field):
                query = query.filter(getattr(self.model, field) == value)
            else:
                return False
            
            # 排除特定ID
            if exclude_id:
                query = query.filter(self.model.id != exclude_id)
            
            return query.first() is not None
            
        except SQLAlchemyError as e:
            logger.error(f"检查{self.model.__name__}记录存在性失败: {e}")
            raise DatabaseError(f"检查记录存在性失败", operation="exists_by_field", details={"error": str(e)})
        
        finally:
            if close_session:
                _db.close()
    
    def _apply_filters(self, query: Query, filters: Dict[str, Any]) -> Query:
        """应用过滤条件"""
        for field, value in filters.items():
            if not hasattr(self.model, field) or value is None:
                continue
            
            # 处理不同类型的过滤
            if isinstance(value, dict):
                # 复杂过滤条件
                operator = value.get('operator', 'eq')
                filter_value = value.get('value')
                
                if operator == 'eq':
                    query = query.filter(getattr(self.model, field) == filter_value)
                elif operator == 'ne':
                    query = query.filter(getattr(self.model, field) != filter_value)
                elif operator == 'gt':
                    query = query.filter(getattr(self.model, field) > filter_value)
                elif operator == 'gte':
                    query = query.filter(getattr(self.model, field) >= filter_value)
                elif operator == 'lt':
                    query = query.filter(getattr(self.model, field) < filter_value)
                elif operator == 'lte':
                    query = query.filter(getattr(self.model, field) <= filter_value)
                elif operator == 'like':
                    query = query.filter(getattr(self.model, field).like(f"%{filter_value}%"))
                elif operator == 'in':
                    if isinstance(filter_value, list):
                        query = query.filter(getattr(self.model, field).in_(filter_value))
                
            elif isinstance(value, list):
                # IN过滤
                query = query.filter(getattr(self.model, field).in_(value))
            else:
                # 等值过滤
                query = query.filter(getattr(self.model, field) == value)
        
        return query
    
    def _apply_search(self, query: Query, search: str, search_fields: List[str]) -> Query:
        """应用搜索条件"""
        if not search or not search_fields:
            return query
        
        search_conditions = []
        for field in search_fields:
            if hasattr(self.model, field):
                search_conditions.append(
                    getattr(self.model, field).like(f"%{search}%")
                )
        
        if search_conditions:
            query = query.filter(or_(*search_conditions))
        
        return query
    
    def _apply_sorting(self, query: Query, sort_by: str, sort_order: str = "asc") -> Query:
        """应用排序"""
        if not hasattr(self.model, sort_by):
            return query
        
        sort_field = getattr(self.model, sort_by)
        
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_field))
        else:
            query = query.order_by(asc(sort_field))
        
        return query
    
    def execute_raw_query(self, sql: str, params: Dict[str, Any] = None, db: Session = None) -> Any:
        """执行原始SQL查询"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            result = _db.execute(text(sql), params or {})
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"执行原始SQL查询失败: {e}")
            raise DatabaseError(f"执行查询失败", operation="raw_query", details={"error": str(e)})
        
        finally:
            if close_session:
                _db.close()
    
    def get_statistics(self, tenant_id: str = None, db: Session = None) -> Dict[str, Any]:
        """获取统计信息"""
        _db = db or self.get_session()
        close_session = db is None
        
        try:
            query = self._get_base_query(_db, tenant_id)
            
            stats = {
                "total_count": query.count(),
            }
            
            # 如果有状态字段，统计各状态数量
            if hasattr(self.model, 'status'):
                status_stats = _db.query(
                    self.model.status,
                    func.count(self.model.id).label('count')
                ).group_by(self.model.status).all()
                
                stats["by_status"] = {status: count for status, count in status_stats}
            
            # 如果有创建时间字段，统计最近创建情况
            if hasattr(self.model, 'created_at'):
                from datetime import datetime, timedelta
                
                now = datetime.utcnow()
                week_ago = now - timedelta(days=7)
                month_ago = now - timedelta(days=30)
                
                stats.update({
                    "created_last_week": query.filter(self.model.created_at >= week_ago).count(),
                    "created_last_month": query.filter(self.model.created_at >= month_ago).count(),
                })
            
            return stats
            
        except SQLAlchemyError as e:
            logger.error(f"获取{self.model.__name__}统计信息失败: {e}")
            raise DatabaseError(f"获取统计信息失败", operation="get_statistics", details={"error": str(e)})
        
        finally:
            if close_session:
                _db.close()
