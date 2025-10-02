"""
日志系统数据模型
"""

from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import BaseModel


class SystemLog(BaseModel):
    """系统日志模型"""
    
    __tablename__ = "system_logs"
    
    # 日志基本信息
    level = Column(
        String(20),
        nullable=False,
        comment="日志级别"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    )
    
    message = Column(
        Text,
        nullable=False,
        comment="日志消息"
    )
    
    # 日志分类
    category = Column(
        String(50),
        nullable=True,
        comment="日志分类"
    )
    
    module = Column(
        String(100),
        nullable=True,
        comment="模块名称"
    )
    
    function = Column(
        String(100),
        nullable=True,
        comment="函数名称"
    )
    
    # 时间信息
    timestamp = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="时间戳"
    )
    
    # 请求信息
    request_id = Column(
        String(50),
        nullable=True,
        comment="请求ID"
    )
    
    session_id = Column(
        String(50),
        nullable=True,
        comment="会话ID"
    )
    
    # 用户信息
    user_id = Column(
        String(50),
        ForeignKey("users.id"),
        nullable=True,
        comment="用户ID"
    )
    
    # 网络信息
    ip_address = Column(
        String(50),
        nullable=True,
        comment="IP地址"
    )
    
    user_agent = Column(
        Text,
        nullable=True,
        comment="用户代理"
    )
    
    # 异常信息
    exception_type = Column(
        String(100),
        nullable=True,
        comment="异常类型"
    )
    
    stack_trace = Column(
        Text,
        nullable=True,
        comment="堆栈跟踪"
    )
    
    # 附加数据
    extra_data = Column(
        Text,
        nullable=True,
        comment="附加数据JSON"
    )
    
    # 关联关系
    user = relationship("User", backref="system_logs")
    
    # 索引
    __table_args__ = (
        Index('idx_system_logs_timestamp', 'timestamp'),
        Index('idx_system_logs_level', 'level'),
        Index('idx_system_logs_category', 'category'),
        Index('idx_system_logs_user_id', 'user_id'),
        Index('idx_system_logs_tenant_id', 'tenant_id'),
    )
    
    def get_extra_data(self) -> dict:
        """获取附加数据"""
        if self.extra_data:
            import json
            try:
                return json.loads(self.extra_data)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    def set_extra_data(self, data: dict):
        """设置附加数据"""
        import json
        self.extra_data = json.dumps(data, ensure_ascii=False)


class OperationLog(BaseModel):
    """操作日志模型"""
    
    __tablename__ = "operation_logs"
    
    # 操作基本信息
    operation_type = Column(
        String(50),
        nullable=False,
        comment="操作类型"  # CREATE, UPDATE, DELETE, LOGIN, LOGOUT, etc.
    )
    
    operation_name = Column(
        String(100),
        nullable=False,
        comment="操作名称"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="操作描述"
    )
    
    # 资源信息
    resource_type = Column(
        String(50),
        nullable=True,
        comment="资源类型"
    )
    
    resource_id = Column(
        String(50),
        nullable=True,
        comment="资源ID"
    )
    
    resource_name = Column(
        String(200),
        nullable=True,
        comment="资源名称"
    )
    
    # 操作者信息
    user_id = Column(
        String(50),
        ForeignKey("users.id"),
        nullable=True,
        comment="操作者ID"
    )
    
    username = Column(
        String(50),
        nullable=True,
        comment="操作者用户名"
    )
    
    # 请求信息
    request_method = Column(
        String(10),
        nullable=True,
        comment="请求方法"
    )
    
    request_url = Column(
        String(500),
        nullable=True,
        comment="请求URL"
    )
    
    request_params = Column(
        Text,
        nullable=True,
        comment="请求参数JSON"
    )
    
    response_status = Column(
        Integer,
        nullable=True,
        comment="响应状态码"
    )
    
    # 网络信息
    ip_address = Column(
        String(50),
        nullable=True,
        comment="IP地址"
    )
    
    user_agent = Column(
        Text,
        nullable=True,
        comment="用户代理"
    )
    
    # 时间信息
    timestamp = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="操作时间"
    )
    
    duration = Column(
        Integer,
        nullable=True,
        comment="操作耗时(毫秒)"
    )
    
    # 结果信息
    success = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否成功"
    )
    
    error_message = Column(
        Text,
        nullable=True,
        comment="错误消息"
    )
    
    # 数据变更
    old_values = Column(
        Text,
        nullable=True,
        comment="变更前数据JSON"
    )
    
    new_values = Column(
        Text,
        nullable=True,
        comment="变更后数据JSON"
    )
    
    # 关联关系
    user = relationship("User", backref="operation_logs")
    
    # 索引
    __table_args__ = (
        Index('idx_operation_logs_timestamp', 'timestamp'),
        Index('idx_operation_logs_user_id', 'user_id'),
        Index('idx_operation_logs_operation_type', 'operation_type'),
        Index('idx_operation_logs_resource_type', 'resource_type'),
        Index('idx_operation_logs_tenant_id', 'tenant_id'),
    )
    
    def get_request_params(self) -> dict:
        """获取请求参数"""
        if self.request_params:
            import json
            try:
                return json.loads(self.request_params)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    def get_old_values(self) -> dict:
        """获取变更前数据"""
        if self.old_values:
            import json
            try:
                return json.loads(self.old_values)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    def get_new_values(self) -> dict:
        """获取变更后数据"""
        if self.new_values:
            import json
            try:
                return json.loads(self.new_values)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}


