import React from 'react'
import { Card, Row, Col } from 'antd'

const Solutions: React.FC = () => {
  return (
    <div className="solutions-page">
      <div className="container">
        <h1>解决方案</h1>
        <Row gutter={[24, 24]}>
          <Col xs={24} md={8}>
            <Card
              hoverable
              cover={<img alt="智慧社区" src="/images/pic4.png" />}
            >
              <Card.Meta title="智慧社区解决方案" description="打造安全、便民、智能的现代化社区" />
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card
              hoverable
              cover={<img alt="智慧楼宇" src="/images/pic5.png" />}
            >
              <Card.Meta title="智慧楼宇解决方案" description="集成化楼宇管理，提升运营效率" />
            </Card>
          </Col>
        </Row>
      </div>
    </div>
  )
}

export default Solutions
