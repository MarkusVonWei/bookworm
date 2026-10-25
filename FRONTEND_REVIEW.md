# 前端代码审查报告

> 基于 SKILL.md 规范，对 bookworm 项目现有前端代码的逐文件审查。
> 状态：🔴 严重 / 🟡 中等 / 🟢 建议

---

## 一、全局问题

### 🔴 1. 无 Design Tokens — 颜色/间距/阴影全部硬编码

**涉及文件：所有 `.vue` 文件的 `<style>` 部分**

当前状态：`#409eff`、`#333`、`#999`、`#666`、`#f5f5f5`、`#eee` 等色值散落在 5 个组件中，至少出现 **40+ 处**硬编码色值。间距 `10px`、`12px`、`13px`、`14px`、`20px`、`30px` 无统一系统。阴影 `0 4px 12px rgba(0,0,0,0.15)` 等单层写法重复出现。

**改进方向：** 将 `frontend/src/styles/variables.css` 引入 `main.js`，全量替换硬编码值为 CSS 变量。

### 🔴 2. Element Plus 已安装但从未使用

**文件：** `package.json`（依赖）、`main.js`（import + app.use）

`element-plus` 及其 CSS 被引入并注册，但 5 个页面组件无一处使用 `<el-xxx>` 组件。白白增加 ~200KB 打包体积。

**改进方向：** 二选一——要么全面使用 Element Plus 组件（按钮、弹窗、表单、空状态），要么彻底移除依赖。

### 🟡 3. 重复代码未抽取

**`getCoverColor` 函数出现 3 次：**
- `Bookshelf.vue:254-261`
- `BookDetail.vue:213-220`
- `My.vue:144-151`

三处逻辑完全一致（hash + 相同 8 色数组）。

**改进方向：** 已创建 `composables/useCoverColor.js`，三个组件改为 `import { useCoverColor } from '@/composables/useCoverColor'`。

### 🟡 4. Modal 样式重复

**`Bookshelf.vue` 和 `BookDetail.vue`** 各自定义了一套完整的 modal 样式（`.modal-overlay`、`.modal`、`.modal-header`、`.modal-body`、`.modal-footer`、`.close-btn`、`.btn`、`.btn-primary`、`.btn-secondary`），约 80 行 CSS 完全重复。

**改进方向：** 抽取 `components/Modal.vue` 公共组件。

---

## 二、逐文件审查

### `App.vue`

| # | 级别 | 问题 | 位置 |
|---|---|---|---|
| 1 | 🔴 | 全局样式 `* { margin:0; padding:0 }` 无 CSS 变量 | `<style>` L27-30 |
| 2 | 🟡 | 底部导航 `background: white` 硬编码，应为 `var(--color-bg-card)` | L48 |
| 3 | 🟡 | 阴影 `0 -2px 10px rgba(0,0,0,0.1)` 单层且不精致，应用 `var(--shadow-md)` 改为上边框线 | L52 |
| 4 | 🟡 | `color: #666`、`#409eff` 硬编码 | L63, L67 |
| 5 | 🟢 | `<div class="app">` 可改为语义化 `<div id="app">` 或直接用 `<router-view>` 作根 | L2 |
| 6 | 🟢 | 底部导航缺少 `aria-label` 无障碍标注 | L6 |

### `Bookshelf.vue`

| # | 级别 | 问题 | 位置 |
|---|---|---|---|
| 1 | 🔴 | 整个 `<style scoped>` 约 350 行，全部硬编码色值/间距/阴影/圆角 | 全文件 |
| 2 | 🔴 | `style="display: none"` 内联样式 | L54 |
| 3 | 🔴 | `style="{ backgroundColor: getCoverColor(...) }"` 动态内联 | L27 |
| 4 | 🟡 | `getCoverColor` 重复定义 | L254-261 |
| 5 | 🟡 | 弹窗 `.modal` 样式与 BookDetail.vue 完全重复 | L412-456 |
| 6 | 🟡 | `.btn`、`.btn-primary`、`.btn-secondary` 与 BookDetail.vue 重复 | L593-616 |
| 7 | 🟡 | `.form-group`、`.form-group label`、`.form-group input` 与 BookDetail.vue 重复 | L539-555 |
| 8 | 🟡 | `color: #333`（3处）、`#999`（4处）、`#666`（2处）、`#ddd`（5处）硬编码 | 散布 |
| 9 | 🟡 | `padding: 10px`（非 8px 倍数） | L268 |
| 10 | 🟡 | `gap: 10px`（非 8px 倍数） | L453 |
| 11 | 🟡 | `margin-bottom: 30px`（非标准间距值，应为 32px） | L275 |
| 12 | 🟡 | `padding: 40px 20px`（40px 非标准值，应为 48px） | L461 |
| 13 | 🟡 | `padding-bottom: 60px`（应为 64px 或用标准值） | App.vue L40 |
| 14 | 🟡 | `upload-area` 缺少键盘可达性（无 `tabindex`、无 `@keydown`） | L50 |
| 15 | 🟡 | `remove-btn` 缺少 `aria-label="移除图片"` | L65 |
| 16 | 🟢 | `loading` 状态缺少视觉反馈（spinner 仅 CSS 动画，无 `role="status"`） | L70-73 |
| 17 | 🟢 | `v-if` / `v-else` 分支中 `<input type="radio">` 无关联 `<label>` | L106 |