class AccessLog(BaseModel):
    """访问日志模型"""
    
    __tablename__ = "access_logs"
    
    # 访问信息
    user_id = Column(
        String(50),
        ForeignKey("users.id"),
        nullable=True,
        comment="用户ID"
    )
    
    username = Column(
        String(50),
        nullable=True,
        comment="用户名"
    )
    
    # 请求信息
    method = Column(
        String(10),
        nullable=False,
        comment="请求方法"
    )
    
    url = Column(
        String(500),
        nullable=False,
        comment="请求URL"
    )
    
    path = Column(
        String(500),
        nullable=False,
        comment="请求路径"
    )
    
    query_params = Column(
        Text,
        nullable=True,
        comment="查询参数"
    )
    
    # 响应信息
    status_code = Column(
        Integer,
        nullable=False,
        comment="响应状态码"
    )
    
    response_size = Column(
        Integer,
        nullable=True,
        comment="响应大小(字节)"
    )
    
    response_time = Column(
        Integer,
        nullable=True,
        comment="响应时间(毫秒)"
    )
    
    # 网络信息
    ip_address = Column(
        String(50),
        nullable=True,
        comment="IP地址"
    )
    
    user_agent = Column(
        Text,
        nullable=True,
        comment="用户代理"
    )
    
    referer = Column(
        String(500),
        nullable=True,
        comment="来源页面"
    )
    
    # 时间信息
    timestamp = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="访问时间"
    )
    
    # 地理信息
    country = Column(
        String(100),
        nullable=True,
        comment="国家"
    )
    
    region = Column(
        String(100),
        nullable=True,
        comment="地区"
    )
    
    city = Column(
        String(100),
        nullable=True,
        comment="城市"
    )
    
    # 关联关系
    user = relationship("User", backref="access_logs")
    
    # 索引
    __table_args__ = (
        Index('idx_access_logs_timestamp', 'timestamp'),
        Index('idx_access_logs_user_id', 'user_id'),
        Index('idx_access_logs_ip_address', 'ip_address'),
        Index('idx_access_logs_status_code', 'status_code'),
        Index('idx_access_logs_tenant_id', 'tenant_id'),
    )


class DeviceOperationLog(BaseModel):
    """设备操作日志模型"""
    
    __tablename__ = "device_operation_logs"
    
    # 设备信息
    device_id = Column(
        String(50),
        ForeignKey("devices.id"),
        nullable=False,
        comment="设备ID"
    )
    
    device_name = Column(
        String(100),
        nullable=True,
        comment="设备名称"
    )
    
    # 操作信息
    operation_type = Column(
        String(50),
        nullable=False,
        comment="操作类型"
    )
    
    operation_name = Column(
        String(100),
        nullable=False,
        comment="操作名称"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="操作描述"
    )
    
    # 操作者信息
    operator_id = Column(
        String(50),
        ForeignKey("users.id"),
        nullable=True,
        comment="操作者ID"
    )
    
    operator_name = Column(
        String(100),
        nullable=True,
        comment="操作者名称"
    )
    
    # 操作参数
    parameters = Column(
        Text,
        nullable=True,
        comment="操作参数JSON"
    )
    
    # 执行结果
    result = Column(
        String(20),
        nullable=False,
        comment="执行结果"  # success, failed, timeout
    )
    
    result_message = Column(
        Text,
        nullable=True,
        comment="结果消息"
    )
    
    error_code = Column(
        String(50),
        nullable=True,
        comment="错误代码"
    )
    
    # 时间信息
    timestamp = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="操作时间"
    )
    
    duration = Column(
        Integer,
        nullable=True,
        comment="执行时长(毫秒)"
    )
    
    # 关联关系
    device = relationship("Device", backref="operation_logs")
    operator = relationship("User", backref="device_operation_logs")
    
    # 索引
    __table_args__ = (
        Index('idx_device_operation_logs_timestamp', 'timestamp'),
        Index('idx_device_operation_logs_device_id', 'device_id'),
        Index('idx_device_operation_logs_operator_id', 'operator_id'),
        Index('idx_device_operation_logs_result', 'result'),
        Index('idx_device_operation_logs_tenant_id', 'tenant_id'),
    )
    
    def get_parameters(self) -> dict:
        """获取操作参数"""
        if self.parameters:
            import json
            try:
                return json.loads(self.parameters)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}


