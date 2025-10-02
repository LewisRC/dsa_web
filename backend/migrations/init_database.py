"""
数据库初始化脚本
创建数据库表和初始数据
"""

import sys
import os
import logging
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import db_manager, init_database
from app.config.settings import settings
from app.core.security import security_manager
from app.models import *

logger = logging.getLogger(__name__)


def create_default_tenant():
    """创建默认租户"""
    try:
        db = db_manager.get_sync_session()
        
        # 检查默认租户是否存在
        existing_tenant = db.query(Tenant).filter(
            Tenant.code == settings.default_tenant_id
        ).first()
        
        if not existing_tenant:
            # 创建默认租户
            default_tenant = Tenant(
                code=settings.default_tenant_id,
                name="默认租户",
                description="系统默认租户",
                contact_person="系统管理员",
                contact_email="admin@example.com",
                tenant_id=settings.default_tenant_id,
                created_by="system",
            )
            
            db.add(default_tenant)
            db.commit()
            logger.info("默认租户创建成功")
        else:
            logger.info("默认租户已存在")
        
        db.close()
        
    except Exception as e:
        logger.error(f"创建默认租户失败: {e}")
        raise


def create_default_permissions():
    """创建默认权限"""
    try:
        db = db_manager.get_sync_session()
        
        # 定义默认权限
        default_permissions = [
            # 用户管理权限
            {"name": "查看用户", "code": "user:read", "module": "user", "category": "read"},
            {"name": "创建用户", "code": "user:create", "module": "user", "category": "write"},
            {"name": "编辑用户", "code": "user:update", "module": "user", "category": "write"},
            {"name": "删除用户", "code": "user:delete", "module": "user", "category": "write"},
            {"name": "管理用户", "code": "user:manage", "module": "user", "category": "admin"},
            
            # 设备管理权限
            {"name": "查看设备", "code": "device:read", "module": "device", "category": "read"},
            {"name": "创建设备", "code": "device:create", "module": "device", "category": "write"},
            {"name": "编辑设备", "code": "device:update", "module": "device", "category": "write"},
            {"name": "删除设备", "code": "device:delete", "module": "device", "category": "write"},
            {"name": "管理设备", "code": "device:manage", "module": "device", "category": "admin"},
            {"name": "控制设备", "code": "device:control", "module": "device", "category": "control"},
            
            # 对讲功能权限
            {"name": "发起对讲", "code": "intercom:initiate", "module": "intercom", "category": "use"},
            {"name": "接受对讲", "code": "intercom:accept", "module": "intercom", "category": "use"},
            {"name": "管理对讲组", "code": "intercom:group_manage", "module": "intercom", "category": "admin"},
            {"name": "查看对讲记录", "code": "intercom:record_view", "module": "intercom", "category": "read"},
            
            # 报警系统权限
            {"name": "查看报警", "code": "alarm:read", "module": "alarm", "category": "read"},
            {"name": "处理报警", "code": "alarm:handle", "module": "alarm", "category": "write"},
            {"name": "管理报警规则", "code": "alarm:rule_manage", "module": "alarm", "category": "admin"},
            {"name": "确认报警", "code": "alarm:acknowledge", "module": "alarm", "category": "write"},
            
            # 报表权限
            {"name": "查看报表", "code": "report:read", "module": "report", "category": "read"},
            {"name": "导出报表", "code": "report:export", "module": "report", "category": "export"},
            {"name": "管理报表", "code": "report:manage", "module": "report", "category": "admin"},
            
            # 系统管理权限
            {"name": "系统设置", "code": "system:settings", "module": "system", "category": "admin"},
            {"name": "租户管理", "code": "tenant:manage", "module": "system", "category": "admin"},
            {"name": "日志查看", "code": "log:read", "module": "system", "category": "read"},
            {"name": "超级管理员", "code": "system:super", "module": "system", "category": "super"},
        ]
        
        # 创建权限
        for perm_data in default_permissions:
            existing_permission = db.query(Permission).filter(
                Permission.code == perm_data["code"],
                Permission.tenant_id == settings.default_tenant_id
            ).first()
            
            if not existing_permission:
                permission = Permission(
                    tenant_id=settings.default_tenant_id,
                    created_by="system",
                    **perm_data
                )
                db.add(permission)
        
        db.commit()
        logger.info("默认权限创建成功")
        db.close()
        
    except Exception as e:
        logger.error(f"创建默认权限失败: {e}")
        raise


