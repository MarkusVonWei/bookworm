# 我的书架 - 项目现状与排期

> 更新日期: 2026-09-29

---

## 一、项目现状总览

| 维度 | 状态 | 说明 |
|------|------|------|
| **后端 API** | ✅ 已上线 | `https://www.bookworm.icu` 运行中 |
| **uni-app 前端** | ✅ 完成开发 | 6 页面，H5 + 微信小程序双端 |
| **数据库** | ✅ 运行中 | SQLite，支持多用户 |
| **域名/HTTPS** | ✅ 已配置 | bookworm.icu + SSL 证书 |
| **微信小程序** | ✅ 可导入 | `uniapp/dist/build/mp-weixin` |

---

## 二、本次会话完成的工作

### 1. 后端修复与增强

| 项目 | 状态 | 文件 |
|------|------|------|
| X-Forwarded-For 伪造防护 | ✅ | `api/rate_limit.py` |
| 内存泄漏修复 (IP 清理) | ✅ | `api/rate_limit.py` |
| GET/POST 分离限流 | ✅ | `api/rate_limit.py` |
| 重复日志 handler 修复 | ✅ | `bookshelf/recognition.py` |
| `content_type` None 崩溃修复 | ✅ | `bookshelf/api.py` |
| `page_number` 空字符串 coercion | ✅ | `bookshelf/api.py` (validator) |
| **外部书籍搜索 API** (新增) | ✅ | `/api/bookshelf/search-external` |
| 豆瓣多结果搜索函数 (新增) | ✅ | `bookshelf/recognition.py` |

### 2. uni-app 前端（全新实现）

| 页面 | 状态 | 功能 |
|------|------|------|
| `bookshelf` | ✅ | 书籍网格、状态筛选、搜索、下拉刷新 |
| `book-detail` | ✅ | 详情、状态切换、阅读记录、删除 |
| `records` | ✅ | 时间线（按日期分组）、里程碑/记录区分 |
| `my` | ✅ | 统计、状态书籍列表、个人中心入口 |
| `add-book` | ✅ | 拍照/相册/搜索添加、表单完善 |
| `profile` | ✅ | 登录/注册/退出（新增） |

| 模块 | 状态 | 说明 |
|------|------|------|
| API 层 | ✅ | 统一 X-User-Id、错误处理、30s 超时 |
| useUser | ✅ | 初始化/验证/注册/登录/重置 |
| useToast | ✅ | 跨平台 toast 封装 |
| device.js | ✅ | 设备指纹（H5 + 小程序） |
| date.js | ✅ | 日期格式化 |
| coverColor.js | ✅ | 封面色 hash + URL 解析 |

### 3. Bug 修复记录

| Bug | 原因 | 修复 |
|-----|------|------|
| `baseUrl` 为空 | `getApp()` 在模块加载时 undefined | `init(app)` + `ensureInit()` |
| `onLaunch` 中 getApp() 报错 | App 实例未就绪 | 传 `this` 给 `api.init()` |
| 域名「非法」 | 开发者工具缓存 | 手动刷新域名配置 |
| 缓存用户失效未清理 | 未验证 userId | 启动时调 `/user/me` 验证 |
| X-User-Id 竞态条件 | globalData 异步为空 | `getStorageSync` 同步读取 |
| `updateBookStatus` 422 | body vs query 参数 | 改为 query 参数 |
| 时间线事件模型错误 | `type` 当作 milestone | `type==='milestone'` + `milestone` |
| WXML 方法调用空白 | 模板不能调 Page 方法 | 预计算到 data |
| `goBack` 处理器缺失 | 未定义 | 添加 `wx.navigateBack()` |
| 封面色硬编码 | 未用 hash 函数 | `getCoverColor()` |
| 日期显示原始 ISO | 未格式化 | `formatDateTime()` |
| `page_number` 空字符串 422 | `''` 不能转 int | 后端 validator + 前端处理 |
| 搜索添加搜自己的书架 | API 是 user-scoped | 新增外部搜索 API |
| 注册/登录无 UI | 未实现 | 新建 profile 页面 |
| WXSS Unicode 转义错误 | CSS 类名用中文 | 改英文类名 + 映射函数 |
| input 文字垂直截断 | 未设 height | 显式 `height: 44px` |
| `image_url` 相对路径 | 小程序不能解析 | `resolveImageUrl()` 前缀 |
| `healthCheck` 路径错误 | `/api/health` vs `/health` | 修正路径 |

### 4. 架构改进

| 项目 | 改进 |
|------|------|
| 代码组织 | 旧代码备份 (`*_backup_20260928/`) |
| 跨平台统一 | uni-app 一套代码 → H5 + 小程序 |
| API 约定 | 统一 X-User-Id header、query vs body |
| 错误处理 | `err.statusCode` 区分网络错误/业务错误 |
| 用户体系 | 匿名→注册→登录完整流程 |