class LoginLog(BaseModel):
    """登录日志模型"""
    
    __tablename__ = "login_logs"
    
    # 用户信息
    user_id = Column(
        String(50),
        ForeignKey("users.id"),
        nullable=True,
        comment="用户ID"
    )
    
    username = Column(
        String(50),
        nullable=False,
        comment="用户名"
    )
    
    # 登录信息
    login_type = Column(
        String(20),
        nullable=False,
        comment="登录类型"  # web, mobile, api, sso
    )
    
    login_method = Column(
        String(20),
        nullable=False,
        comment="登录方式"  # password, oauth, sms, etc.
    )
    
    # 结果信息
    success = Column(
        Boolean,
        nullable=False,
        comment="是否成功"
    )
    
    failure_reason = Column(
        String(100),
        nullable=True,
        comment="失败原因"
    )
    
    # 设备信息
    device_info = Column(
        Text,
        nullable=True,
        comment="设备信息JSON"
    )
    
    browser = Column(
        String(100),
        nullable=True,
        comment="浏览器"
    )
    
    os = Column(
        String(100),
        nullable=True,
        comment="操作系统"
    )
    
    # 网络信息
    ip_address = Column(
        String(50),
        nullable=True,
        comment="IP地址"
    )
    
    location = Column(
        String(200),
        nullable=True,
        comment="地理位置"
    )
    
    # 会话信息
    session_id = Column(
        String(100),
        nullable=True,
        comment="会话ID"
    )
    
    logout_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="登出时间"
    )
    
    session_duration = Column(
        Integer,
        nullable=True,
        comment="会话时长(秒)"
    )
    
    # 时间信息
    timestamp = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="登录时间"
    )
    
    # 关联关系
    user = relationship("User", backref="login_logs")
    
    # 索引
    __table_args__ = (
        Index('idx_login_logs_timestamp', 'timestamp'),
        Index('idx_login_logs_user_id', 'user_id'),
        Index('idx_login_logs_username', 'username'),
        Index('idx_login_logs_success', 'success'),
        Index('idx_login_logs_ip_address', 'ip_address'),
        Index('idx_login_logs_tenant_id', 'tenant_id'),
    )
    
    def get_device_info(self) -> dict:
        """获取设备信息"""
        if self.device_info:
            import json
            try:
                return json.loads(self.device_info)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}


class AuditTrail(BaseModel):
    """审计追踪模型"""
    
    __tablename__ = "audit_trails"
    
    # 审计信息
    event_type = Column(
        String(50),
        nullable=False,
        comment="事件类型"
    )
    
    event_name = Column(
        String(100),
        nullable=False,
        comment="事件名称"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="事件描述"
    )
    
    # 主体信息
    subject_type = Column(
        String(50),
        nullable=False,
        comment="主体类型"  # user, system, device
    )
    
    subject_id = Column(
        String(50),
        nullable=True,
        comment="主体ID"
    )
    
    subject_name = Column(
        String(100),
        nullable=True,
        comment="主体名称"
    )
    
    # 对象信息
    object_type = Column(
        String(50),
        nullable=True,
        comment="对象类型"
    )
    
    object_id = Column(
        String(50),
        nullable=True,
        comment="对象ID"
    )
    
    object_name = Column(
        String(100),
        nullable=True,
        comment="对象名称"
    )
    
    # 操作结果
    result = Column(
        String(20),
        nullable=False,
        comment="操作结果"  # success, failure, unknown
    )
    
    risk_level = Column(
        String(20),
        default="low",
        nullable=False,
        comment="风险级别"  # low, medium, high, critical
    )
    
    # 时间信息
    timestamp = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="事件时间"
    )
    
    # 上下文信息
    context_data = Column(
        Text,
        nullable=True,
        comment="上下文数据JSON"
    )
    
    # 合规标记
    compliance_tags = Column(
        Text,
        nullable=True,
        comment="合规标签JSON"
    )
    
    # 索引
    __table_args__ = (
        Index('idx_audit_trails_timestamp', 'timestamp'),
        Index('idx_audit_trails_event_type', 'event_type'),
        Index('idx_audit_trails_subject_type', 'subject_type'),
        Index('idx_audit_trails_object_type', 'object_type'),
        Index('idx_audit_trails_risk_level', 'risk_level'),
        Index('idx_audit_trails_tenant_id', 'tenant_id'),
    )
    
    def get_context_data(self) -> dict:
        """获取上下文数据"""
        if self.context_data:
            import json
            try:
                return json.loads(self.context_data)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    def get_compliance_tags(self) -> list:
        """获取合规标签"""
        if self.compliance_tags:
            import json
            try:
                return json.loads(self.compliance_tags)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
