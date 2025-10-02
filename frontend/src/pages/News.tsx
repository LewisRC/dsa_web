import React from 'react'
import { Card, Row, Col, Tag } from 'antd'

const News: React.FC = () => {
  return (
    <div className="news-page">
      <div className="container">
        <h1>新闻中心</h1>
        <Row gutter={[24, 24]}>
          <Col xs={24} md={8}>
            <Card
              hoverable
              cover={<img alt="新闻1" src="/images/pic3.png" />}
            >
              <Card.Meta 
                title="德视安新品发布会成功举办" 
                description={
                  <div>
                    <p>公司最新研发的智能对讲系统正式发布...</p>
                    <Tag color="blue">公司动态</Tag>
                  </div>
                }
              />
            </Card>
          </Col>
        </Row>
      </div>
    </div>
  )
}

export default News
