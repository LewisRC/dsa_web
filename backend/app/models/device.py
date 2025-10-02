"""
设备数据模型
"""

from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import BaseModel, ConfigurableBaseModel, LocationMixin


class DeviceType(ConfigurableBaseModel):
    """设备类型模型"""
    
    __tablename__ = "device_types"
    
    # 类型信息
    code = Column(
        String(50),
        nullable=False,
        comment="类型代码"
    )
    
    category = Column(
        String(50),
        nullable=False,
        comment="设备分类"
    )
    
    # 厂商信息
    manufacturer = Column(
        String(100),
        nullable=True,
        comment="厂商"
    )
    
    model = Column(
        String(100),
        nullable=True,
        comment="型号"
    )
    
    # 功能特性
    capabilities = Column(
        Text,
        nullable=True,
        comment="功能特性JSON"
    )
    
    # 支持协议
    protocols = Column(
        Text,
        nullable=True,
        comment="支持协议JSON"
    )
    
    def get_capabilities(self) -> list:
        """获取功能特性列表"""
        if self.capabilities:
            import json
            try:
                return json.loads(self.capabilities)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    def get_protocols(self) -> list:
        """获取支持协议列表"""
        if self.protocols:
            import json
            try:
                return json.loads(self.protocols)
            except (json.JSONDecodeError, TypeError):
                return []
        return []


class Device(BaseModel, LocationMixin):
    """设备模型"""
    
    __tablename__ = "devices"
    
    # 基本信息
    name = Column(
        String(100),
        nullable=False,
        comment="设备名称"
    )
    
    code = Column(
        String(50),
        nullable=False,
        comment="设备编码"
    )
    
    serial_number = Column(
        String(100),
        nullable=True,
        comment="序列号"
    )
    
    # 设备类型
    device_type_id = Column(
        String(50),
        ForeignKey("device_types.id"),
        nullable=False,
        comment="设备类型ID"
    )
    
    # 网络信息
    ip_address = Column(
        String(50),
        nullable=True,
        comment="IP地址"
    )
    
    port = Column(
        Integer,
        nullable=True,
        comment="端口"
    )
    
    mac_address = Column(
        String(20),
        nullable=True,
        comment="MAC地址"
    )
    
    # 状态信息
    status = Column(
        String(20),
        default="offline",
        nullable=False,
        comment="设备状态"
    )
    
    is_online = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否在线"
    )
    
    last_online_time = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="最后在线时间"
    )
    
    # 配置信息
    configuration = Column(
        Text,
        nullable=True,
        comment="设备配置JSON"
    )
    
    firmware_version = Column(
        String(50),
        nullable=True,
        comment="固件版本"
    )
    
    software_version = Column(
        String(50),
        nullable=True,
        comment="软件版本"
    )
    
    # 监控信息
    cpu_usage = Column(
        Float,
        nullable=True,
        comment="CPU使用率"
    )
    
    memory_usage = Column(
        Float,
        nullable=True,
        comment="内存使用率"
    )
    
    disk_usage = Column(
        Float,
        nullable=True,
        comment="磁盘使用率"
    )
    
    temperature = Column(
        Float,
        nullable=True,
        comment="温度"
    )
    
    # 安装信息
    install_date = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="安装日期"
    )
    
    warranty_expires = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="保修到期日期"
    )
    
    # 责任人
    manager_id = Column(
        String(50),
        ForeignKey("users.id"),
        nullable=True,
        comment="负责人ID"
    )
    
    # 备注
    notes = Column(
        Text,
        nullable=True,
        comment="备注"
    )
    
    # 关联关系
    device_type = relationship("DeviceType", backref="devices")
    manager = relationship("User", backref="managed_devices")
    
    def get_configuration(self) -> dict:
        """获取设备配置"""
        if self.configuration:
            import json
            try:
                return json.loads(self.configuration)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    def set_configuration(self, config: dict):
        """设置设备配置"""
        import json
        self.configuration = json.dumps(config, ensure_ascii=False)
    
    def is_healthy(self) -> bool:
        """检查设备是否健康"""
        if not self.is_online:
            return False
        
        # 检查CPU使用率
        if self.cpu_usage and self.cpu_usage > 90:
            return False
        
        # 检查内存使用率
        if self.memory_usage and self.memory_usage > 90:
            return False
        
        # 检查磁盘使用率
        if self.disk_usage and self.disk_usage > 95:
            return False
        
        # 检查温度
        if self.temperature and self.temperature > 70:
            return False
        
        return True
    
    def get_status_display(self) -> str:
        """获取状态显示文本"""
        status_map = {
            "online": "在线",
            "offline": "离线",
            "error": "故障",
            "maintenance": "维护中",
            "disabled": "已禁用",
        }
        return status_map.get(self.status, self.status)


