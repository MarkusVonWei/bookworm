# 我的书架 - 微信小程序部署指南

将 bookworm（我的书架）Web 应用发布到微信小程序的完整步骤。

## 技术方案选择

### 方案一：Taro 跨端框架（推荐）

使用 Taro 将 Vue.js 代码编译为微信小程序，实现一套代码多端运行。

**优势**：
- 复用现有 Vue.js 代码
- 一套代码同时支持 Web + 小程序
- 社区活跃，文档完善

### 方案二：uni-app

使用 uni-app 框架，基于 Vue.js 开发。

**优势**：
- Vue.js 语法，学习成本低
- 微信小程序支持好
- 插件生态丰富

### 方案三：原生小程序开发

完全重写为微信小程序原生代码。

**优势**：
- 性能最优
- 完整的微信能力支持

**劣势**：
- 开发成本高
- 无法复用现有代码

## 方案一：Taro 实现步骤

### 1. 安装 Taro CLI

```bash
npm install -g @tarojs/cli
```

### 2. 初始化项目

```bash
# 在 bookworm 项目目录下
taro init miniprogram --template vue --description "我的书架小程序"
```

### 3. 迁移现有代码

#### 3.1 迁移页面组件

将 `frontend/src/views/` 下的 Vue 组件迁移到 Taro 项目：

```bash
# 迁移文件
Bookshelf.vue → pages/bookshelf/
BookDetail.vue → pages/book-detail/
Records.vue → pages/records/
My.vue → pages/my/
```

#### 3.2 迁移 API 调用

修改 `frontend/src/api/index.js`，适配小程序环境：

```javascript
// 原来的 axios 调用
import axios from 'axios'

// 改为 Taro.request
import Taro from '@tarojs/taro'

const api = {
  get: (url, params) => Taro.request({
    url: `${BASE_URL}${url}`,
    method: 'GET',
    data: params
  }),
  post: (url, data) => Taro.request({
    url: `${BASE_URL}${url}`,
    method: 'POST',
    data
  })
}
```

#### 3.3 迁移路由配置

修改 `app.json` 配置页面路由：

```json
{
  "pages": [
    "pages/bookshelf/index",
    "pages/book-detail/index",
    "pages/records/index",
    "pages/my/index"
  ],
  "tabBar": {
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

### 4. 处理小程序限制

#### 4.1 网络请求

小程序网络请求必须是 HTTPS，且需要在后台配置服务器域名：

1. 登录微信公众平台
2. 进入「开发」→「开发管理」→「开发设置」
3. 在「服务器域名」中添加：
   - request 合法域名：`https://your-server.com`
   - uploadFile 合法域名：`https://your-server.com`
   - downloadFile 合法域名：`https://your-server.com`

#### 4.2 本地存储

小程序本地存储使用 `wx.setStorageSync` / `wx.getStorageSync`：

```javascript
// 替换 localStorage
Taro.setStorageSync('key', 'value')
const value = Taro.getStorageSync('key')
```

#### 4.3 文件上传

小程序文件上传使用 `wx.chooseImage` + `wx.uploadFile`：

```javascript
// 选择图片
const res = await Taro.chooseImage({
  count: 1,
  sizeType: ['compressed'],
  sourceType: ['album', 'camera']
})

// 上传图片
const uploadRes = await Taro.uploadFile({
  url: `${BASE_URL}/api/bookshelf/recognize`,
  filePath: res.tempFilePaths[0],
  name: 'file'
})
```

### 5. 配置 HTTPS 服务器

#### 5.1 申请 SSL 证书

1. 购买域名
2. 申请 SSL 证书（可使用免费的 Let's Encrypt）
3. 配置服务器 HTTPS

#### 5.2 配置服务器域名

在微信公众平台配置：
- request 合法域名
- uploadFile 合法域名
- downloadFile 合法域名

### 6. 开发调试

#### 6.1 本地开发

```bash
cd miniprogram
npm run dev:weapp
```

在微信开发者工具中导入项目，进行调试。

#### 6.2 真机调试

1. 在开发者工具中点击「真机调试」
2. 使用手机微信扫描二维码
3. 在真机上测试功能

### 7. 上传与发布

#### 7.1 上传代码

```bash
# 在 Taro 项目目录
taro build --type weapp
```

然后在微信开发者工具中：
1. 点击「上传」
2. 填写版本号（如 1.0.0）
3. 填写项目备注

#### 7.2 提交审核

1. 登录微信公众平台
2. 进入「管理」→「版本管理」
3. 找到上传的版本
4. 点击「提交审核」
5. 填写审核信息：
   - 选择服务类目：工具 → 信息查询
   - 配置功能页面
   - 提供测试账号（如需要）

#### 7.3 发布上线

审核通过后：
1. 在「版本管理」中点击「全量发布」
2. 小程序正式上线

## 后端适配

### 1. 启用 HTTPS

```bash
# 使用 Nginx 配置 SSL
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. 配置 CORS

在 FastAPI 中配置 CORS：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. 文件存储

小程序上传的文件需要存储到云服务：

```python
# 使用阿里云 OSS
import oss2

auth = oss2.Auth(access_key_id, access_key_secret)
bucket = oss2.Bucket(auth, endpoint, bucket_name)

# 上传文件
bucket.put_object(key, file_data)
```

## 常见问题

### Q: 为什么我的小程序无法调用后端 API？

A: 检查以下几点：
1. 服务器域名是否配置正确
2. 是否使用 HTTPS
3. CORS 配置是否允许小程序域名

### Q: 小程序文件上传大小限制是多少？

A: 微信小程序文件上传最大 10MB，建议图片压缩后上传。

### Q: 如何实现用户登录？

A: 使用微信登录流程：
1. 调用 `wx.login()` 获取 code
2. 将 code 发送到后端
3. 后端调用微信接口换取 openid
4. 创建或查找用户记录
5. 返回 token 给小程序

### Q: 如何处理小程序分享？

A: 使用 `onShareAppMessage` 生命周期：

```javascript
Page({
  onShareAppMessage() {
    return {
      title: '我的书架 - 记录你的阅读时光',
      path: '/pages/bookshelf/index'
    }
  }
})
```

## 测试清单

- [ ] 所有页面功能正常
- [ ] 网络请求正常（HTTPS）
- [ ] 文件上传正常
- [ ] 本地存储正常
- [ ] 分享功能正常
- [ ] 真机测试通过
- [ ] 性能优化（首屏加载 < 2s）
- [ ] 隐私协议配置
- [ ] 服务类目选择正确
