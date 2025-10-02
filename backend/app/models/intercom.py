"""
对讲系统数据模型
"""

from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import BaseModel


class IntercomSession(BaseModel):
    """对讲会话模型"""
    
    __tablename__ = "intercom_sessions"
    
    # 会话信息
    session_id = Column(
        String(100),
        unique=True,
        nullable=False,
        comment="会话ID"
    )
    
    session_type = Column(
        String(20),
        nullable=False,
        comment="会话类型"  # point_to_point, group_call, broadcast
    )
    
    # 参与者信息
    initiator_id = Column(
        String(50),
        ForeignKey("users.id"),
        nullable=False,
        comment="发起者ID"
    )
    
    initiator_device_id = Column(
        String(50),
        ForeignKey("devices.id"),
        nullable=True,
        comment="发起者设备ID"
    )
    
    # 会话状态
    status = Column(
        String(20),
        default="initiated",
        nullable=False,
        comment="会话状态"  # initiated, connecting, connected, ended, failed
    )
    
    # 时间信息
    started_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="开始时间"
    )
    
    connected_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="连接时间"
    )
    
    ended_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="结束时间"
    )
    
    duration = Column(
        Integer,
        nullable=True,
        comment="通话时长(秒)"
    )
    
    # 质量信息
    audio_quality = Column(
        Float,
        nullable=True,
        comment="音频质量评分"
    )
    
    video_quality = Column(
        Float,
        nullable=True,
        comment="视频质量评分"
    )
    
    # 技术信息
    codec = Column(
        String(50),
        nullable=True,
        comment="编解码器"
    )
    
    bitrate = Column(
        Integer,
        nullable=True,
        comment="比特率"
    )
    
    # 结束原因
    end_reason = Column(
        String(100),
        nullable=True,
        comment="结束原因"
    )
    
    error_message = Column(
        Text,
        nullable=True,
        comment="错误信息"
    )
    
    # 关联关系
    initiator = relationship("User", foreign_keys=[initiator_id], backref="initiated_sessions")
    initiator_device = relationship("Device", foreign_keys=[initiator_device_id], backref="initiated_sessions")
    
    def get_duration_display(self) -> str:
        """获取通话时长显示"""
        if not self.duration:
            return "00:00:00"
        
        hours = self.duration // 3600
        minutes = (self.duration % 3600) // 60
        seconds = self.duration % 60
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def is_active(self) -> bool:
        """检查会话是否活跃"""
        return self.status in ["initiated", "connecting", "connected"]


class IntercomParticipant(BaseModel):
    """对讲参与者模型"""
    
    __tablename__ = "intercom_participants"
    
    # 会话信息
    session_id = Column(
        String(50),
        ForeignKey("intercom_sessions.id"),
        nullable=False,
        comment="会话ID"
    )
    
    # 参与者信息
    user_id = Column(
        String(50),
        ForeignKey("users.id"),
        nullable=False,
        comment="用户ID"
    )
    
    device_id = Column(
        String(50),
        ForeignKey("devices.id"),
        nullable=True,
        comment="设备ID"
    )
    
    # 参与状态
    status = Column(
        String(20),
        default="invited",
        nullable=False,
        comment="参与状态"  # invited, joined, left, declined, failed
    )
    
    # 时间信息
    invited_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="邀请时间"
    )
    
    joined_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="加入时间"
    )
    
    left_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="离开时间"
    )
    
    # 权限设置
    can_speak = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否可以发言"
    )
    
    can_listen = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否可以收听"
    )
    
    is_moderator = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否为主持人"
    )
    
    # 质量信息
    connection_quality = Column(
        Float,
        nullable=True,
        comment="连接质量"
    )
    
    packet_loss = Column(
        Float,
        nullable=True,
        comment="丢包率"
    )
    
    latency = Column(
        Integer,
        nullable=True,
        comment="延迟(ms)"
    )
    
    # 关联关系
    session = relationship("IntercomSession", backref="participants")
    user = relationship("User", backref="intercom_participations")
    device = relationship("Device", backref="intercom_participations")


class IntercomGroup(BaseModel):
    """对讲组模型"""
    
    __tablename__ = "intercom_groups"
    
    # 组信息
    name = Column(
        String(100),
        nullable=False,
        comment="组名称"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="组描述"
    )
    
    # 组类型
    group_type = Column(
        String(20),
        default="normal",
        nullable=False,
        comment="组类型"  # normal, emergency, department
    )
    
    # 权限设置
    is_public = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否公开"
    )
    
    max_members = Column(
        Integer,
        default=100,
        nullable=False,
        comment="最大成员数"
    )
    
    # 管理员
    owner_id = Column(
        String(50),
        ForeignKey("users.id"),
        nullable=False,
        comment="创建者ID"
    )
    
    # 关联关系
    owner = relationship("User", backref="owned_intercom_groups")


