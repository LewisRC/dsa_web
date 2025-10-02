import React, { useState } from 'react'
import { Row, Col, Card, Button, Carousel, Statistic } from 'antd'
import { ArrowRightOutlined, SafetyOutlined, TeamOutlined, TrophyOutlined, GlobalOutlined } from '@ant-design/icons'

const Home: React.FC = () => {
  const [currentSlide, setCurrentSlide] = useState(0);

  const handleSlideChange = (current: number) => {
    setCurrentSlide(current);
  };
  const carouselItems = [
    {
      id: 1,
      title: '德视安智慧安防解决方案',
      subtitle: '专业的楼宇对讲、视频监控、门禁控制系统制造商',
      description: '围绕智慧社区和智慧楼宇领域，通过不断的技术创新、产品升级和功能优化',
      image: '/images/pic1.png',
      buttonText: '了解更多'
    },
    {
      id: 2,
      title: '创新科技 安全守护',
      subtitle: '领先的安防技术与产品',
      description: '为客户提供高品质、高可靠性的安防产品与服务',
      image: '/images/pic2.png',
      buttonText: '产品中心'
    },
    {
      id: 3,
      title: '智慧社区 美好生活',
      subtitle: '构建智能化社区生态',
      description: '通过先进的物联网技术，打造安全、便捷的智慧社区',
      image: '/images/pic3.png',
      buttonText: '解决方案'
    }
  ]

  const productCategories = [
    {
      title: '楼宇对讲',
      description: '数字化对讲系统，支持视频通话、门禁控制',
      image: '/images/pic4.png',
      link: '/products/intercom'
    },
    {
      title: '智能家居',
      description: '智能门锁、传感器、家居自动化系统',
      image: '/images/pic5.png',
      link: '/products/smart-home'
    },
    {
      title: '安防监控',
      description: '高清网络摄像机、智能分析、云端存储',
      image: '/images/pic6.png',
      link: '/products/security'
    },
    {
      title: '智慧通行',
      description: '人脸识别、刷卡门禁、手机开门系统',
      image: '/images/pic8.png',
      link: '/products/access'
    }
  ]

  const solutions = [
    {
      icon: <SafetyOutlined />,
      title: '智慧社区',
      description: '集成楼宇对讲、视频监控、门禁控制等多种安防设备'
    },
    {
      icon: <TeamOutlined />,
      title: '智慧楼宇',
      description: '为商业楼宇提供完整的安防解决方案'
    },
    {
      icon: <TrophyOutlined />,
      title: '智慧医院',
      description: '医护对讲、病房管理、安全监控系统'
    },
    {
      icon: <GlobalOutlined />,
      title: '智慧酒店',
      description: '客房控制、访客管理、安全防护系统'
    }
  ]

  const stats = [
    { title: '服务客户', value: 10000, suffix: '+' },
    { title: '项目案例', value: 5000, suffix: '+' },
    { title: '技术专利', value: 200, suffix: '+' },
    { title: '服务网点', value: 500, suffix: '+' }
  ]

  return (
    <div className="dnake-home">
      {/* 轮播图 */}
      <section className="hero-banner">
        <Carousel 
          autoplay 
          autoplaySpeed={6000}
          effect="fade" 
          className="banner-carousel"
          dots={true}
          arrows={true}
          pauseOnHover={false}
          afterChange={handleSlideChange}
        >
          {carouselItems.map((item, index) => (
            <div key={item.id} className="banner-slide">
              <div className="banner-background">
                <img 
                  src={item.image} 
                  alt={item.title} 
                  className={`background-image ${currentSlide === index ? 'active' : ''}`}
                />
              </div>
              <div className="container">
                <div className="banner-content">
                  <div className={`banner-text ${currentSlide === index ? 'active' : ''}`}>
                    <h1 className="banner-title">{item.title}</h1>
                    <h2 className="banner-subtitle">{item.subtitle}</h2>
                    <p className="banner-description">{item.description}</p>
                    <Button type="primary" size="large" className="banner-btn">
                      {item.buttonText} <ArrowRightOutlined />
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </Carousel>
      </section>

      {/* 产品分类 */}
      <section className="product-categories">
        <div className="container">
          <div className="section-header">
            <h2>产品中心</h2>
            <p>专业的安防产品，为您提供全方位的安全保障</p>
          </div>
          <Row gutter={[24, 24]}>
            {productCategories.map((product, index) => (
              <Col xs={24} sm={12} lg={6} key={index}>
                <Card 
                  className="product-category-card" 
                  hoverable
                  cover={<img alt={product.title} src={product.image} />}
                >
                  <h3>{product.title}</h3>
                  <p>{product.description}</p>
                  <Button type="link" className="learn-more">
                    了解更多 <ArrowRightOutlined />
                  </Button>
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      </section>

      {/* 解决方案 */}
      <section className="solutions-section">
        <div className="container">
          <div className="section-header">
            <h2>解决方案</h2>
            <p>为不同行业提供专业的安防解决方案</p>
          </div>
          <Row gutter={[32, 32]}>
            {solutions.map((solution, index) => (
              <Col xs={24} sm={12} lg={6} key={index}>
                <Card className="solution-card" hoverable>
                  <div className="solution-icon">{solution.icon}</div>
                  <h3>{solution.title}</h3>
                  <p>{solution.description}</p>
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      </section>

      {/* 统计数据 */}
      <section className="stats-section">
        <div className="container">
          <Row gutter={[32, 32]}>
            {stats.map((stat, index) => (
              <Col xs={12} sm={6} key={index}>
                <div className="stat-item">
                  <Statistic
                    title={stat.title}
                    value={stat.value}
                    suffix={stat.suffix}
                    valueStyle={{ 
                      color: '#1890ff', 
                      fontSize: '48px', 
                      fontWeight: 'bold',
                      lineHeight: 1
                    }}
                  />
                </div>
              </Col>
            ))}
          </Row>
        </div>
      </section>

      {/* 新闻资讯 */}
      <section className="news-section">
        <div className="container">
          <div className="section-header">
            <h2>新闻中心</h2>
            <p>了解德视安最新动态和行业资讯</p>
          </div>
          <Row gutter={[24, 24]}>
            <Col xs={24} md={8}>
              <Card className="news-card" hoverable>
                <div className="news-date">2024-03-15</div>
                <h3>德视安荣获2024年度安防行业创新奖</h3>
                <p>在刚刚结束的2024年安防行业大会上，德视安凭借其创新的智慧社区解决方案荣获年度创新奖...</p>
              </Card>
            </Col>
            <Col xs={24} md={8}>
              <Card className="news-card" hoverable>
                <div className="news-date">2024-03-10</div>
                <h3>德视安与华为达成战略合作协议</h3>
                <p>德视安科技与华为技术有限公司正式签署战略合作协议，双方将在智慧城市、物联网等领域展开深度合作...</p>
              </Card>
            </Col>
            <Col xs={24} md={8}>
              <Card className="news-card" hoverable>
                <div className="news-date">2024-03-05</div>
                <h3>德视安新一代AI智能分析系统正式发布</h3>
                <p>德视安最新研发的AI智能分析系统正式发布，该系统集成了人脸识别、行为分析、异常检测等多项功能...</p>
              </Card>
            </Col>
          </Row>
          <div className="section-footer">
            <Button type="primary" size="large">
              查看更多新闻 <ArrowRightOutlined />
            </Button>
          </div>
        </div>
      </section>
    </div>
  )
}

export default Home