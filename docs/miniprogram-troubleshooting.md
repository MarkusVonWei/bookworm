# 小程序踩坑记录与解决方案

本文记录「我的书架」微信小程序开发过程中遇到的典型问题及修复方式。

---

## 1. `api.js` 中 `baseUrl` 为空

### 现象

所有请求 URL 变成相对路径（`/api/bookshelf/...`），网络请求失败。

### 原因

`api.js` 在**模块加载时**执行 `const app = getApp()`，此时 App 实例尚未创建，`getApp()` 返回 `undefined`。后续 `init()` 从未被任何地方调用，`baseUrl` 始终为空字符串。

```js
// 错误写法 — 模块加载时 getApp() 返回 undefined
const app = getApp()

const api = {
  baseUrl: '',
  init() {
    this.baseUrl = app.globalData.apiBaseUrl // 读 undefined 的属性
  },
}
```

### 修复

- 删除模块顶层的 `getApp()` 调用
- `init()` 接收外部传入的 app 实例（见问题 2）
- `request()` / `uploadFile()` 内部调用 `ensureInit()` 做懒加载兜底

```js
// app.js onLaunch 中显式初始化
api.init(this)
```

---

## 2. `onLaunch` 中 `getApp()` 返回 undefined

### 现象

```
TypeError: Cannot read properties of undefined (reading 'globalData')
    at Object.init (app.js:10)
    at onLaunch (app.js:186)
```

### 原因

微信小程序中 `getApp()` 在 `App()` 构造完成、`onLaunch` 执行期间**仍不可用**。App 实例要到 `onLaunch` 结束后才能通过 `getApp()` 获取。

### 修复

`onLaunch` 中不要用 `getApp()`，直接把 `this` 传给 `api.init()`：

```js
// app.js
App({
  onLaunch() {
    api.init(this) // 传 this，而非 getApp()
    this.initUser()
  },
})

// api.js
init(app) {
  this.baseUrl = app.globalData.apiBaseUrl
},
ensureInit() {
  if (!this.baseUrl) {
    this.baseUrl = getApp().globalData.apiBaseUrl // 请求时 getApp() 已可用
  }
},
```

---

## 3. 域名配置报「不在 request 合法域名列表中」

### 现象

已在微信公众平台配置了 `https://www.bookworm.icu`，但开发者工具仍报：

```
https://www.bookworm.icu 不在以下 request 合法域名列表中
```

### 原因

微信开发者工具**不会自动拉取**后台更新的域名配置，需要手动刷新。

### 修复

1. **刷新配置**：开发者工具 → 「详情」→ 「域名信息」→ 点「刷新」，然后重新编译
2. **确认后台位置**：必须加到 **request 合法域名**（不是 socket / uploadFile），且只填域名不含路径
3. **确认 AppID 一致**：`project.config.json` 的 `appid` 必须与后台配置域名的小程序一致
4. **开发临时方案**：「详情」→「本地设置」→ 勾选「不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书」（上线前取消）

> **注意**：`uploadFile` 接口（`/api/bookshelf/recognize`）还需要把域名加到 **uploadFile 合法域名**。

---

## 4. 本地缓存用户失效未清理

### 现象

后端数据库重置或用户数据被清除后，小程序仍使用本地缓存的 `userId` 请求，接口返回 401，页面加载异常。

### 原因

`initUser()` 只检查本地是否有 `userId` 缓存，不向后端验证有效性。

### 修复

启动时请求 `GET /api/user/me` 验证用户，无效则清除缓存并重新初始化：

```js
initUser() {
  const userId = wx.getStorageSync('userId')
  if (userId) {
    wx.request({
      url: `${this.globalData.apiBaseUrl}/api/user/me`,
      header: { 'X-User-Id': userId },
      success: (res) => {
        if (res.statusCode === 200) {
          this.globalData.userId = userId       // 验证通过
        } else {
          this.resetUser()                       // 无效 → 清缓存重建
        }
      },
      fail: () => {
        this.globalData.userId = userId          // 网络异常 → 保留缓存，不清
      },
    })
  } else {
    this.resetUser()
  }
},

resetUser() {
  wx.removeStorageSync('userId')
  wx.removeStorageSync('deviceId')
  this.globalData.userId = null
  this.initAnonymousUser(this.getDeviceId())
},
```

**设计要点**：网络请求失败（`fail`）时不废弃缓存用户，避免网络抖动导致误清；只有后端明确返回非 200（用户不存在 / 未授权）才清理。

---

## 通用注意事项

| 事项 | 说明 |
|------|------|
| `getApp()` 时机 | 只能在 `onLaunch` 之后调用；模块加载和 `onLaunch` 期间都不可用 |
| 域名配置 | 后台改完必须在开发者工具手动刷新；request / uploadFile 分开配置 |
| 缓存用户 | 每次启动验证有效性，区分「验证失败」和「网络失败」 |
| API 初始化 | `app.js` 显式 `api.init(this)`，`api.js` 内部 `ensureInit()` 兜底 |
