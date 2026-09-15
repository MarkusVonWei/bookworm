# 我的书架 - 小程序快速部署指南

## 5 分钟快速开始

### 前置准备

1. 注册微信小程序账号：https://mp.weixin.qq.com/
2. 获取 AppID
3. 安装 Node.js 16+
4. 安装微信开发者工具

### 步骤 1：初始化 Taro 项目

```bash
# 进入 bookworm 项目
cd /Users/marvin/workspace/life_project/bookworm

# 安装 Taro CLI
npm install -g @tarojs/cli

# 创建小程序项目（基于现有 Vue 代码）
taro init miniprogram --template vue --description "我的书架小程序"
```

### 步骤 2：迁移前端代码

```bash
# 复制页面组件
cp -r frontend/src/views/* miniprogram/src/pages/

# 复制工具函数
cp -r frontend/src/utils/* miniprogram/src/utils/

# 复制 API 配置（需要适配）
cp frontend/src/api/index.js miniprogram/src/api/
```

### 步骤 3：配置小程序

编辑 `miniprogram/src/app.json`：

```json
{
  "pages": [
    "pages/bookshelf/index",
    "pages/book-detail/index",
    "pages/records/index",
    "pages/my/index"
  ],
  "window": {
    "navigationBarTitleText": "我的书架",
    "navigationBarBackgroundColor": "#409EFF",
    "navigationBarTextStyle": "white"
  },
  "tabBar": {
    "color": "#999",
    "selectedColor": "#409EFF",
    "list": [
      {
        "pagePath": "pages/bookshelf/index",
        "text": "书架",
        "iconPath": "assets/tab-bookshelf.png",
        "selectedIconPath": "assets/tab-bookshelf-active.png"
      },
      {
        "pagePath": "pages/records/index",
        "text": "记录",
        "iconPath": "assets/tab-records.png",
        "selectedIconPath": "assets/tab-records-active.png"
      },
      {
        "pagePath": "pages/my/index",
        "text": "我的",
        "iconPath": "assets/tab-my.png",
        "selectedIconPath": "assets/tab-my-active.png"
      }
    ]
  }
}
```

### 步骤 4：配置服务器域名

1. 登录微信公众平台
2. 进入「开发」→「开发管理」→「开发设置」
3. 添加服务器域名：
   - request 合法域名：`https://your-server.com`
   - uploadFile 合法域名：`https://your-server.com`

### 步骤 5：本地开发

```bash
cd miniprogram
npm run dev:weapp
```

在微信开发者工具中导入项目进行调试。

### 步骤 6：上传发布

```bash
# 构建
taro build --type weapp

# 在微信开发者工具中上传
# 提交审核 → 发布
```

## 关键配置文件

### project.config.json

```json
{
  "appid": "your-appid",
  "projectname": "bookworm-miniprogram",
  "description": "我的书架小程序",
  "setting": {
    "urlCheck": true,
    "es6": true,
    "postcss": true,
    "minified": true
  },
  "compileType": "miniprogram"
}
```

### sitemap.json

```json
{
  "desc": "关于本文件的更多信息，请参考文档",
  "rules": [
    {
      "action": "allow",
      "page": "*"
    }
  ]
}
```

## 常用命令

```bash
# 本地开发
taro build --type weapp --watch

# 构建生产版本
taro build --type weapp

# 清理构建产物
rm -rf miniprogram/dist
```

## 调试技巧

### 1. 真机预览

在微信开发者工具中：
- 点击「预览」生成二维码
- 使用手机微信扫描测试

### 2. 真机调试

- 点击「真机调试」
- 可以在电脑上查看手机日志
- 支持断点调试

### 3. 性能分析

- 点击「性能」面板
- 查看启动耗时、内存占用
- 优化首屏加载时间

## 注意事项

1. **图片优化**：小程序对图片大小敏感，建议压缩后上传
2. **HTTPS 必须**：所有网络请求必须使用 HTTPS
3. **域名白名单**：服务器域名必须在微信公众平台配置
4. **代码包大小**：单个代码包最大 2MB，总大小最大 20MB
5. **审核周期**：首次审核 1-7 个工作日，加急审核 2 小时

## 下一步

1. 完成小程序开发
2. 配置 HTTPS 服务器
3. 测试所有功能
4. 提交审核
5. 发布上线

详细步骤请参考 [bookworm-deployment.md](bookworm-deployment.md)
