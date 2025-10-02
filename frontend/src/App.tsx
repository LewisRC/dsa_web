import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Layout } from 'antd'
import Header from './components/Layout/Header'
import Footer from './components/Layout/Footer'
import Home from './pages/Home'
import Products from './pages/Products'
import About from './pages/About'
import News from './pages/News'
import Solutions from './pages/Solutions'
import Contact from './pages/Contact'

const { Content } = Layout

function App() {
  return (
    <Layout className="app-layout">
      <Header />
      <Content className="app-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<Products />} />
          <Route path="/about" element={<About />} />
          <Route path="/news" element={<News />} />
          <Route path="/solutions" element={<Solutions />} />
          <Route path="/contact" element={<Contact />} />
        </Routes>
      </Content>
      <Footer />
    </Layout>
  )
}

export default App