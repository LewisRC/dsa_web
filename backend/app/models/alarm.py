"""
报警系统数据模型
"""

from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import BaseModel, LocationMixin


class AlarmType(BaseModel):
    """报警类型模型"""
    
    __tablename__ = "alarm_types"
    
    # 类型信息
    name = Column(
        String(100),
        nullable=False,
        comment="类型名称"
    )
    
    code = Column(
        String(50),
        nullable=False,
        comment="类型代码"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="类型描述"
    )
    
    # 严重级别
    severity = Column(
        String(20),
        default="medium",
        nullable=False,
        comment="严重级别"  # low, medium, high, critical
    )
    
    # 颜色标识
    color = Column(
        String(10),
        nullable=True,
        comment="颜色标识"
    )
    
    # 图标
    icon = Column(
        String(50),
        nullable=True,
        comment="图标"
    )
    
    # 分类
    category = Column(
        String(50),
        nullable=True,
        comment="报警分类"
    )
    
    # 是否需要确认
    requires_acknowledgment = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否需要确认"
    )
    
    # 是否自动升级
    auto_escalate = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否自动升级"
    )
    
    # 升级时间(分钟)
    escalate_after_minutes = Column(
        Integer,
        nullable=True,
        comment="升级时间(分钟)"
    )
    
    # 状态
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否启用"
    )


class Alarm(BaseModel, LocationMixin):
    """报警模型"""
    
    __tablename__ = "alarms"
    
    # 报警信息
    title = Column(
        String(200),
        nullable=False,
        comment="报警标题"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="报警描述"
    )
    
    # 报警类型
    alarm_type_id = Column(
        String(50),
        ForeignKey("alarm_types.id"),
        nullable=False,
        comment="报警类型ID"
    )
    
    # 设备信息
    device_id = Column(
        String(50),
        ForeignKey("devices.id"),
        nullable=True,
        comment="报警设备ID"
    )
    
    # 严重级别
    severity = Column(
        String(20),
        nullable=False,
        comment="严重级别"
    )
    
    # 状态信息
    status = Column(
        String(20),
        default="active",
        nullable=False,
        comment="报警状态"  # active, acknowledged, resolved, closed
    )
    
    # 发生时间
    occurred_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="发生时间"
    )
    
    # 确认信息
    acknowledged = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否已确认"
    )
    
    acknowledged_by = Column(
        String(50),
        ForeignKey("users.id"),
        nullable=True,
        comment="确认人ID"
    )
    
    acknowledged_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="确认时间"
    )
    
    acknowledgment_notes = Column(
        Text,
        nullable=True,
        comment="确认备注"
    )
    
    # 解决信息
    resolved = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否已解决"
    )
    
    resolved_by = Column(
        String(50),
        ForeignKey("users.id"),
        nullable=True,
        comment="解决人ID"
    )
    
    resolved_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="解决时间"
    )
    
    resolution_notes = Column(
        Text,
        nullable=True,
        comment="解决备注"
    )
    
    # 处理时间统计
    response_time = Column(
        Integer,
        nullable=True,
        comment="响应时间(秒)"
    )
    
    resolution_time = Column(
        Integer,
        nullable=True,
        comment="解决时间(秒)"
    )
    
    # 升级信息
    escalated = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否已升级"
    )
    
    escalated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="升级时间"
    )
    
    escalation_level = Column(
        Integer,
        default=0,
        nullable=False,
        comment="升级级别"
    )
    
    # 附加数据
    additional_data = Column(
        Text,
        nullable=True,
        comment="附加数据JSON"
    )
    
    # 关联关系
    alarm_type = relationship("AlarmType", backref="alarms")
    device = relationship("Device", backref="alarms")
    acknowledged_user = relationship("User", foreign_keys=[acknowledged_by], backref="acknowledged_alarms")
    resolved_user = relationship("User", foreign_keys=[resolved_by], backref="resolved_alarms")
    
    def get_additional_data(self) -> dict:
        """获取附加数据"""
        if self.additional_data:
            import json
            try:
                return json.loads(self.additional_data)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    def set_additional_data(self, data: dict):
        """设置附加数据"""
        import json
        self.additional_data = json.dumps(data, ensure_ascii=False)
    
    def get_duration_display(self) -> str:
        """获取持续时间显示"""
        if self.resolved_at:
            delta = self.resolved_at - self.occurred_at
            total_seconds = int(delta.total_seconds())
        else:
            delta = func.now() - self.occurred_at
            total_seconds = int(delta.total_seconds()) if hasattr(delta, 'total_seconds') else 0
        
        if total_seconds < 60:
            return f"{total_seconds}秒"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            return f"{minutes}分钟"
        else:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}小时{minutes}分钟"
    
    def get_severity_display(self) -> str:
        """获取严重级别显示"""
        severity_map = {
            "low": "低",
            "medium": "中",
            "high": "高",
            "critical": "紧急",
        }
        return severity_map.get(self.severity, self.severity)


