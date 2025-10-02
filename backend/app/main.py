"""
FastAPI应用主文件
整合所有组件，启动应用
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config.settings import settings
from .config.database import init_database
from .core.middleware import setup_middleware
from .core.exceptions import setup_exception_handlers
from .controllers.user_controller import UserController


# 配置日志
logging.basicConfig(
    level=logging.INFO if settings.environment == "production" else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("启动应用...")
    
    try:
        # 初始化数据库
        init_database()
        logger.info("数据库初始化完成")
        
        # 其他初始化逻辑
        logger.info("应用启动完成")
        
        yield
        
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        raise
    finally:
        # 关闭时执行
        logger.info("应用关闭")


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="通用安防楼宇对讲系统API",
    docs_url=settings.docs_url if not settings.environment == "production" else None,
    redoc_url=settings.redoc_url if not settings.environment == "production" else None,
    openapi_url=settings.openapi_url if not settings.environment == "production" else None,
    lifespan=lifespan
)

# 设置中间件
setup_middleware(app)

# 设置异常处理器
setup_exception_handlers(app)


# 健康检查端点
@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment
    }


# 根路径
@app.get("/", tags=["根路径"])
async def root():
    """根路径"""
    return {
        "message": f"欢迎使用{settings.app_name}",
        "version": settings.app_version,
        "docs_url": "/docs" if settings.docs_url else None,
        "api_prefix": settings.api_v1_prefix
    }


# API路由
from fastapi import APIRouter

api_v1 = APIRouter(prefix=settings.api_v1_prefix)

# 用户相关路由
user_controller = UserController()

# 基础CRUD路由
api_v1.post(
    "/users",
    response_model=user_controller.StandardResponse,
    tags=["用户管理"],
    summary="创建用户"
)(user_controller.create_user)

api_v1.get(
    "/users/{user_id}",
    response_model=user_controller.StandardResponse,
    tags=["用户管理"],
    summary="获取用户详情"
)(user_controller.get_item_by_id)

api_v1.get(
    "/users",
    response_model=user_controller.PaginatedResponse,
    tags=["用户管理"],
    summary="获取用户列表"
)(user_controller.get_item_list)

api_v1.put(
    "/users/{user_id}",
    response_model=user_controller.StandardResponse,
    tags=["用户管理"],
    summary="更新用户"
)(user_controller.update_user)

api_v1.delete(
    "/users/{user_id}",
    response_model=user_controller.StandardResponse,
    tags=["用户管理"],
    summary="删除用户"
)(user_controller.delete_item)

# 用户特殊操作路由
api_v1.put(
    "/users/{user_id}/password",
    response_model=user_controller.StandardResponse,
    tags=["用户管理"],
    summary="修改密码"
)(user_controller.change_password)

api_v1.post(
    "/users/{user_id}/reset-password",
    response_model=user_controller.StandardResponse,
    tags=["用户管理"],
    summary="重置密码"
)(user_controller.reset_password)

api_v1.post(
    "/users/{user_id}/lock",
    response_model=user_controller.StandardResponse,
    tags=["用户管理"],
    summary="锁定用户"
)(user_controller.lock_user)

api_v1.post(
    "/users/{user_id}/unlock",
    response_model=user_controller.StandardResponse,
    tags=["用户管理"],
    summary="解锁用户"
)(user_controller.unlock_user)

api_v1.post(
    "/users/{user_id}/activate",
    response_model=user_controller.StandardResponse,
    tags=["用户管理"],
    summary="激活用户"
)(user_controller.activate_user)

api_v1.post(
    "/users/{user_id}/deactivate",
    response_model=user_controller.StandardResponse,
    tags=["用户管理"],
    summary="停用用户"
)(user_controller.deactivate_user)

# 角色权限相关路由
api_v1.get(
    "/users/{user_id}/roles",
    response_model=user_controller.StandardResponse,
    tags=["用户管理"],
    summary="获取用户角色"
)(user_controller.get_user_roles)

api_v1.post(
    "/users/{user_id}/roles",
    response_model=user_controller.StandardResponse,
    tags=["用户管理"],
    summary="分配用户角色"
)(user_controller.assign_roles)

api_v1.delete(
    "/users/{user_id}/roles/{role_id}",
    response_model=user_controller.StandardResponse,
    tags=["用户管理"],
    summary="移除用户角色"
)(user_controller.remove_role)

api_v1.get(
    "/users/{user_id}/permissions",
    response_model=user_controller.StandardResponse,
    tags=["用户管理"],
    summary="获取用户权限"
)(user_controller.get_user_permissions)

# 搜索和查询路由
api_v1.get(
    "/users/search",
    response_model=user_controller.StandardResponse,
    tags=["用户管理"],
    summary="搜索用户"
)(user_controller.search_users)

api_v1.get(
    "/users/by-role",
    response_model=user_controller.StandardResponse,
    tags=["用户管理"],
    summary="根据角色获取用户"
)(user_controller.get_users_by_role)

# 当前用户相关路由
api_v1.get(
    "/users/me/profile",
    response_model=user_controller.StandardResponse,
    tags=["个人中心"],
    summary="获取个人信息"
)(user_controller.get_current_user_info)

api_v1.put(
    "/users/me/profile",
    response_model=user_controller.StandardResponse,
    tags=["个人中心"],
    summary="更新个人信息"
)(user_controller.update_current_user_info)

api_v1.get(
    "/users/{user_id}/password-status",
    response_model=user_controller.StandardResponse,
    tags=["用户管理"],
    summary="检查密码过期状态"
)(user_controller.check_password_expiry)

# 统计信息路由
api_v1.get(
    "/users/statistics",
    response_model=user_controller.StandardResponse,
    tags=["用户管理"],
    summary="获取用户统计信息"
)(user_controller.get_statistics)

# 导出功能路由
api_v1.get(
    "/users/export/csv",
    tags=["用户管理"],
    summary="导出用户CSV"
)(user_controller.export_csv)

api_v1.get(
    "/users/export/excel",
    tags=["用户管理"],
    summary="导出用户Excel"
)(user_controller.export_excel)

# 认证相关路由
from .controllers.auth_controller import AuthController

auth_controller = AuthController()

api_v1.post(
    "/auth/login",
    tags=["认证"],
    summary="用户登录"
)(auth_controller.login)

api_v1.post(
    "/auth/logout",
    tags=["认证"],
    summary="用户登出"
)(auth_controller.logout)

api_v1.post(
    "/auth/refresh",
    tags=["认证"],
    summary="刷新令牌"
)(auth_controller.refresh_token)

# 将API路由添加到主应用
app.include_router(api_v1)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "内部服务器错误",
                "error_code": "INTERNAL_SERVER_ERROR",
                "status_code": 500,
            },
            "request_id": getattr(request.state, "request_id", None)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )
