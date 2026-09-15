# 我的书架 - 微信小程序发布指南

## 概述

本文档描述如何将 bookworm（我的书架）Web 应用发布到微信小程序平台。

## 技术方案

### 推荐方案：Taro 跨端框架

使用 Taro 将现有 Vue.js 代码编译为微信小程序，实现一套代码多端运行。

**技术栈**：
- 前端框架：Vue 3 + Taro
- 后端：FastAPI（已有）
- 数据库：SQLite（已有）

## 发布流程

### 阶段一：准备（1-2 天）

1. **注册微信小程序账号**
   - 访问 https://mp.weixin.qq.com/
   - 注册小程序账号
   - 获取 AppID

2. **安装开发工具**
   - 安装微信开发者工具
   - 安装 Taro CLI

3. **配置服务器**
   - 申请 SSL 证书
   - 配置 HTTPS
   - 在微信公众平台配置服务器域名

### 阶段二：开发（3-5 天）

1. **初始化 Taro 项目**
   ```bash
   taro init miniprogram --template vue
   ```

2. **迁移前端代码**
   - 迁移页面组件
   - 迁移 API 调用
   - 迁移样式和工具函数

3. **适配小程序限制**
   - 网络请求（HTTPS）
   - 文件上传（10MB 限制）
   - 本地存储（10MB 限制）

4. **开发测试**
   - 本地开发调试
   - 真机测试
   - 性能优化

### 阶段三：发布（1-2 天）

1. **上传代码**
   ```bash
   taro build --type weapp
   ```

2. **提交审核**
   - 选择服务类目：工具 → 信息查询
   - 配置功能页面
   - 提交审核

3. **发布上线**
   - 审核通过后发布
   - 生成小程序码

## 关键配置

### 服务器域名配置

在微信公众平台配置：
- request 合法域名
- uploadFile 合法域名
- downloadFile 合法域名

### 服务类目选择

推荐选择：**工具 → 信息查询**

### 隐私协议配置

在微信公众平台配置用户隐私保护指引。

## 常见问题

### Q: 审核需要多长时间？

A: 普通审核 1-7 个工作日，加急审核 2 小时内（需付费）。

### Q: 个人号可以发布吗？

A: 可以，但功能受限（无法使用微信支付等高级能力）。

### Q: 如何实现用户登录？

A: 使用微信登录流程：wx.login() → 后端换取 openid → 创建用户。

### Q: 文件上传大小限制？

A: 微信小程序文件上传最大 10MB。

## 参考资源

- [微信小程序官方文档](https://developers.weixin.qq.com/miniprogram/dev/framework/)
- [Taro 官方文档](https://taro.jd.com/)
- [bookworm-deployment.md](../wechat-miniprogram/references/bookworm-deployment.md) - 详细部署指南
- [bookworm-quick-start.md](../wechat-miniprogram/references/bookworm-quick-start.md) - 快速开始指南
