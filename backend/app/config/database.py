"""
数据库配置和连接管理
支持SQLite和其他数据库的连接配置
"""

import logging
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .settings import settings

logger = logging.getLogger(__name__)

# 数据库元数据
metadata = MetaData()

# 声明性基类
Base = declarative_base(metadata=metadata)

# 数据库引擎配置
engine_kwargs = {
    "echo": settings.database_echo,
    "future": True,
}

# 同步数据库引擎
if settings.database_url.startswith("sqlite"):
    # SQLite特殊配置
    engine_kwargs.update({
        "poolclass": StaticPool,
        "connect_args": {
            "check_same_thread": False,  # 允许多线程访问SQLite
            "timeout": 20,  # 连接超时
        },
    })

sync_engine = create_engine(settings.database_url, **engine_kwargs)

# 异步数据库引擎（如果需要）
if settings.database_url.startswith("sqlite"):
    # SQLite异步支持
    async_database_url = settings.database_url.replace("sqlite://", "sqlite+aiosqlite://")
    async_engine = create_async_engine(
        async_database_url,
        echo=settings.database_echo,
        future=True,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
else:
    # 其他数据库的异步支持
    async_engine = create_async_engine(settings.database_url, **engine_kwargs)

# 会话制造器
SessionLocal = sessionmaker(
    bind=sync_engine,
    class_=Session,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.sync_engine = sync_engine
        self.async_engine = async_engine
        self.metadata = metadata
    
    def create_all_tables(self):
        """创建所有数据表"""
        try:
            metadata.create_all(bind=self.sync_engine)
            logger.info("数据库表创建成功")
        except Exception as e:
            logger.error(f"数据库表创建失败: {e}")
            raise
    
    def drop_all_tables(self):
        """删除所有数据表"""
        try:
            metadata.drop_all(bind=self.sync_engine)
            logger.info("数据库表删除成功")
        except Exception as e:
            logger.error(f"数据库表删除失败: {e}")
            raise
    
    async def async_create_all_tables(self):
        """异步创建所有数据表"""
        try:
            async with self.async_engine.begin() as conn:
                await conn.run_sync(metadata.create_all)
            logger.info("数据库表异步创建成功")
        except Exception as e:
            logger.error(f"数据库表异步创建失败: {e}")
            raise
    
    def get_sync_session(self) -> Session:
        """获取同步数据库会话"""
        return SessionLocal()
    
    def get_async_session(self) -> AsyncSession:
        """获取异步数据库会话"""
        return AsyncSessionLocal()
    
    @asynccontextmanager
    async def get_async_session_context(self) -> AsyncGenerator[AsyncSession, None]:
        """获取异步数据库会话上下文管理器"""
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


# 全局数据库管理器实例
db_manager = DatabaseManager()


def get_db() -> Session:
    """
    FastAPI依赖注入：获取数据库会话
    使用方式：
    @app.get("/users/")
    def get_users(db: Session = Depends(get_db)):
        ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI依赖注入：获取异步数据库会话
    使用方式：
    @app.get("/users/")
    async def get_users(db: AsyncSession = Depends(get_async_db)):
        ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


class TenantDatabaseMixin:
    """
    租户数据库混合类
    为模型提供多租户支持
    """
    
    @classmethod
    def filter_by_tenant(cls, query, tenant_id: str):
        """根据租户ID过滤查询"""
        if hasattr(cls, 'tenant_id') and settings.tenant_isolation:
            return query.filter(cls.tenant_id == tenant_id)
        return query
    
    @classmethod
    def get_tenant_context(cls, tenant_id: str = None) -> dict:
        """获取租户上下文"""
        if tenant_id is None:
            tenant_id = settings.default_tenant_id
        
        return {
            "tenant_id": tenant_id,
            "isolation_enabled": settings.tenant_isolation,
        }


def init_database():
    """初始化数据库"""
    try:
        logger.info("开始初始化数据库...")
        
        # 创建数据库表
        db_manager.create_all_tables()
        
        # 创建默认数据（如果需要）
        with db_manager.get_sync_session() as db:
            # 这里可以添加默认数据的创建逻辑
            pass
        
        logger.info("数据库初始化完成")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise


async def async_init_database():
    """异步初始化数据库"""
    try:
        logger.info("开始异步初始化数据库...")
        
        # 异步创建数据库表
        await db_manager.async_create_all_tables()
        
        # 创建默认数据（如果需要）
        async with db_manager.get_async_session_context() as db:
            # 这里可以添加默认数据的创建逻辑
            pass
        
        logger.info("数据库异步初始化完成")
        
    except Exception as e:
        logger.error(f"数据库异步初始化失败: {e}")
        raise