class DeviceGroup(BaseModel):
    """设备组模型"""
    
    __tablename__ = "device_groups"
    
    # 组信息
    name = Column(
        String(100),
        nullable=False,
        comment="组名称"
    )
    
    code = Column(
        String(50),
        nullable=False,
        comment="组编码"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="描述"
    )
    
    # 父组
    parent_id = Column(
        String(50),
        ForeignKey("device_groups.id"),
        nullable=True,
        comment="父组ID"
    )
    
    # 层级
    level = Column(
        Integer,
        default=0,
        nullable=False,
        comment="层级"
    )
    
    # 排序
    sort_order = Column(
        Integer,
        default=0,
        nullable=False,
        comment="排序"
    )
    
    # 关联关系
    parent = relationship("DeviceGroup", remote_side="DeviceGroup.id", backref="children")


class DeviceGroupMember(BaseModel):
    """设备组成员模型"""
    
    __tablename__ = "device_group_members"
    
    # 关联字段
    group_id = Column(
        String(50),
        ForeignKey("device_groups.id"),
        nullable=False,
        comment="组ID"
    )
    
    device_id = Column(
        String(50),
        ForeignKey("devices.id"),
        nullable=False,
        comment="设备ID"
    )
    
    # 关联关系
    group = relationship("DeviceGroup", backref="members")
    device = relationship("Device", backref="groups")


class DeviceLog(BaseModel):
    """设备日志模型"""
    
    __tablename__ = "device_logs"
    
    # 设备信息
    device_id = Column(
        String(50),
        ForeignKey("devices.id"),
        nullable=False,
        comment="设备ID"
    )
    
    # 日志信息
    level = Column(
        String(20),
        nullable=False,
        comment="日志级别"
    )
    
    message = Column(
        Text,
        nullable=False,
        comment="日志消息"
    )
    
    category = Column(
        String(50),
        nullable=True,
        comment="日志分类"
    )
    
    # 事件信息
    event_type = Column(
        String(50),
        nullable=True,
        comment="事件类型"
    )
    
    event_data = Column(
        Text,
        nullable=True,
        comment="事件数据JSON"
    )
    
    # 时间信息
    timestamp = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="时间戳"
    )
    
    # 关联关系
    device = relationship("Device", backref="logs")
    
    def get_event_data(self) -> dict:
        """获取事件数据"""
        if self.event_data:
            import json
            try:
                return json.loads(self.event_data)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}


class DeviceCommand(BaseModel):
    """设备命令模型"""
    
    __tablename__ = "device_commands"
    
    # 设备信息
    device_id = Column(
        String(50),
        ForeignKey("devices.id"),
        nullable=False,
        comment="设备ID"
    )
    
    # 命令信息
    command = Column(
        String(100),
        nullable=False,
        comment="命令"
    )
    
    parameters = Column(
        Text,
        nullable=True,
        comment="参数JSON"
    )
    
    # 执行信息
    status = Column(
        String(20),
        default="pending",
        nullable=False,
        comment="执行状态"
    )
    
    executed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="执行时间"
    )
    
    result = Column(
        Text,
        nullable=True,
        comment="执行结果"
    )
    
    error_message = Column(
        Text,
        nullable=True,
        comment="错误信息"
    )
    
    # 执行者
    executor_id = Column(
        String(50),
        ForeignKey("users.id"),
        nullable=True,
        comment="执行者ID"
    )
    
    # 关联关系
    device = relationship("Device", backref="commands")
    executor = relationship("User", backref="executed_commands")
    
    def get_parameters(self) -> dict:
        """获取命令参数"""
        if self.parameters:
            import json
            try:
                return json.loads(self.parameters)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    def set_parameters(self, params: dict):
        """设置命令参数"""
        import json
        self.parameters = json.dumps(params, ensure_ascii=False)


class DeviceAlert(BaseModel):
    """设备警报模型"""
    
    __tablename__ = "device_alerts"
    
    # 设备信息
    device_id = Column(
        String(50),
        ForeignKey("devices.id"),
        nullable=False,
        comment="设备ID"
    )
    
    # 警报信息
    alert_type = Column(
        String(50),
        nullable=False,
        comment="警报类型"
    )
    
    severity = Column(
        String(20),
        nullable=False,
        comment="严重程度"
    )
    
    title = Column(
        String(200),
        nullable=False,
        comment="警报标题"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="警报描述"
    )
    
    # 状态信息
    status = Column(
        String(20),
        default="active",
        nullable=False,
        comment="警报状态"
    )
    
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
        comment="确认者ID"
    )
    
    acknowledged_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="确认时间"
    )
    
    resolved_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="解决时间"
    )
    
    # 关联关系
    device = relationship("Device", backref="alerts")
    acknowledged_user = relationship("User", backref="acknowledged_alerts")