class AlarmRule(BaseModel):
    """报警规则模型"""
    
    __tablename__ = "alarm_rules"
    
    # 规则信息
    name = Column(
        String(100),
        nullable=False,
        comment="规则名称"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="规则描述"
    )
    
    # 报警类型
    alarm_type_id = Column(
        String(50),
        ForeignKey("alarm_types.id"),
        nullable=False,
        comment="报警类型ID"
    )
    
    # 触发条件
    condition_expression = Column(
        Text,
        nullable=False,
        comment="触发条件表达式"
    )
    
    # 设备过滤
    device_filter = Column(
        Text,
        nullable=True,
        comment="设备过滤条件JSON"
    )
    
    # 时间过滤
    time_filter = Column(
        Text,
        nullable=True,
        comment="时间过滤条件JSON"
    )
    
    # 阈值设置
    threshold_value = Column(
        Float,
        nullable=True,
        comment="阈值"
    )
    
    threshold_operator = Column(
        String(10),
        nullable=True,
        comment="阈值比较操作符"  # >, <, >=, <=, ==, !=
    )
    
    # 去重设置
    suppress_duplicate = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="抑制重复报警"
    )
    
    suppress_duration = Column(
        Integer,
        default=300,
        nullable=False,
        comment="抑制时间(秒)"
    )
    
    # 状态
    is_enabled = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否启用"
    )
    
    # 优先级
    priority = Column(
        Integer,
        default=0,
        nullable=False,
        comment="优先级"
    )
    
    # 关联关系
    alarm_type = relationship("AlarmType", backref="rules")
    
    def get_device_filter(self) -> dict:
        """获取设备过滤条件"""
        if self.device_filter:
            import json
            try:
                return json.loads(self.device_filter)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    def get_time_filter(self) -> dict:
        """获取时间过滤条件"""
        if self.time_filter:
            import json
            try:
                return json.loads(self.time_filter)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}


class AlarmNotificationRule(BaseModel):
    """报警通知规则模型"""
    
    __tablename__ = "alarm_notification_rules"
    
    # 规则信息
    name = Column(
        String(100),
        nullable=False,
        comment="规则名称"
    )
    
    # 报警类型过滤
    alarm_type_ids = Column(
        Text,
        nullable=True,
        comment="报警类型ID列表JSON"
    )
    
    # 严重级别过滤
    severity_filter = Column(
        Text,
        nullable=True,
        comment="严重级别过滤JSON"
    )
    
    # 通知方式
    notification_channels = Column(
        Text,
        nullable=False,
        comment="通知方式JSON"  # email, sms, push, webhook
    )
    
    # 接收人
    recipients = Column(
        Text,
        nullable=False,
        comment="接收人列表JSON"
    )
    
    # 通知模板
    email_template = Column(
        Text,
        nullable=True,
        comment="邮件模板"
    )
    
    sms_template = Column(
        Text,
        nullable=True,
        comment="短信模板"
    )
    
    # 时间设置
    active_hours = Column(
        Text,
        nullable=True,
        comment="生效时间JSON"
    )
    
    # 状态
    is_enabled = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否启用"
    )
    
    def get_alarm_type_ids(self) -> list:
        """获取报警类型ID列表"""
        if self.alarm_type_ids:
            import json
            try:
                return json.loads(self.alarm_type_ids)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    def get_notification_channels(self) -> list:
        """获取通知方式列表"""
        if self.notification_channels:
            import json
            try:
                return json.loads(self.notification_channels)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    def get_recipients(self) -> list:
        """获取接收人列表"""
        if self.recipients:
            import json
            try:
                return json.loads(self.recipients)
            except (json.JSONDecodeError, TypeError):
                return []
        return []


