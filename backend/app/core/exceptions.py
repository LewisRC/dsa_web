"""
异常处理模块
定义自定义异常和全局异常处理器
"""

import logging
from typing import Any, Dict, Optional, Union
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class BaseCustomException(Exception):
    """基础自定义异常"""
    
    def __init__(
        self,
        message: str,
        error_code: str = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class BusinessLogicError(BaseCustomException):
    """业务逻辑错误"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "BUSINESS_LOGIC_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class ValidationError(BaseCustomException):
    """数据验证错误"""
    
    def __init__(
        self,
        message: str,
        field: str = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if field:
            error_details["field"] = field
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=error_details,
        )


class NotFoundError(BaseCustomException):
    """资源未找到错误"""
    
    def __init__(
        self,
        resource: str,
        identifier: str = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        message = f"{resource} 未找到"
        if identifier:
            message = f"{resource} ({identifier}) 未找到"
        
        error_details = details or {}
        error_details.update({
            "resource": resource,
            "identifier": identifier,
        })
        
        super().__init__(
            message=message,
            error_code="NOT_FOUND_ERROR",
            status_code=status.HTTP_404_NOT_FOUND,
            details=error_details,
        )


class AuthenticationError(BaseCustomException):
    """认证错误"""
    
    def __init__(
        self,
        message: str = "认证失败",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class AuthorizationError(BaseCustomException):
    """授权错误"""
    
    def __init__(
        self,
        message: str = "权限不足",
        required_permission: str = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if required_permission:
            error_details["required_permission"] = required_permission
        
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=status.HTTP_403_FORBIDDEN,
            details=error_details,
        )


class TenantError(BaseCustomException):
    """租户相关错误"""
    
    def __init__(
        self,
        message: str,
        tenant_id: str = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if tenant_id:
            error_details["tenant_id"] = tenant_id
        
        super().__init__(
            message=message,
            error_code="TENANT_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=error_details,
        )


class DeviceError(BaseCustomException):
    """设备相关错误"""
    
    def __init__(
        self,
        message: str,
        device_id: str = None,
        device_status: str = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if device_id:
            error_details["device_id"] = device_id
        if device_status:
            error_details["device_status"] = device_status
        
        super().__init__(
            message=message,
            error_code="DEVICE_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=error_details,
        )


class IntercomError(BaseCustomException):
    """对讲相关错误"""
    
    def __init__(
        self,
        message: str,
        session_id: str = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if session_id:
            error_details["session_id"] = session_id
        
        super().__init__(
            message=message,
            error_code="INTERCOM_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=error_details,
        )


class AlarmError(BaseCustomException):
    """报警相关错误"""
    
    def __init__(
        self,
        message: str,
        alarm_id: str = None,
        alarm_type: str = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if alarm_id:
            error_details["alarm_id"] = alarm_id
        if alarm_type:
            error_details["alarm_type"] = alarm_type
        
        super().__init__(
            message=message,
            error_code="ALARM_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=error_details,
        )


class DatabaseError(BaseCustomException):
    """数据库错误"""
    
    def __init__(
        self,
        message: str = "数据库操作失败",
        operation: str = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if operation:
            error_details["operation"] = operation
        
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details,
        )


class ExternalServiceError(BaseCustomException):
    """外部服务错误"""
    
    def __init__(
        self,
        message: str,
        service_name: str = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if service_name:
            error_details["service_name"] = service_name
        
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=error_details,
        )


class ConfigurationError(BaseCustomException):
    """配置错误"""
    
    def __init__(
        self,
        message: str,
        config_key: str = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if config_key:
            error_details["config_key"] = config_key
        
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details,
        )


def create_error_response(
    exception: Union[BaseCustomException, Exception],
    request: Request = None,
) -> Dict[str, Any]:
    """创建标准错误响应"""
    
    # 生成请求ID用于错误追踪
    request_id = None
    if request:
        request_id = getattr(request.state, "request_id", None)
    
    if isinstance(exception, BaseCustomException):
        error_response = {
            "error": {
                "message": exception.message,
                "error_code": exception.error_code,
                "status_code": exception.status_code,
                "details": exception.details,
            }
        }
    else:
        error_response = {
            "error": {
                "message": "内部服务器错误",
                "error_code": "INTERNAL_SERVER_ERROR",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "details": {},
            }
        }
    
    if request_id:
        error_response["request_id"] = request_id
    
    return error_response


async def custom_exception_handler(request: Request, exc: BaseCustomException):
    """自定义异常处理器"""
    logger.error(f"自定义异常: {exc.error_code} - {exc.message}", exc_info=True)
    
    error_response = create_error_response(exc, request)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response,
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP异常处理器"""
    logger.warning(f"HTTP异常: {exc.status_code} - {exc.detail}")
    
    error_response = {
        "error": {
            "message": exc.detail,
            "error_code": "HTTP_EXCEPTION",
            "status_code": exc.status_code,
            "details": {},
        }
    }
    
    request_id = getattr(request.state, "request_id", None)
    if request_id:
        error_response["request_id"] = request_id
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理器"""
    logger.warning(f"请求验证异常: {exc.errors()}")
    
    # 格式化验证错误
    validation_errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"][1:])  # 跳过 'body'
        validation_errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"],
        })
    
    error_response = {
        "error": {
            "message": "请求数据验证失败",
            "error_code": "REQUEST_VALIDATION_ERROR",
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "details": {
                "validation_errors": validation_errors,
            },
        }
    }
    
    request_id = getattr(request.state, "request_id", None)
    if request_id:
        error_response["request_id"] = request_id
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response,
    )


async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    logger.error(f"未处理的异常: {type(exc).__name__} - {str(exc)}", exc_info=True)
    
    error_response = create_error_response(exc, request)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response,
    )


# 异常处理器映射
exception_handlers = {
    BaseCustomException: custom_exception_handler,
    StarletteHTTPException: http_exception_handler,
    RequestValidationError: validation_exception_handler,
    Exception: general_exception_handler,
}


def setup_exception_handlers(app):
    """设置异常处理器"""
    for exception_type, handler in exception_handlers.items():
        app.add_exception_handler(exception_type, handler)