---

## 三、排期表

### Phase 1: MVP 核心功能 ✅ 已完成

| 功能 | 状态 | 备注 |
|------|------|------|
| 书籍管理（添加/识别/删除） | ✅ | 拍照/相册/搜索添加 |
| 书架展示 | ✅ | 网格布局，状态筛选 |
| 阅读状态管理 | ✅ | 想读/在读/已读 |
| 书籍详情 | ✅ | 元信息、简介、封面 |
| 阅读记录 | ✅ | 内容/摘录/页码/标签 |
| 时间线 | ✅ | 按日期分组 |
| 统计信息 | ✅ | 总数、分类统计 |
| 底部导航 | ✅ | 书架/记录/我的 |
| 用户体系 | ✅ | 匿名/注册/登录 |
| 外部搜索添加 | ✅ | 豆瓣 suggest API |

### Phase 2: 重要加分功能 🔄 进行中

| 功能 | 状态 | 备注 |
|------|------|------|
| 搜索自己的书 | ✅ | 客户端 + 服务端搜索 |
| 标签系统 | ✅ | 阅读记录支持标签 |
| 阅读统计 | ✅ | 基础统计已有 |
| 阅读时间轴 | ✅ | 里程碑 + 记录 |
| ~~年度阅读报告~~ | ⬜ | P3 |
| ~~分享书架~~ | ⬜ | P3 |

### Phase 3: 可选功能 ⬜ 未开始

| 功能 | 优先级 | 预估工时 |
|------|--------|----------|
| 年度阅读报告 | P3 | 3 天 |
| 分享书架 | P3 | 2 天 |
| AI 总结阅读记录 | P3 | 3 天 |
| 用户评分 (user_rating) | P2 | 1 天 |
| 完整书单页（翻页/排序） | P2 | 2 天 |
| 登录后数据同步 | P2 | 2 天 |

---

## 四、待办事项 (TODO)

### 高优先级 (P0)

- [ ] **微信小程序真机测试** — 导入 `dist/build/mp-weixin` 验证全部功能
- [ ] **图片上传域名配置** — 小程序后台 uploadFile 合法域名
- [ ] **识别功能测试** — 拍照识别 → 添加书籍完整流程

### 中优先级 (P1)

- [ ] **输入框高度复查** — 所有表单页面在真机上验证
- [ ] **H5 端测试** — `npm run dev:h5` 验证 Web 端功能
- [ ] **封面图显示** — 识别后封面 URL 正确显示
- [ ] **错误提示优化** — 网络错误、限流等场景友好提示

### 低优先级 (P2)

- [ ] **用户评分 UI** — 后端已支持 `user_rating`，缺前端
- [ ] **完整书单页** — 书籍翻页、排序、筛选
- [ ] **数据同步** — 登录后跨设备同步书架
- [ ] **下拉刷新优化** — 骨架屏、加载动画

### 已知限制

| 限制 | 说明 | 影响 |
|------|------|------|
| 搜索添加只查豆瓣 | 无 Google Books/Open Library 搜索 | 英文书搜索覆盖有限 |
| 匿名用户无跨设备同步 | 换设备书架丢失 | 需注册账号 |
| 识别依赖 MiMo VLM | API 可能超时/限流 | 识别失败需手动输入 |
| 封面图相对路径 | 后端返回 `/data/uploads/...` | 已用 `resolveImageUrl()` 处理 |

---

## 五、技术债务

| 项目 | 严重程度 | 说明 |
|------|----------|------|
| 密码哈希 (SHA256+静态盐) | 中 | 生产环境应换 bcrypt |
| N+1 查询 (records_count) | 低 | 书籍列表时逐条查记录数 |
| 无分页 | 低 | 书籍多时加载慢 |
| 无离线缓存 | 低 | 无网时无法使用 |
| 测试覆盖不足 | 中 | 缺自动化测试 |

---

## 六、文件结构

```
bookworm/
├── uniapp/                    # uni-app 跨平台前端 (新)
│   ├── src/
│   │   ├── api/index.js      # 统一 API 层
│   │   ├── composables/      # useUser, useToast
│   │   ├── utils/            # device, date, coverColor
│   │   └── pages/            # 6 个页面
│   └── dist/build/mp-weixin/ # 小程序构建产物
├── frontend/                  # 旧 Vue.js 前端
├── frontend_backup_20260928/  # 备份
├── miniprogram/               # 旧原生小程序
├── miniprogram_backup_20260928/ # 备份
├── src/bookworm/              # 后端源码
└── docs/                      # 文档
```

---

## 七、下一步行动

1. **立即**: 打开微信开发者工具，导入 `uniapp/dist/build/mp-weixin` 真机测试
2. **今天**: 修复测试中发现的问题
3. **本周**: H5 端测试 + UI 细节优化
4. **下周**: Phase 2 收尾 + Phase 3 规划