class IntercomGroupMember(BaseModel):
    """对讲组成员模型"""
    
    __tablename__ = "intercom_group_members"
    
    # 关联信息
    group_id = Column(
        String(50),
        ForeignKey("intercom_groups.id"),
        nullable=False,
        comment="组ID"
    )
    
    user_id = Column(
        String(50),
        ForeignKey("users.id"),
        nullable=False,
        comment="用户ID"
    )
    
    # 角色权限
    role = Column(
        String(20),
        default="member",
        nullable=False,
        comment="成员角色"  # member, admin, moderator
    )
    
    # 权限设置
    can_invite = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否可以邀请成员"
    )
    
    can_manage = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否可以管理组"
    )
    
    # 加入信息
    joined_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="加入时间"
    )
    
    invited_by = Column(
        String(50),
        ForeignKey("users.id"),
        nullable=True,
        comment="邀请者ID"
    )
    
    # 关联关系
    group = relationship("IntercomGroup", backref="members")
    user = relationship("User", backref="intercom_group_memberships")
    inviter = relationship("User", foreign_keys=[invited_by], backref="intercom_invitations")


class IntercomContact(BaseModel):
    """对讲联系人模型"""
    
    __tablename__ = "intercom_contacts"
    
    # 用户信息
    user_id = Column(
        String(50),
        ForeignKey("users.id"),
        nullable=False,
        comment="用户ID"
    )
    
    contact_user_id = Column(
        String(50),
        ForeignKey("users.id"),
        nullable=False,
        comment="联系人用户ID"
    )
    
    # 联系人信息
    nickname = Column(
        String(100),
        nullable=True,
        comment="联系人昵称"
    )
    
    notes = Column(
        Text,
        nullable=True,
        comment="备注"
    )
    
    # 分组信息
    group_name = Column(
        String(50),
        nullable=True,
        comment="分组名称"
    )
    
    # 快速拨号
    speed_dial = Column(
        String(10),
        nullable=True,
        comment="快速拨号码"
    )
    
    # 关联关系
    user = relationship("User", foreign_keys=[user_id], backref="contacts")
    contact_user = relationship("User", foreign_keys=[contact_user_id], backref="contact_of")


class IntercomSettings(BaseModel):
    """对讲设置模型"""
    
    __tablename__ = "intercom_settings"
    
    # 用户信息
    user_id = Column(
        String(50),
        ForeignKey("users.id"),
        nullable=False,
        comment="用户ID"
    )
    
    # 音频设置
    microphone_volume = Column(
        Integer,
        default=80,
        nullable=False,
        comment="麦克风音量"
    )
    
    speaker_volume = Column(
        Integer,
        default=80,
        nullable=False,
        comment="扬声器音量"
    )
    
    echo_cancellation = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="回声消除"
    )
    
    noise_suppression = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="噪声抑制"
    )
    
    # 视频设置
    video_enabled = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="启用视频"
    )
    
    video_quality = Column(
        String(20),
        default="medium",
        nullable=False,
        comment="视频质量"  # low, medium, high
    )
    
    # 通知设置
    incoming_call_notification = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="来电通知"
    )
    
    missed_call_notification = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="未接来电通知"
    )
    
    # 自动设置
    auto_answer = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="自动接听"
    )
    
    auto_answer_delay = Column(
        Integer,
        default=3,
        nullable=False,
        comment="自动接听延迟(秒)"
    )
    
    # 状态设置
    status = Column(
        String(20),
        default="available",
        nullable=False,
        comment="在线状态"  # available, busy, away, do_not_disturb
    )
    
    status_message = Column(
        String(200),
        nullable=True,
        comment="状态消息"
    )
    
    # 关联关系
    user = relationship("User", backref="intercom_settings")


class IntercomRecord(BaseModel):
    """对讲录音模型"""
    
    __tablename__ = "intercom_records"
    
    # 会话信息
    session_id = Column(
        String(50),
        ForeignKey("intercom_sessions.id"),
        nullable=False,
        comment="会话ID"
    )
    
    # 录音信息
    file_name = Column(
        String(255),
        nullable=False,
        comment="文件名"
    )
    
    file_path = Column(
        String(500),
        nullable=False,
        comment="文件路径"
    )
    
    file_size = Column(
        Integer,
        nullable=True,
        comment="文件大小"
    )
    
    duration = Column(
        Integer,
        nullable=True,
        comment="录音时长(秒)"
    )
    
    # 录音类型
    record_type = Column(
        String(20),
        default="full",
        nullable=False,
        comment="录音类型"  # full, audio_only, video_only
    )
    
    # 质量信息
    audio_codec = Column(
        String(50),
        nullable=True,
        comment="音频编码"
    )
    
    video_codec = Column(
        String(50),
        nullable=True,
        comment="视频编码"
    )
    
    resolution = Column(
        String(20),
        nullable=True,
        comment="分辨率"
    )
    
    # 状态信息
    status = Column(
        String(20),
        default="completed",
        nullable=False,
        comment="录音状态"  # recording, completed, failed, deleted
    )
    
    # 关联关系
    session = relationship("IntercomSession", backref="records")
