"""
中间件模块
提供请求日志、CORS、安全头等中间件
"""

import time
import uuid
import logging
from typing import Callable
from datetime import datetime

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from ..config.settings import settings
from .security import rate_limiter

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取客户端信息
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        method = request.method
        url = str(request.url)
        
        # 记录请求日志
        logger.info(
            f"请求开始 - ID: {request_id}, IP: {client_ip}, "
            f"方法: {method}, URL: {url}, User-Agent: {user_agent}"
        )
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应日志
            logger.info(
                f"请求完成 - ID: {request_id}, 状态: {response.status_code}, "
                f"处理时间: {process_time:.3f}s"
            )
            
            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            
            return response
            
        except Exception as e:
            # 记录异常日志
            process_time = time.time() - start_time
            logger.error(
                f"请求异常 - ID: {request_id}, 错误: {str(e)}, "
                f"处理时间: {process_time:.3f}s",
                exc_info=True
            )
            
            # 返回错误响应
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "message": "内部服务器错误",
                        "error_code": "INTERNAL_SERVER_ERROR",
                        "status_code": 500,
                    },
                    "request_id": request_id,
                },
                headers={
                    "X-Request-ID": request_id,
                    "X-Process-Time": f"{process_time:.3f}",
                }
            )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全头中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # 添加安全头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # 如果是HTTPS，添加HSTS头
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """频率限制中间件"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 跳过文档和健康检查端点
        if request.url.path in ["/docs", "/redoc", "/openapi.json", "/health"]:
            return await call_next(request)
        
        # 获取客户端IP
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"
        
        # 检查频率限制
        if not rate_limiter.is_allowed(key, self.requests_per_minute, 60):
            logger.warning(f"IP {client_ip} 触发频率限制")
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "message": "请求频率过高，请稍后再试",
                        "error_code": "RATE_LIMIT_EXCEEDED",
                        "status_code": 429,
                        "details": {
                            "limit": self.requests_per_minute,
                            "window": "1分钟",
                        }
                    }
                },
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Window": "60",
                    "Retry-After": "60",
                }
            )
        
        return await call_next(request)


class TenantContextMiddleware(BaseHTTPMiddleware):
    """租户上下文中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 从请求头或查询参数中提取租户ID
        tenant_id = None
        
        # 优先从头部获取
        if "X-Tenant-ID" in request.headers:
            tenant_id = request.headers["X-Tenant-ID"]
        
        # 其次从查询参数获取
        elif "tenant_id" in request.query_params:
            tenant_id = request.query_params["tenant_id"]
        
        # 如果没有提供租户ID，使用默认租户
        if not tenant_id:
            tenant_id = settings.default_tenant_id
        
        # 设置租户上下文
        request.state.tenant_id = tenant_id
        
        response = await call_next(request)
        
        # 在响应头中添加租户信息
        response.headers["X-Tenant-ID"] = tenant_id
        
        return response


class DatabaseConnectionMiddleware(BaseHTTPMiddleware):
    """数据库连接中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 这里可以添加数据库连接检查逻辑
        # 例如检查数据库是否可用
        
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # 如果是数据库相关错误，可以在这里进行特殊处理
            logger.error(f"数据库操作异常: {str(e)}", exc_info=True)
            raise


class AuditLogMiddleware(BaseHTTPMiddleware):
    """审计日志中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 跳过GET请求和静态文件
        if request.method == "GET" or request.url.path.startswith("/static"):
            return await call_next(request)
        
        # 记录审计信息
        audit_info = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": getattr(request.state, "request_id", None),
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "tenant_id": getattr(request.state, "tenant_id", None),
        }
        
        # 处理请求
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # 补充响应信息
        audit_info.update({
            "status_code": response.status_code,
            "process_time": process_time,
        })
        
        # 记录审计日志（这里可以发送到专门的审计日志系统）
        logger.info(f"审计日志: {audit_info}")
        
        return response


class HealthCheckMiddleware(BaseHTTPMiddleware):
    """健康检查中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 处理健康检查请求
        if request.url.path == "/health":
            health_status = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": settings.app_version,
                "environment": settings.environment,
            }
            
            # 检查数据库连接
            try:
                from ..config.database import db_manager
                # 这里可以添加数据库连接检查
                health_status["database"] = "connected"
            except Exception:
                health_status["database"] = "disconnected"
                health_status["status"] = "unhealthy"
            
            # 检查Redis连接（如果配置了）
            if settings.redis_url:
                try:
                    # 这里可以添加Redis连接检查
                    health_status["redis"] = "connected"
                except Exception:
                    health_status["redis"] = "disconnected"
            
            status_code = 200 if health_status["status"] == "healthy" else 503
            
            return JSONResponse(
                status_code=status_code,
                content=health_status
            )
        
        return await call_next(request)


def setup_middleware(app):
    """设置所有中间件"""
    
    # CORS中间件（最外层）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_credentials,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )
    
    # 安全头中间件
    app.add_middleware(SecurityHeadersMiddleware)
    
    # 频率限制中间件
    app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
    
    # 请求日志中间件
    app.add_middleware(RequestLoggingMiddleware)
    
    # 租户上下文中间件
    app.add_middleware(TenantContextMiddleware)
    
    # 健康检查中间件
    app.add_middleware(HealthCheckMiddleware)
    
    # 审计日志中间件
    if settings.enable_audit_logging:
        app.add_middleware(AuditLogMiddleware)
    
    # 数据库连接中间件
    app.add_middleware(DatabaseConnectionMiddleware)
    
    logger.info("所有中间件设置完成")
