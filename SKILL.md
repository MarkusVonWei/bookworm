# 前端开发规范 — 书虫项目

> 基于 Vue 3 + Vite + 原生 CSS 的前端工程规范。
> 兼顾工程素养（可维护、可复用、语义化）与审美素养（呼吸感、高级感、克制用色）。

---

## 1. 设计系统（Design Tokens）

**所有颜色、间距、圆角、阴影必须通过 CSS 变量引用，禁止在组件内硬编码。**

### 1.1 色彩体系

在 `frontend/src/styles/variables.css` 中统一定义，组件通过 `var(--xxx)` 引用。

| Token | 值 | 用途 |
|---|---|---|
| `--color-primary` | `#409EFF` | 主色调（按钮、高亮、链接） |
| `--color-primary-hover` | `#66B1FF` | 主色 hover |
| `--color-primary-light` | `#ECF5FF` | 主色浅底（标签背景等） |
| `--color-success` | `#67C23A` | 成功/已完成 |
| `--color-warning` | `#E6A23C` | 警告 |
| `--color-danger` | `#F56C6C` | 危险/删除 |
| `--color-text-primary` | `#1D2129` | 主文本（不用 #000） |
| `--color-text-regular` | `#4E5969` | 正文 |
| `--color-text-secondary` | `#86909C` | 辅助文本 |
| `--color-text-placeholder` | `#C0C4CC` | 占位符 |
| `--color-border` | `#E5E6EB` | 边框/分割线 |
| `--color-bg-page` | `#F7F8FA` | 页面背景（不用 #FFF） |
| `--color-bg-card` | `#FFFFFF` | 卡片背景 |
| `--color-bg-hover` | `#F2F3F5` | 悬停背景 |
| `--color-overlay` | `rgba(0, 0, 0, 0.45)` | 遮罩层 |

**规则：**
- 背景禁用纯白 `#FFFFFF`，用 `--color-bg-page`（`#F7F8FA`）或 `--color-bg-card`
- 文本禁用纯黑 `#000000`，用 `--color-text-primary`（`#1D2129`）
- 高饱和度纯色（`#FF0000`, `#0000FF`）禁止直接使用

### 1.2 间距系统（8px 网格）

| Token | 值 |
|---|---|
| `--space-xs` | `4px` |
| `--space-sm` | `8px` |
| `--space-md` | `16px` |
| `--space-lg` | `24px` |
| `--space-xl` | `32px` |
| `--space-2xl` | `48px` |

**规则：** padding / margin / gap 只能使用以上值或其组合。禁止 `13px`、`17px` 等任意值。

### 1.3 圆角

| Token | 值 |
|---|---|
| `--radius-sm` | `4px` |
| `--radius-md` | `8px` |
| `--radius-lg` | `12px` |
| `--radius-xl` | `16px` |
| `--radius-full` | `9999px` |

### 1.4 阴影（多层模拟真实光影）

| Token | 值 |
|---|---|
| `--shadow-sm` | `0 1px 2px 0 rgba(0,0,0,0.05)` |
| `--shadow-md` | `0 2px 8px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)` |
| `--shadow-lg` | `0 4px 16px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04)` |
| `--shadow-xl` | `0 8px 24px rgba(0,0,0,0.10), 0 4px 8px rgba(0,0,0,0.04)` |

**规则：** 禁止单层 `box-shadow: 0 4px 12px rgba(0,0,0,0.15)` 这种"脏阴影"。

### 1.5 过渡

| Token | 值 |
|---|---|
| `--transition-fast` | `0.15s ease-out` |
| `--transition-normal` | `0.25s ease-out` |
| `--transition-slow` | `0.35s ease-out` |

---

## 2. HTML 语义化

### 2.1 禁止 Div 地狱

- 页面骨架用 `<header>`, `<main>`, `<section>`, `<article>`, `<nav>`, `<aside>`, `<footer>`
- 列表必须用 `<ul>/<ol>` + `<li>`
- 表单必须用 `<form>`, `<label>`, `<input>`，label 的 `for` 关联 input 的 `id`
- 按钮必须用 `<button>`，禁止用 `<div @click>` 模拟按钮

### 2.2 无障碍基础

- 所有 `<img>` 必须有 `alt`（哪怕为空字符串 `alt=""`）
- 表单控件必须有关联的 `<label>`
- 交互元素必须可通过键盘操作（`tabindex`, `@keydown`）
- 颜色对比度：文本与背景对比度 >= 4.5:1

---

## 3. CSS 架构

### 3.1 样式隔离

- **必须使用 `<style scoped>`**
- 禁止 `!important`
- CSS 嵌套层级 <= 3 层
- 禁止使用深层选择器（`::v-deep` 仅在覆盖第三方组件时使用）

### 3.2 BEM 命名约定

组件内采用 BEM 变体命名，避免全局冲突：

```
.book-card {}           /* 块 */
.book-card__cover {}    /* 元素 */
.book-card--dimmed {}   /* 修饰符 */
```

