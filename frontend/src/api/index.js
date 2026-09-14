import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000
})

/**
 * 请求拦截器: 自动附加 X-User-Id header
 * 从 localStorage 读取 device_id, 由 useUser composable 在初始化时设置
 */
api.interceptors.request.use((config) => {
  const deviceId = localStorage.getItem('bookworm_device_id')
  if (deviceId) {
    config.headers['X-User-Id'] = deviceId
  }
  return config
})

// ========== 用户API ==========

// 初始化匿名用户
export function initUser(deviceId) {
  return api.post('/user/init', { device_id: deviceId })
}

// 注册 (匿名 → 正式)
export function registerUser(data) {
  return api.post('/user/register-with-device', data)
}

// 登录
export function loginUser(data) {
  return api.post('/user/login', data)
}

// 获取当前用户信息
export function getMe() {
  return api.get('/user/me')
}

// ========== 书架API ==========

// 获取所有书籍
export function getBooks(status = null) {
  const params = {}
  if (status) params.status = status
  return api.get('/bookshelf/books', { params })
}

// 获取单本书籍
export function getBook(id) {
  return api.get(`/bookshelf/books/${id}`)
}

// 添加书籍
export function createBook(bookData) {
  return api.post('/bookshelf/books', bookData)
}

// 更新书籍
export function updateBook(id, bookData) {
  return api.put(`/bookshelf/books/${id}`, bookData)
}

// 删除书籍
export function deleteBook(id) {
  return api.delete(`/bookshelf/books/${id}`)
}

// 更新阅读状态
export function updateBookStatus(id, status) {
  return api.put(`/bookshelf/books/${id}/status`, null, { params: { status } })
}

// 识别书籍
export function recognizeBook(file) {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/bookshelf/recognize', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// ========== 阅读记录API ==========

// 获取书籍的阅读记录
export function getReadingRecords(bookId) {
  return api.get(`/bookshelf/books/${bookId}/records`)
}

// 添加阅读记录
export function createReadingRecord(bookId, recordData) {
  return api.post(`/bookshelf/books/${bookId}/records`, recordData)
}

// 获取所有阅读记录
export function getAllRecords() {
  return api.get('/bookshelf/records')
}

// ========== 统计API ==========

// 获取统计信息
export function getStatistics() {
  return api.get('/bookshelf/statistics')
}

// ========== 时间线API ==========

// 获取时间线 (状态里程碑 + 阅读记录)
export function getTimeline() {
  return api.get('/bookshelf/timeline')
}

// ========== 搜索API ==========

// 搜索书籍
export function searchBooks(keyword) {
  return api.get('/bookshelf/search', { params: { keyword } })
}

// ========== 健康检查 ==========

export function healthCheck() {
  return api.get('/health')
}

export default api
