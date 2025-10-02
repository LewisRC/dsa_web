import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Layout, Menu, Dropdown } from 'antd'
import { DownOutlined } from '@ant-design/icons'
import type { MenuProps } from 'antd'
import './Header.scss'

const { Header: AntHeader } = Layout

const Header: React.FC = () => {
  const location = useLocation()
  const [currentPath, setCurrentPath] = useState(location.pathname)

  // 产品中心下拉菜单
  const productMenuItems: MenuProps['items'] = [
    {
      key: 'intercom-products',
      label: '楼宇对讲',
      children: [
        { key: 'digital-intercom', label: <Link to="/products/digital-intercom">数字对讲</Link> },
        { key: 'analog-intercom', label: <Link to="/products/analog-intercom">模拟对讲</Link> },
        { key: 'ip-intercom', label: <Link to="/products/ip-intercom">IP对讲</Link> },
      ]
    },
    {
      key: 'smart-home',
      label: '智能家居',
      children: [
        { key: 'smart-locks', label: <Link to="/products/smart-locks">智能门锁</Link> },
        { key: 'smart-sensors', label: <Link to="/products/smart-sensors">智能传感器</Link> },
        { key: 'home-automation', label: <Link to="/products/home-automation">家居自动化</Link> },
      ]
    },
    {
      key: 'security-monitoring',
      label: '安防监控',
      children: [
        { key: 'cameras', label: <Link to="/products/cameras">监控摄像</Link> },
        { key: 'nvr-systems', label: <Link to="/products/nvr-systems">录像系统</Link> },
        { key: 'alarm-systems', label: <Link to="/products/alarm-systems">报警系统</Link> },
      ]
    },
    {
      key: 'access-control',
      label: '智慧通行',
      children: [
        { key: 'face-recognition', label: <Link to="/products/face-recognition">人脸识别</Link> },
        { key: 'card-access', label: <Link to="/products/card-access">刷卡门禁</Link> },
        { key: 'mobile-access', label: <Link to="/products/mobile-access">手机开门</Link> },
      ]
    }
  ]

  // 关于我们下拉菜单
  const aboutMenuItems: MenuProps['items'] = [
    { key: 'company-profile', label: <Link to="/about/profile">公司简介</Link> },
    { key: 'company-history', label: <Link to="/about/history">发展历程</Link> },
    { key: 'company-culture', label: <Link to="/about/culture">企业文化</Link> },
    { key: 'company-honors', label: <Link to="/about/honors">荣誉资质</Link> },
    { key: 'strategic-cooperation', label: <Link to="/about/cooperation">战略合作</Link> },
  ]

  // 解决方案下拉菜单
  const solutionMenuItems: MenuProps['items'] = [
    { key: 'smart-community', label: <Link to="/solutions/smart-community">智慧社区</Link> },
    { key: 'smart-building', label: <Link to="/solutions/smart-building">智慧楼宇</Link> },
    { key: 'smart-hospital', label: <Link to="/solutions/smart-hospital">智慧医院</Link> },
    { key: 'smart-hotel', label: <Link to="/solutions/smart-hotel">智慧酒店</Link> },
    { key: 'smart-office', label: <Link to="/solutions/smart-office">智慧办公</Link> },
  ]

  const navigationItems = [
    {
      key: '/',
      label: <Link to="/" className={currentPath === '/' ? 'nav-active' : ''}>首页</Link>
    },
    {
      key: '/about',
      label: (
        <Dropdown menu={{ items: aboutMenuItems }} trigger={['hover']} placement="bottomLeft">
          <span className={currentPath.startsWith('/about') ? 'nav-active nav-dropdown' : 'nav-dropdown'}>
            关于德视安 <DownOutlined />
          </span>
        </Dropdown>
      )
    },
    {
      key: '/products',
      label: (
        <Dropdown menu={{ items: productMenuItems }} trigger={['hover']} placement="bottomLeft">
          <span className={currentPath.startsWith('/products') ? 'nav-active nav-dropdown' : 'nav-dropdown'}>
            产品中心 <DownOutlined />
          </span>
        </Dropdown>
      )
    },
    {
      key: '/solutions',
      label: (
        <Dropdown menu={{ items: solutionMenuItems }} trigger={['hover']} placement="bottomLeft">
          <span className={currentPath.startsWith('/solutions') ? 'nav-active nav-dropdown' : 'nav-dropdown'}>
            解决方案 <DownOutlined />
          </span>
        </Dropdown>
      )
    },
    {
      key: '/news',
      label: <Link to="/news" className={currentPath === '/news' ? 'nav-active' : ''}>新闻中心</Link>
    },
    {
      key: '/cases',
      label: <Link to="/cases" className={currentPath === '/cases' ? 'nav-active' : ''}>成功案例</Link>
    },
    {
      key: '/service',
      label: <Link to="/service" className={currentPath === '/service' ? 'nav-active' : ''}>服务支持</Link>
    },
    {
      key: '/contact',
      label: <Link to="/contact" className={currentPath === '/contact' ? 'nav-active' : ''}>联系我们</Link>
    }
  ]

  return (
    <div className="dnake-header">
      <AntHeader className="dnake-main-header">
        <div className="container">
          {/* Logo */}
          <div className="logo">
            <Link to="/">
              <img src="/images/logo.png" alt="德视安" className="logo-img" />
              <span className="logo-text">德视安</span>
            </Link>
          </div>

          {/* 导航菜单 */}
          <nav className="main-navigation">
            <ul className="nav-list">
              {navigationItems.map((item) => (
                <li key={item.key} className="nav-item">
                  {item.label}
                </li>
              ))}
            </ul>
          </nav>
        </div>
      </AntHeader>
    </div>
  )
}

export default Header