# 我的书架 - MVP 实现总结

> 更新日期: 2026-09-29

---

## 项目概述

**我的书架 (dog-ear)** — 智能阅读管理应用，基于 uni-app 跨平台架构，支持 H5 和微信小程序。

**核心价值**: 把读过的，变成看得见的自己。

---

## 技术架构

```
┌─────────────────────────────────────────────┐
│                   客户端                     │
│  ┌─────────────┐    ┌─────────────────────┐ │
│  │   H5 Web    │    │  微信小程序          │ │
│  │  (uni-app)  │    │  (uni-app 编译)     │ │
│  └──────┬──────┘    └──────────┬──────────┘ │
│         └──────────┬───────────┘            │
│                    ▼                        │
│            ┌──────────────┐                 │
│            │  统一 API 层  │                 │
│            │ X-User-Id    │                 │
│            └──────┬───────┘                 │
└───────────────────┼─────────────────────────┘
                    ▼
┌─────────────────────────────────────────────┐
│               后端 (FastAPI)                 │
│  ┌─────────┐ ┌──────────┐ ┌──────────────┐ │
│  │ User API│ │ Book API │ │ Recognize API│ │
│  └────┬────┘ └────┬─────┘ └──────┬───────┘ │
│       └───────────┼──────────────┘          │
│                   ▼                         │
│  ┌──────────────────────────────────────┐   │
│  │          BookshelfService            │   │
│  └──────────────────┬───────────────────┘   │
│                     ▼                       │
│  ┌─────────┐  ┌───────────┐  ┌───────────┐ │
│  │ SQLite  │  │ 豆瓣 API  │  │ MiMo VLM  │ │
│  └─────────┘  └───────────┘  └───────────┘ │
└─────────────────────────────────────────────┘
```

---

## 功能清单

### ✅ 已完成功能

#### 用户体系
- [x] 匿名用户（设备指纹识别）
- [x] 手机号注册
- [x] 登录/退出
- [x] 用户验证（启动时）
- [x] 账号升级（匿名 → 正式）

#### 书籍管理
- [x] 拍照识别添加
- [x] 相册选择添加
- [x] 搜索添加（豆瓣外部目录）
- [x] 手动编辑信息
- [x] 删除书籍
- [x] 封面展示（图片/占位色）

#### 书架功能
- [x] 书籍网格展示
- [x] 状态筛选（想读/在读/已读）
- [x] 搜索（客户端 + 服务端）
- [x] 状态统计
- [x] 下拉刷新

#### 阅读记录
- [x] 添加记录（内容/摘录/页码/标签）
- [x] 记录列表
- [x] 时间线（按日期分组）
- [x] 里程碑事件（加入/开始/完成）

#### 统计与展示
- [x] 阅读统计（总数、分类）
- [x] 状态书籍列表
- [x] 书籍详情页

---

## API 接口

### 用户
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/user/init` | 初始化匿名用户 |
| POST | `/api/user/register-with-device` | 注册 |
| POST | `/api/user/login` | 登录 |
| GET | `/api/user/me` | 获取当前用户 |

### 书籍
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/bookshelf/books` | 获取书籍列表 |
| POST | `/api/bookshelf/books` | 添加书籍 |
| GET | `/api/bookshelf/books/:id` | 获取详情 |
| PUT | `/api/bookshelf/books/:id` | 更新书籍 |
| DELETE | `/api/bookshelf/books/:id` | 删除书籍 |
| PUT | `/api/bookshelf/books/:id/status` | 更新状态 |

### 记录
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/bookshelf/books/:id/records` | 获取记录 |
| POST | `/api/bookshelf/books/:id/records` | 添加记录 |
| GET | `/api/bookshelf/records` | 所有记录 |
| GET | `/api/bookshelf/timeline` | 时间线 |

### 其他
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/bookshelf/recognize` | 识别书籍 |
| GET | `/api/bookshelf/search` | 搜索自己的书 |
| GET | `/api/bookshelf/search-external` | 搜索外部目录 |
| GET | `/api/bookshelf/statistics` | 统计信息 |