### 3.3 禁止内联样式

除动态计算值（如 `transform`、拖拽位置）外，禁止 `style="..."`。

---

## 4. Vue 3 组件规范

### 4.1 Composition API Only

- 统一使用 `<script setup>` 语法
- 禁止 Options API

### 4.2 逻辑抽离（Composables）

当以下逻辑在 2 个以上组件重复出现时，必须抽为 Composable：

- 数据获取（`useFetch`）
- 表单处理
- 分页/筛选
- 日期格式化（已有 `utils/date.js`，直接复用）

### 4.3 Props 与 Emits

- Props 必须声明类型和默认值
- Emits 必须声明事件名和参数类型
- 用 `defineProps` / `defineEmits` 的类型声明语法

### 4.4 API 层封装

- 所有 HTTP 请求统一走 `src/api/index.js`
- 组件内禁止直接写 `axios.get('/api/xxx')`，必须调用 API 层函数
- API 函数按模块组织（books, records, statistics）

---

## 5. 视觉与交互审美

### 5.1 排版层级

| 层级 | 字号 | 字重 | 颜色 | 用途 |
|---|---|---|---|---|
| H1 | 24-28px | 600 | `--color-text-primary` | 页面标题 |
| H2 | 18-20px | 600 | `--color-text-primary` | 区块标题 |
| H3 | 16px | 500 | `--color-text-primary` | 卡片标题 |
| Body | 14px | 400 | `--color-text-regular` | 正文 |
| Caption | 12px | 400 | `--color-text-secondary` | 辅助说明 |

- 行高：正文 `line-height: 1.6`，标题 `line-height: 1.3`
- 字间距：标题可加 `letter-spacing: -0.01em` 增紧凑感

### 5.2 留白原则

- 卡片内部 padding >= 24px（`--space-lg`）
- 卡片之间 gap >= 24px
- 空状态 padding >= 48px（`--space-2xl`）
- 区块之间 margin >= 32px（`--space-xl`）

### 5.3 微交互

- 所有可交互元素必须有 `transition`
- Hover 效果：背景色微调 + 轻微上浮（`translateY(-2px)`），不使用生硬变色
- 按钮 hover：背景色透明度变化，不改变尺寸
- 禁止缓慢线性动画，统一用 `ease-out`

### 5.4 阴影美学

- 卡片默认使用 `--shadow-sm`
- Hover 时升级到 `--shadow-md`
- 弹窗使用 `--shadow-xl`
- 底部导航栏使用 `0 -1px 0 var(--color-border)` 而非重阴影

---

## 6. 绝对禁止（Anti-Patterns）

| 反模式 | 说明 |
|---|---|
| 硬编码色值 | `color: #333` → `color: var(--color-text-primary)` |
| 硬编码间距 | `padding: 13px` → `padding: var(--space-md)` |
| 硬编码圆角 | `border-radius: 8px` → `border-radius: var(--radius-md)` |
| 硬编码阴影 | `box-shadow: 0 4px 12px ...` → `box-shadow: var(--shadow-md)` |
| 纯黑纯白 | `#000` / `#FFF` → 使用语义化色彩变量 |
| 无语义 div | 嵌套 `<div>` 代替 `<section>`, `<article>` 等 |
| 内联样式 | `style="color: red"` → scoped class |
| 重复代码 | 3 处以上相同逻辑 → 抽 composables / utils |
| 未用依赖 | package.json 有但未 import → 移除 |
| 无过渡动画 | 状态变化无 transition → 加 `transition: var(--transition-fast)` |

---

## 7. 文件组织

```
frontend/src/
├── styles/
│   └── variables.css       # Design Tokens（CSS 变量）
├── composables/            # 可复用组合函数
│   └── useCoverColor.js
├── utils/
│   └── date.js             # 日期格式化
├── api/
│   └── index.js            # API 封装层
├── components/             # 共享组件（跨页面复用）
│   ├── BookCard.vue
│   ├── Modal.vue
│   └── EmptyState.vue
├── views/                  # 页面级组件
│   ├── Bookshelf.vue
│   ├── BookDetail.vue
│   ├── Records.vue
│   └── My.vue
├── router/
│   └── index.js
├── App.vue                 # 壳（仅含 router-view + 底部导航）
└── main.js                 # 入口
```

---

## 8. 自检清单（输出代码前逐条核对）

- [ ] 所有颜色是否通过 CSS 变量引用？
- [ ] 所有间距是否符合 8px 网格？
- [ ] 是否使用了语义化 HTML 标签？
- [ ] `<img>` 是否都有 `alt`？
- [ ] 表单 `<label>` 是否关联了 `input[id]`？
- [ ] 是否有重复代码需要抽取？
- [ ] 是否有未使用的依赖/变量？
- [ ] 所有交互元素是否有 transition？
- [ ] 阴影是否使用多层而非单层？
- [ ] 是否避免了纯黑纯白？
- [ ] scoped 样式是否启用？
- [ ] 是否有 `!important` 或超过 3 层嵌套？