class AlarmNotification(BaseModel):
    """报警通知记录模型"""
    
    __tablename__ = "alarm_notifications"
    
    # 报警信息
    alarm_id = Column(
        String(50),
        ForeignKey("alarms.id"),
        nullable=False,
        comment="报警ID"
    )
    
    # 通知信息
    notification_type = Column(
        String(20),
        nullable=False,
        comment="通知类型"
    )
    
    recipient = Column(
        String(200),
        nullable=False,
        comment="接收人"
    )
    
    # 发送状态
    status = Column(
        String(20),
        default="pending",
        nullable=False,
        comment="发送状态"  # pending, sent, failed, delivered
    )
    
    sent_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="发送时间"
    )
    
    delivered_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="送达时间"
    )
    
    # 错误信息
    error_message = Column(
        Text,
        nullable=True,
        comment="错误信息"
    )
    
    # 重试信息
    retry_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="重试次数"
    )
    
    max_retries = Column(
        Integer,
        default=3,
        nullable=False,
        comment="最大重试次数"
    )
    
    # 关联关系
    alarm = relationship("Alarm", backref="notifications")


class AlarmEscalation(BaseModel):
    """报警升级记录模型"""
    
    __tablename__ = "alarm_escalations"
    
    # 报警信息
    alarm_id = Column(
        String(50),
        ForeignKey("alarms.id"),
        nullable=False,
        comment="报警ID"
    )
    
    # 升级信息
    from_level = Column(
        Integer,
        nullable=False,
        comment="原级别"
    )
    
    to_level = Column(
        Integer,
        nullable=False,
        comment="升级到级别"
    )
    
    escalated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="升级时间"
    )
    
    # 升级原因
    reason = Column(
        String(100),
        nullable=True,
        comment="升级原因"
    )
    
    # 升级规则
    escalation_rule_id = Column(
        String(50),
        nullable=True,
        comment="升级规则ID"
    )
    
    # 通知信息
    notifications_sent = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否已发送通知"
    )
    
    # 关联关系
    alarm = relationship("Alarm", backref="escalations")


class AlarmStatistics(BaseModel):
    """报警统计模型"""
    
    __tablename__ = "alarm_statistics"
    
    # 统计时间
    date = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="统计日期"
    )
    
    # 统计维度
    dimension_type = Column(
        String(20),
        nullable=False,
        comment="统计维度"  # daily, weekly, monthly
    )
    
    dimension_value = Column(
        String(50),
        nullable=False,
        comment="维度值"
    )
    
    # 统计数据
    total_alarms = Column(
        Integer,
        default=0,
        nullable=False,
        comment="总报警数"
    )
    
    critical_alarms = Column(
        Integer,
        default=0,
        nullable=False,
        comment="紧急报警数"
    )
    
    high_alarms = Column(
        Integer,
        default=0,
        nullable=False,
        comment="高级报警数"
    )
    
    medium_alarms = Column(
        Integer,
        default=0,
        nullable=False,
        comment="中级报警数"
    )
    
    low_alarms = Column(
        Integer,
        default=0,
        nullable=False,
        comment="低级报警数"
    )
    
    # 处理统计
    acknowledged_alarms = Column(
        Integer,
        default=0,
        nullable=False,
        comment="已确认报警数"
    )
    
    resolved_alarms = Column(
        Integer,
        default=0,
        nullable=False,
        comment="已解决报警数"
    )
    
    # 时间统计
    avg_response_time = Column(
        Float,
        nullable=True,
        comment="平均响应时间(秒)"
    )
    
    avg_resolution_time = Column(
        Float,
        nullable=True,
        comment="平均解决时间(秒)"
    )