---

## 项目结构

```
bookworm/
├── uniapp/                        # uni-app 前端 (主要)
│   ├── src/
│   │   ├── api/index.js          # 统一 API
│   │   ├── composables/          # useUser, useToast
│   │   ├── utils/                # device, date, coverColor
│   │   └── pages/                # 6 页面
│   └── dist/build/mp-weixin/     # 小程序产物
│
├── src/bookworm/                  # 后端源码
│   ├── api/                      # FastAPI 应用
│   │   ├── app.py                # 主应用
│   │   └── rate_limit.py         # 限流
│   └── bookshelf/                # 书架模块
│       ├── api.py                # API 路由
│       ├── models.py             # 数据模型
│       ├── service.py            # 业务逻辑
│       ├── recognition.py        # 书籍识别
│       └── user_service.py       # 用户服务
│
├── frontend/                      # 旧 Vue.js 前端
├── frontend_backup_20260928/      # 备份
├── miniprogram/                   # 旧原生小程序
├── miniprogram_backup_20260928/   # 备份
│
└── docs/                          # 文档
    ├── miniprogram-troubleshooting.md
    └── deployment.md
```

---

## Bug 修复记录 (17 项)

| # | Bug | 根因 | 修复 |
|---|-----|------|------|
| 1 | baseUrl 为空 | getApp() 时序 | init(app) |
| 2 | onLaunch 崩溃 | getApp() 未就绪 | 传 this |
| 3 | 域名非法 | 工具缓存 | 手动刷新 |
| 4 | 用户缓存失效 | 未验证 | /user/me |
| 5 | X-User-Id 竞态 | 异步 globalData | getStorageSync |
| 6 | updateBookStatus 422 | body vs query | query 参数 |
| 7 | 时间线事件错误 | type 模型错 | milestone 区分 |
| 8 | WXML 方法空白 | 模板限制 | 预计算 |
| 9 | goBack 缺失 | 未定义 | navigateBack |
| 10 | 封面色硬编码 | 未用 hash | getCoverColor |
| 11 | 日期原始格式 | 未格式化 | formatDateTime |
| 12 | page_number 422 | 空字符串 | validator |
| 13 | 搜索自己书架 | API 范围 | 外部搜索 |
| 14 | 无登录 UI | 未实现 | profile 页 |
| 15 | WXSS 转义错误 | 中文类名 | 英文类名 |
| 16 | input 截断 | 无 height | height:44px |
| 17 | 图片相对路径 | 小程序限制 | resolveImageUrl |

---

## 经验教训

1. **uni-app CSS 类名必须 ASCII** — 中文类名被转为 Unicode 转义导致 WXSS 编译失败
2. **小程序 input 必须显式 height** — padding 不能撑开高度，文字会截断
3. **getApp() 有时序限制** — onLaunch 中不可用，需传 this
4. **API 参数位置要对齐** — FastAPI query vs body，前后端约定一致
5. **外部搜索 vs 内部搜索** — 语义不同，需区分 API

---

## 测试验证

| 测试项 | 状态 | 说明 |
|--------|------|------|
| 外部搜索 | ✅ | 豆瓣 suggest API |
| 注册 | ✅ | 手机号 + 密码 |
| 登录 | ✅ | 返回用户信息 |
| 创建书籍 | ✅ | 含状态 |
| page_number 空字符串 | ✅ | 正确返回 null |
| 书籍识别 | 🔄 | 待真机测试 |
| UI 显示 | 🔄 | 待真机测试 |

---

## 部署信息

| 项目 | 值 |
|------|-----|
| 后端 | `https://www.bookworm.icu` |
| 服务器 | 124.220.45.149 (ubuntu) |
| 路径 | `~/workspace/bookshelf` |
| 启动 | `bash run.sh` |
| 小程序 AppID | `wx102d18424fb612c2` |
| 小程序导入 | `uniapp/dist/build/mp-weixin` |