def create_default_roles():
    """创建默认角色"""
    try:
        db = db_manager.get_sync_session()
        
        # 定义默认角色
        default_roles = [
            {
                "name": "超级管理员",
                "code": "super_admin",
                "description": "系统超级管理员，拥有所有权限",
                "is_system": True,
                "permissions": []  # 超级管理员拥有所有权限
            },
            {
                "name": "管理员",
                "code": "admin",
                "description": "系统管理员，拥有大部分管理权限",
                "is_system": True,
                "permissions": [
                    "user:manage", "device:manage", "intercom:group_manage",
                    "alarm:rule_manage", "report:manage"
                ]
            },
            {
                "name": "操作员",
                "code": "operator",
                "description": "系统操作员，可以进行日常操作",
                "is_system": True,
                "permissions": [
                    "user:read", "device:read", "device:control",
                    "intercom:initiate", "intercom:accept",
                    "alarm:read", "alarm:handle", "alarm:acknowledge",
                    "report:read", "report:export"
                ]
            },
            {
                "name": "普通用户",
                "code": "user",
                "description": "普通用户，只能使用基本功能",
                "is_system": True,
                "permissions": [
                    "device:read", "intercom:initiate", "intercom:accept",
                    "alarm:read", "report:read"
                ]
            },
        ]
        
        # 获取所有权限
        all_permissions = db.query(Permission).filter(
            Permission.tenant_id == settings.default_tenant_id
        ).all()
        permission_map = {p.code: p for p in all_permissions}
        
        # 创建角色
        for role_data in default_roles:
            existing_role = db.query(Role).filter(
                Role.code == role_data["code"],
                Role.tenant_id == settings.default_tenant_id
            ).first()
            
            if not existing_role:
                role = Role(
                    name=role_data["name"],
                    code=role_data["code"],
                    description=role_data["description"],
                    is_system=role_data["is_system"],
                    tenant_id=settings.default_tenant_id,
                    created_by="system",
                )
                db.add(role)
                db.flush()  # 获取role的ID
                
                # 添加角色权限
                if role_data["code"] == "super_admin":
                    # 超级管理员拥有所有权限
                    for permission in all_permissions:
                        role_permission = RolePermission(
                            role_id=role.id,
                            permission_id=permission.id,
                            tenant_id=settings.default_tenant_id,
                            created_by="system",
                        )
                        db.add(role_permission)
                else:
                    # 其他角色根据配置添加权限
                    for perm_code in role_data["permissions"]:
                        if perm_code in permission_map:
                            role_permission = RolePermission(
                                role_id=role.id,
                                permission_id=permission_map[perm_code].id,
                                tenant_id=settings.default_tenant_id,
                                created_by="system",
                            )
                            db.add(role_permission)
        
        db.commit()
        logger.info("默认角色创建成功")
        db.close()
        
    except Exception as e:
        logger.error(f"创建默认角色失败: {e}")
        raise


def create_default_admin_user():
    """创建默认管理员用户"""
    try:
        db = db_manager.get_sync_session()
        
        # 检查是否已存在管理员用户
        existing_admin = db.query(User).filter(
            User.username == "admin",
            User.tenant_id == settings.default_tenant_id
        ).first()
        
        if not existing_admin:
            # 创建管理员用户
            admin_password = "admin123"  # 生产环境应使用更安全的密码
            password_hash = security_manager.create_password_hash(admin_password)
            
            admin_user = User(
                username="admin",
                email="admin@example.com",
                password_hash=password_hash,
                real_name="系统管理员",
                is_active=True,
                is_superuser=True,
                is_staff=True,
                tenant_id=settings.default_tenant_id,
                created_by="system",
            )
            
            db.add(admin_user)
            db.flush()  # 获取用户ID
            
            # 分配超级管理员角色
            super_admin_role = db.query(Role).filter(
                Role.code == "super_admin",
                Role.tenant_id == settings.default_tenant_id
            ).first()
            
            if super_admin_role:
                user_role = UserRole(
                    user_id=admin_user.id,
                    role_id=super_admin_role.id,
                    tenant_id=settings.default_tenant_id,
                    created_by="system",
                )
                db.add(user_role)
            
            db.commit()
            logger.info(f"默认管理员用户创建成功，用户名: admin, 密码: {admin_password}")
        else:
            logger.info("默认管理员用户已存在")
        
        db.close()
        
    except Exception as e:
        logger.error(f"创建默认管理员用户失败: {e}")
        raise


