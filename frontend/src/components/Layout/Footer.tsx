import React from 'react'
import { Layout } from 'antd'
import './Footer.scss'

const { Footer: AntFooter } = Layout

const Footer: React.FC = () => {
  return (
    <AntFooter className="app-footer">
      <div className="container">
        <div className="footer-content">
          <div className="footer-info">
            <h3>德视安安防科技有限公司</h3>
            <p>专业的楼宇对讲、视频监控、门禁控制系统制造商</p>
          </div>
          <div className="footer-links">
            <div className="link-group">
              <h4>产品中心</h4>
              <ul>
                <li>楼宇对讲</li>
                <li>视频监控</li>
                <li>门禁控制</li>
              </ul>
            </div>
            <div className="link-group">
              <h4>解决方案</h4>
              <ul>
                <li>智慧社区</li>
                <li>智慧楼宇</li>
                <li>智慧停车</li>
              </ul>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2024 德视安安防科技有限公司. 版权所有</p>
        </div>
      </div>
    </AntFooter>
  )
}

export default Footer
