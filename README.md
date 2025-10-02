# 通用安防楼宇对讲系统

## 项目概述

这是一个通用的安防和楼宇对讲系统，具备多租户支持、主题化配置和模块化扩展能力，适用于不同公司和场景的部署使用。

## 技术栈

### 后端
- **框架**: FastAPI (Python)
- **架构**: 分层架构 (Controller -> Service -> DAO)
- **数据库**: SQLite (可扩展支持 MySQL/PostgreSQL)
- **认证**: JWT Token
- **API文档**: Swagger/OpenAPI

### 前端
- **框架**: React 18
- **状态管理**: Redux Toolkit
- **UI组件**: Ant Design + 自定义主题
- **路由**: React Router
- **HTTP客户端**: Axios
- **构建工具**: Vite

## 核心特性

### 🏢 多租户支持
- 租户数据隔离
- 独立配置管理
- 品牌主题定制

### 🎨 主题化
- 可配置的品牌色彩
- 自定义Logo和标识
- 响应式布局

### 🔧 模块化架构
- 功能模块可插拔
- 权限细粒度控制
- API接口标准化

### 📊 核心功能模块
- **用户管理**: 多角色用户体系
- **设备管理**: 设备注册、监控、控制
- **实时对讲**: WebRTC音视频通信
- **报警通知**: 实时报警推送
- **日志报表**: 操作日志和统计分析

## 快速开始

### 环境要求
- Python 3.9+
- Node.js 16+
- SQLite 3

### 后端启动
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 前端启动
```bash
cd frontend
npm install
npm run dev
```

## 项目结构

详见下方目录结构说明。

## 配置说明

系统支持多环境配置，包括开发、测试、生产环境的独立配置。

## 部署指南

支持Docker容器化部署和传统服务器部署两种方式。

## 许可证

MIT License
