import React from 'react'
import { Card, Row, Col } from 'antd'

const About: React.FC = () => {
  return (
    <div className="about-page">
      <div className="container">
        <h1>关于德视安</h1>
        <Row gutter={[24, 24]}>
          <Col xs={24} md={12}>
            <Card title="公司简介">
              <p>德视安安防科技有限公司是一家专业从事楼宇对讲、视频监控、门禁控制系统研发、生产、销售的高新技术企业。</p>
            </Card>
          </Col>
          <Col xs={24} md={12}>
            <Card title="企业文化">
              <p>以科技创新为驱动，以客户需求为导向，致力于为客户提供优质的安防解决方案。</p>
            </Card>
          </Col>
        </Row>
      </div>
    </div>
  )
}

export default About
