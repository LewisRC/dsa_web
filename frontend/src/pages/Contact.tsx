import React from 'react'
import { Card, Form, Input, Button, Row, Col } from 'antd'

const Contact: React.FC = () => {
  const onFinish = (values: any) => {
    console.log('表单提交:', values)
  }

  return (
    <div className="contact-page">
      <div className="container">
        <h1>联系我们</h1>
        <Row gutter={[24, 24]}>
          <Col xs={24} md={12}>
            <Card title="联系信息">
              <p><strong>公司地址：</strong>深圳市南山区科技园</p>
              <p><strong>联系电话：</strong>400-123-4567</p>
              <p><strong>邮箱：</strong>info@deshian.com</p>
            </Card>
          </Col>
          <Col xs={24} md={12}>
            <Card title="在线咨询">
              <Form onFinish={onFinish} layout="vertical">
                <Form.Item name="name" label="姓名" rules={[{ required: true }]}>
                  <Input />
                </Form.Item>
                <Form.Item name="phone" label="电话" rules={[{ required: true }]}>
                  <Input />
                </Form.Item>
                <Form.Item name="message" label="留言">
                  <Input.TextArea rows={4} />
                </Form.Item>
                <Form.Item>
                  <Button type="primary" htmlType="submit">提交</Button>
                </Form.Item>
              </Form>
            </Card>
          </Col>
        </Row>
      </div>
    </div>
  )
}

export default Contact
