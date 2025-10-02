# 项目目录结构

## 总体架构

```
universal-security-intercom/
├── backend/                          # 后端项目
│   ├── app/                         # 应用程序代码
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI应用入口
│   │   ├── config/                  # 配置管理
│   │   │   ├── __init__.py
│   │   │   ├── settings.py         # 应用配置
│   │   │   ├── database.py         # 数据库配置
│   │   │   └── tenant_config.py    # 租户配置
│   │   ├── core/                    # 核心功能
│   │   │   ├── __init__.py
│   │   │   ├── security.py         # 安全认证
│   │   │   ├── dependencies.py     # 依赖注入
│   │   │   ├── exceptions.py       # 异常处理
│   │   │   └── middleware.py       # 中间件
│   │   ├── models/                  # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # 基础模型
│   │   │   ├── user.py             # 用户模型
│   │   │   ├── device.py           # 设备模型
│   │   │   ├── tenant.py           # 租户模型
│   │   │   ├── intercom.py         # 对讲模型
│   │   │   ├── alarm.py            # 报警模型
│   │   │   └── log.py              # 日志模型
│   │   ├── dao/                     # 数据访问层
│   │   │   ├── __init__.py
│   │   │   ├── base_dao.py         # 基础DAO
│   │   │   ├── user_dao.py         # 用户DAO
│   │   │   ├── device_dao.py       # 设备DAO
│   │   │   ├── tenant_dao.py       # 租户DAO
│   │   │   ├── intercom_dao.py     # 对讲DAO
│   │   │   ├── alarm_dao.py        # 报警DAO
│   │   │   └── log_dao.py          # 日志DAO
│   │   ├── services/                # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── base_service.py     # 基础服务
│   │   │   ├── user_service.py     # 用户服务
│   │   │   ├── device_service.py   # 设备服务
│   │   │   ├── tenant_service.py   # 租户服务
│   │   │   ├── intercom_service.py # 对讲服务
│   │   │   ├── alarm_service.py    # 报警服务
│   │   │   ├── log_service.py      # 日志服务
│   │   │   └── auth_service.py     # 认证服务
│   │   ├── controllers/             # 控制器层
│   │   │   ├── __init__.py
│   │   │   ├── base_controller.py  # 基础控制器
│   │   │   ├── user_controller.py  # 用户控制器
│   │   │   ├── device_controller.py# 设备控制器
│   │   │   ├── tenant_controller.py# 租户控制器
│   │   │   ├── intercom_controller.py # 对讲控制器
│   │   │   ├── alarm_controller.py # 报警控制器
│   │   │   ├── log_controller.py   # 日志控制器
│   │   │   └── auth_controller.py  # 认证控制器
│   │   └── utils/                   # 工具函数
│   │       ├── __init__.py
│   │       ├── validators.py       # 数据验证
│   │       ├── formatters.py       # 数据格式化
│   │       ├── encryption.py       # 加密工具
│   │       └── websocket.py        # WebSocket工具
│   ├── tests/                       # 测试代码
│   │   ├── __init__.py
│   │   ├── conftest.py             # 测试配置
│   │   ├── test_models/            # 模型测试
│   │   ├── test_services/          # 服务测试
│   │   └── test_controllers/       # 控制器测试
│   ├── migrations/                  # 数据库迁移
│   │   └── init_database.py        # 数据库初始化
│   ├── requirements.txt             # Python依赖
│   └── run.py                      # 启动脚本
├── frontend/                        # 前端项目
│   ├── public/                     # 静态资源
│   │   ├── index.html
│   │   ├── favicon.ico
│   │   └── config/                 # 前端配置
│   │       └── tenant-configs.json # 租户配置
│   ├── src/                        # 源代码
│   │   ├── main.tsx               # 应用入口
│   │   ├── App.tsx                # 主应用组件
│   │   ├── components/            # 通用组件
│   │   │   ├── common/            # 基础组件
│   │   │   │   ├── Layout/        # 布局组件
│   │   │   │   ├── Header/        # 头部组件
│   │   │   │   ├── Sidebar/       # 侧边栏组件
│   │   │   │   ├── Footer/        # 底部组件
│   │   │   │   └── Loading/       # 加载组件
│   │   │   ├── forms/             # 表单组件
│   │   │   │   ├── LoginForm/     # 登录表单
│   │   │   │   ├── UserForm/      # 用户表单
│   │   │   │   └── DeviceForm/    # 设备表单
│   │   │   └── charts/            # 图表组件
│   │   │       ├── LineChart/     # 折线图
│   │   │       ├── PieChart/      # 饼图
│   │   │       └── BarChart/      # 柱状图
│   │   ├── pages/                 # 页面组件
│   │   │   ├── Dashboard/         # 仪表板
│   │   │   ├── Users/             # 用户管理
│   │   │   │   ├── UserList.tsx   # 用户列表
│   │   │   │   ├── UserDetail.tsx # 用户详情
│   │   │   │   └── UserCreate.tsx # 创建用户
│   │   │   ├── Devices/           # 设备管理
│   │   │   │   ├── DeviceList.tsx # 设备列表
│   │   │   │   ├── DeviceDetail.tsx # 设备详情
│   │   │   │   └── DeviceCreate.tsx # 创建设备
│   │   │   ├── Intercom/          # 对讲功能
│   │   │   │   ├── IntercomList.tsx # 对讲列表
│   │   │   │   └── IntercomRoom.tsx # 对讲房间
│   │   │   ├── Alarms/            # 报警管理
│   │   │   │   ├── AlarmList.tsx  # 报警列表
│   │   │   │   └── AlarmDetail.tsx # 报警详情
│   │   │   ├── Reports/           # 报表分析
│   │   │   │   ├── ReportList.tsx # 报表列表
│   │   │   │   └── ReportDetail.tsx # 报表详情
│   │   │   ├── Settings/          # 系统设置
│   │   │   │   ├── TenantSettings.tsx # 租户设置
│   │   │   │   └── SystemSettings.tsx # 系统设置
│   │   │   └── Auth/              # 认证相关
│   │   │       ├── Login.tsx      # 登录页
│   │   │       └── Register.tsx   # 注册页
│   │   ├── services/              # API服务
│   │   │   ├── api.ts             # API基础配置
│   │   │   ├── auth.ts            # 认证API
│   │   │   ├── user.ts            # 用户API
│   │   │   ├── device.ts          # 设备API
│   │   │   ├── intercom.ts        # 对讲API
│   │   │   ├── alarm.ts           # 报警API
│   │   │   └── report.ts          # 报表API
│   │   ├── store/                 # 状态管理
│   │   │   ├── index.ts           # Store配置
│   │   │   ├── slices/            # Redux Slices
│   │   │   │   ├── authSlice.ts   # 认证状态
│   │   │   │   ├── userSlice.ts   # 用户状态
│   │   │   │   ├── deviceSlice.ts # 设备状态
│   │   │   │   └── tenantSlice.ts # 租户状态
│   │   │   └── middleware/        # 中间件
│   │   │       └── apiMiddleware.ts # API中间件
│   │   ├── utils/                 # 工具函数
│   │   │   ├── constants.ts       # 常量定义
│   │   │   ├── formatters.ts      # 格式化工具
│   │   │   ├── validators.ts      # 验证工具
│   │   │   └── theme.ts           # 主题配置
│   │   ├── styles/                # 样式文件
│   │   │   ├── globals.css        # 全局样式
│   │   │   ├── themes/            # 主题样式
│   │   │   │   ├── default.css    # 默认主题
│   │   │   │   └── dark.css       # 深色主题
│   │   │   └── components/        # 组件样式
│   │   └── assets/                # 静态资源
│   │       ├── images/            # 图片资源
│   │       ├── icons/             # 图标资源
│   │       └── fonts/             # 字体资源
│   ├── package.json               # 项目依赖
│   ├── vite.config.ts            # Vite配置
│   ├── tsconfig.json             # TypeScript配置
│   └── tailwind.config.js        # Tailwind配置
├── docker/                        # Docker配置
│   ├── Dockerfile.backend        # 后端Docker文件
│   ├── Dockerfile.frontend       # 前端Docker文件
│   └── docker-compose.yml        # Docker Compose配置
├── scripts/                       # 脚本文件
│   ├── start.sh                  # 启动脚本
│   ├── build.sh                  # 构建脚本
│   └── deploy.sh                 # 部署脚本
├── docs/                         # 项目文档
│   ├── API.md                    # API文档
│   ├── DEPLOYMENT.md             # 部署文档
│   └── CONFIGURATION.md          # 配置文档
├── .gitignore                    # Git忽略文件
├── .env.example                  # 环境变量示例
└── README.md                     # 项目说明
```

## 架构说明

### 后端架构
- **分层架构**: Controller -> Service -> DAO -> Model
- **依赖注入**: 使用FastAPI的依赖注入系统
- **多租户**: 基于租户ID的数据隔离
- **API标准**: RESTful API设计，支持OpenAPI文档

### 前端架构
- **组件化**: 基于React的组件化开发
- **状态管理**: Redux Toolkit统一状态管理
- **主题化**: 支持多主题切换和品牌定制
- **模块化**: 页面和功能模块独立开发

### 数据库设计
- **多租户支持**: 所有表包含tenant_id字段
- **软删除**: 支持数据的软删除和恢复
- **审计日志**: 记录所有重要操作的日志

### 安全设计
- **JWT认证**: 基于Token的无状态认证
- **权限控制**: RBAC角色权限模型
- **数据加密**: 敏感数据加密存储
- **接口防护**: 请求频率限制和参数验证
