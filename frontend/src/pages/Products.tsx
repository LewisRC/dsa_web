import React from 'react'
import { Card, Row, Col, Tabs } from 'antd'

const Products: React.FC = () => {
  return (
    <div className="products-page">
      <div className="container">
        <h1>产品中心</h1>
        <Tabs defaultActiveKey="1">
          <Tabs.TabPane tab="楼宇对讲" key="1">
            <Row gutter={[24, 24]}>
              <Col xs={24} sm={12} md={8}>
                <Card
                  hoverable
                  cover={<img alt="数字对讲" src="/images/pic1.png" />}
                >
                  <Card.Meta title="数字对讲系统" description="高清音视频通话，支持远程开锁" />
                </Card>
              </Col>
            </Row>
          </Tabs.TabPane>
          <Tabs.TabPane tab="视频监控" key="2">
            <Row gutter={[24, 24]}>
              <Col xs={24} sm={12} md={8}>
                <Card
                  hoverable
                  cover={<img alt="监控摄像头" src="/images/pic2.png" />}
                >
                  <Card.Meta title="高清摄像头" description="4K超高清监控，夜视功能" />
                </Card>
              </Col>
            </Row>
          </Tabs.TabPane>
        </Tabs>
      </div>
    </div>
  )
}

export default Products