### `BookDetail.vue`

| # | 级别 | 问题 | 位置 |
|---|---|---|---|
| 1 | 🔴 | 整个 `<style scoped>` 约 320 行，全部硬编码 | 全文件 |
| 2 | 🔴 | `style="{ backgroundColor: getCoverColor(...) }"` 动态内联 | L13 |
| 3 | 🟡 | `getCoverColor` 重复定义 | L213-220 |
| 4 | 🟡 | Modal 样式与 Bookshelf.vue 重复（约 80 行） | L444-501 |
| 5 | 🟡 | `.btn`、`.btn-primary`、`.btn-secondary` 重复 | L524-546 |
| 6 | 🟡 | `.form-group`、`label`、`input`、`textarea` 样式重复 | L503-522 |
| 7 | 🟡 | `color: #333`（5处）、`#999`（3处）、`#666`（3处）、`#ddd`（4处）硬编码 | 散布 |
| 8 | 🟡 | `box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2)` 单层重阴影 | L259 |
| 9 | 🟡 | `box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05)` 单层阴影 | L405 |
| 10 | 🟡 | 删除按钮无确认二次弹窗（仅 `confirm()`，不美观） | L180-181 |
| 11 | 🟢 | `<header class="header">` 中 `← 返回` 可用 `<button aria-label="返回">` | L5 |
| 12 | 🟢 | 表单 `<label>` 未关联 `input[id]`（无障碍） | L94, L98, L102, L106 |

### `Records.vue`

| # | 级别 | 问题 | 位置 |
|---|---|---|---|
| 1 | 🟡 | 硬编码色值 `#333`、`#999`、`#666`、`#eee`、`#f0f0f0` | 散布 |
| 2 | 🟡 | `padding: 20px`（非标准值，应为 `--space-lg` 即 24px） | L94 |
| 3 | 🟡 | `padding: 16px` 在 `.record-card` 中 OK，但 `.date-header` 的 `padding-bottom: 8px` 与 `margin-bottom: 12px` 组合不一致 | L130-131 |
| 4 | 🟡 | `.tag` 的 `padding: 2px 8px`（2px 非标准值） | L181 |
| 5 | 🟢 | `@click="goToBook(record.book_id)"` 缺少键盘支持（卡片应可聚焦） | L16 |

### `My.vue`

| # | 级别 | 问题 | 位置 |
|---|---|---|---|
| 1 | 🔴 | `getCoverColor` 第三处重复定义 | L144-151 |
| 2 | 🟡 | `linear-gradient(135deg, #667eea 0%, #764ba2 100%)` 硬编码渐变色 | L205 |
| 3 | 🟡 | 硬编码色值散布 | 散布 |
| 4 | 🟡 | `padding: 20px`（非标准值） | L158, L239, L310 |
| 5 | 🟡 | `margin-right: 20px`（非标准值，应为 `--space-lg` 即 24px） | L215 |
| 6 | 🟡 | `margin-bottom: 24px` OK，但 `margin-bottom: 16px` 与 `margin-bottom: 12px` 混用不一致 | L246, L193 |
| 7 | 🟢 | `.stat-value` 的 `font-size: 28px` 可考虑用 CSS 变量统一 | L189 |

---

## 三、重复代码汇总（应抽取为公共组件/Composable）

| 重复项 | 出现位置 | 建议 |
|---|---|---|
| `getCoverColor()` | Bookshelf, BookDetail, My | → `composables/useCoverColor.js`（已创建） |
| Modal 样式（~80行） | Bookshelf, BookDetail | → `components/Modal.vue` |
| `.btn` / `.btn-primary` / `.btn-secondary` | Bookshelf, BookDetail | → `components/BaseButton.vue` 或全局样式 |
| `.form-group` / `.form-group label` / `.form-group input` | Bookshelf, BookDetail | → `components/FormFields.vue` 或全局样式 |
| `.empty-shelf` / `.empty-state` / `.empty-records` | Bookshelf, Records, BookDetail | → `components/EmptyState.vue` |

---

## 四、优先级排序

### P0 — 必须修复（阻塞工程质量）

1. 引入 `variables.css` 到 `main.js`，建立 Design Tokens 基础
2. 决策 Element Plus 去留：使用或移除
3. 将 `getCoverColor` 改为 import `useCoverColor` composable

### P1 — 应该修复（影响可维护性）

4. 抽取 `Modal.vue` 公共组件，消除两处重复
5. 抽取 `EmptyState.vue` 公共组件
6. 抽取按钮 / 表单域的共享样式
7. 全量替换硬编码色值为 CSS 变量
8. 全量替换硬编码间距为标准间距值
9. 全量替换单层阴影为多层阴影变量

### P2 — 建议改进（提升体验与无障碍）

10. 底部导航加 `aria-label`
11. 上传区域加 `tabindex` 和键盘事件
12. 图片加 `alt` 属性
13. 表单 label 关联 input id
14. 删除操作增加二次确认弹窗
15. 所有交互元素加 `transition`

---

## 五、已安装的基础设施

| 文件 | 状态 | 说明 |
|---|---|---|
| `styles/variables.css` | ✅ 已创建 | Design Tokens，待引入 main.js |
| `composables/useCoverColor.js` | ✅ 已创建 | 封面颜色生成，待组件引用 |
| `SKILL.md` | ✅ 已创建 | 前端开发规范 |