def create_default_device_types():
    """创建默认设备类型"""
    try:
        db = db_manager.get_sync_session()
        
        # 定义默认设备类型
        default_device_types = [
            {
                "name": "门禁对讲机",
                "code": "door_intercom",
                "category": "intercom",
                "description": "门禁对讲设备",
                "manufacturer": "通用",
                "capabilities": ["audio", "video", "door_control"],
                "protocols": ["sip", "rtsp", "http"],
            },
            {
                "name": "室内分机",
                "code": "indoor_unit",
                "category": "intercom",
                "description": "室内对讲分机",
                "manufacturer": "通用",
                "capabilities": ["audio", "video", "monitoring"],
                "protocols": ["sip", "rtsp"],
            },
            {
                "name": "监控摄像头",
                "code": "camera",
                "category": "security",
                "description": "安防监控摄像头",
                "manufacturer": "通用",
                "capabilities": ["video", "audio", "ptz", "night_vision"],
                "protocols": ["rtsp", "onvif", "http"],
            },
            {
                "name": "门禁控制器",
                "code": "access_controller",
                "category": "access",
                "description": "门禁控制设备",
                "manufacturer": "通用",
                "capabilities": ["card_reader", "fingerprint", "remote_control"],
                "protocols": ["tcp", "rs485", "wiegand"],
            },
            {
                "name": "报警探测器",
                "code": "alarm_detector",
                "category": "alarm",
                "description": "各类报警探测器",
                "manufacturer": "通用",
                "capabilities": ["motion_detection", "smoke_detection", "gas_detection"],
                "protocols": ["wireless", "rs485"],
            },
        ]
        
        # 创建设备类型
        for device_type_data in default_device_types:
            existing_type = db.query(DeviceType).filter(
                DeviceType.code == device_type_data["code"],
                DeviceType.tenant_id == settings.default_tenant_id
            ).first()
            
            if not existing_type:
                capabilities = device_type_data.pop("capabilities")
                protocols = device_type_data.pop("protocols")
                
                device_type = DeviceType(
                    tenant_id=settings.default_tenant_id,
                    created_by="system",
                    **device_type_data
                )
                
                # 设置功能特性和协议
                import json
                device_type.capabilities = json.dumps(capabilities)
                device_type.protocols = json.dumps(protocols)
                
                db.add(device_type)
        
        db.commit()
        logger.info("默认设备类型创建成功")
        db.close()
        
    except Exception as e:
        logger.error(f"创建默认设备类型失败: {e}")
        raise


def create_default_alarm_types():
    """创建默认报警类型"""
    try:
        db = db_manager.get_sync_session()
        
        # 定义默认报警类型
        default_alarm_types = [
            {
                "name": "设备离线",
                "code": "device_offline",
                "description": "设备失去网络连接",
                "severity": "medium",
                "color": "#ff9800",
                "category": "device",
                "requires_acknowledgment": True,
                "auto_escalate": True,
                "escalate_after_minutes": 30,
            },
            {
                "name": "设备故障",
                "code": "device_error",
                "description": "设备硬件或软件故障",
                "severity": "high",
                "color": "#f44336",
                "category": "device",
                "requires_acknowledgment": True,
                "auto_escalate": True,
                "escalate_after_minutes": 15,
            },
            {
                "name": "入侵检测",
                "code": "intrusion_detected",
                "description": "检测到非法入侵",
                "severity": "critical",
                "color": "#ff0000",
                "category": "security",
                "requires_acknowledgment": True,
                "auto_escalate": True,
                "escalate_after_minutes": 5,
            },
            {
                "name": "火灾报警",
                "code": "fire_alarm",
                "description": "检测到火灾或烟雾",
                "severity": "critical",
                "color": "#ff0000",
                "category": "safety",
                "requires_acknowledgment": True,
                "auto_escalate": False,
            },
            {
                "name": "门禁异常",
                "code": "access_anomaly",
                "description": "门禁系统检测到异常",
                "severity": "medium",
                "color": "#ff9800",
                "category": "access",
                "requires_acknowledgment": True,
                "auto_escalate": False,
            },
        ]
        
        # 创建报警类型
        for alarm_type_data in default_alarm_types:
            existing_type = db.query(AlarmType).filter(
                AlarmType.code == alarm_type_data["code"],
                AlarmType.tenant_id == settings.default_tenant_id
            ).first()
            
            if not existing_type:
                alarm_type = AlarmType(
                    tenant_id=settings.default_tenant_id,
                    created_by="system",
                    **alarm_type_data
                )
                db.add(alarm_type)
        
        db.commit()
        logger.info("默认报警类型创建成功")
        db.close()
        
    except Exception as e:
        logger.error(f"创建默认报警类型失败: {e}")
        raise


def main():
    """主函数"""
    try:
        logger.info("开始初始化数据库...")
        
        # 初始化数据库表
        init_database()
        
        # 创建默认数据
        create_default_tenant()
        create_default_permissions()
        create_default_roles()
        create_default_admin_user()
        create_default_device_types()
        create_default_alarm_types()
        
        logger.info("数据库初始化完成！")
        
        # 输出初始化信息
        print("\n" + "="*50)
        print("数据库初始化成功！")
        print("="*50)
        print("默认管理员账户:")
        print("  用户名: admin")
        print("  密码: admin123")
        print("  请首次登录后立即修改密码！")
        print("="*50)
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        print(f"\n数据库初始化失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    main()
