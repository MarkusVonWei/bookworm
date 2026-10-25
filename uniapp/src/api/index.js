/**
 * API 请求封装
 * 统一处理 baseUrl、X-User-Id header、错误格式
 * 与后端 src/bookworm/bookshelf/api.py 约定一致
 */

const BASE_URL = 'https://www.bookworm.icu'

// 从本地存储获取用户ID（与前端约定：X-User-Id 使用 user_id/device_id）
function getUserId() {
  return uni.getStorageSync('userId') || uni.getStorageSync('deviceId') || ''
}

// 统一请求方法
function request(options) {
  return new Promise((resolve, reject) => {
    const userId = getUserId()
    uni.request({
      url: `${BASE_URL}${options.url}`,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Content-Type': 'application/json',
        'X-User-Id': userId
      },
      timeout: 30000,
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          const err = new Error(
            (res.data && (res.data.detail || res.data.error)) || `请求失败(${res.statusCode})`
          )
          err.statusCode = res.statusCode
          err.data = res.data
          reject(err)
        }
      },
      fail(err) {
        reject(new Error(err.errMsg || '网络请求失败'))
      }
    })
  })
}

// 文件上传
function uploadFile(options) {
  return new Promise((resolve, reject) => {
    const userId = getUserId()
    uni.uploadFile({
      url: `${BASE_URL}${options.url}`,
      filePath: options.filePath,
      name: 'file',
      header: {
        'X-User-Id': userId
      },
      timeout: 60000,
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            resolve(typeof res.data === 'string' ? JSON.parse(res.data) : res.data)
          } catch (e) {
            resolve(res.data)
          }
        } else {
          let detail = ''
          try {
            const body = typeof res.data === 'string' ? JSON.parse(res.data) : res.data
            detail = (body && (body.detail || body.error)) || JSON.stringify(body)
          } catch (e) {
            detail = res.data
          }
          const err = new Error(`上传失败(${res.statusCode}): ${detail}`)
          err.statusCode = res.statusCode
          err.data = res.data
          reject(err)
        }
      },
      fail(err) {
        reject(new Error(err.errMsg || '上传请求失败'))
      }
    })
  })
}

// ========== 用户API ==========

export function initUser(deviceId) {
  return request({
    url: '/api/user/init',
    method: 'POST',
    data: { device_id: deviceId }
  })
}

export function getMe() {
  return request({ url: '/api/user/me' })
}

export function registerUser(data) {
  return request({
    url: '/api/user/register-with-device',
    method: 'POST',
    data
  })
}

export function loginUser(data) {
  return request({
    url: '/api/user/login',
    method: 'POST',
    data
  })
}

// ========== 书籍API ==========

export function getBooks(status) {
  const data = {}
  if (status) data.status = status
  return request({ url: '/api/bookshelf/books', data })
}

export function getBook(bookId) {
  return request({ url: `/api/bookshelf/books/${bookId}` })
}

export function createBook(bookData) {
  return request({
    url: '/api/bookshelf/books',
    method: 'POST',
    data: bookData
  })
}

export function updateBook(bookId, bookData) {
  return request({
    url: `/api/bookshelf/books/${bookId}`,
    method: 'PUT',
    data: bookData
  })
}

export function deleteBook(bookId) {
  return request({
    url: `/api/bookshelf/books/${bookId}`,
    method: 'DELETE'
  })
}

// 更新阅读状态（status 作为 query 参数，与后端约定一致）
export function updateBookStatus(bookId, status) {
  return request({
    url: `/api/bookshelf/books/${bookId}/status?status=${encodeURIComponent(status)}`,
    method: 'PUT'
  })
}

// ========== 阅读记录API ==========

export function getReadingRecords(bookId) {
  return request({ url: `/api/bookshelf/books/${bookId}/records` })
}

export function createReadingRecord(bookId, recordData) {
  return request({
    url: `/api/bookshelf/books/${bookId}/records`,
    method: 'POST',
    data: recordData
  })
}

export function getAllRecords() {
  return request({ url: '/api/bookshelf/records' })
}

// ========== 搜索API ==========

export function searchBooks(keyword) {
  return request({
    url: '/api/bookshelf/search',
    data: { keyword }
  })
}

// ========== 统计API ==========

export function getStatistics() {
  return request({ url: '/api/bookshelf/statistics' })
}

// ========== 时间线API ==========

export function getTimeline() {
  return request({ url: '/api/bookshelf/timeline' })
}

// ========== 识别API ==========

export function recognizeBook(filePath) {
  return uploadFile({
    url: '/api/bookshelf/recognize',
    filePath
  })
}

// ========== 健康检查 ==========

export function healthCheck() {
  return request({ url: '/health' })
}

export default {
  initUser,
  getMe,
  registerUser,
  loginUser,
  getBooks,
  getBook,
  createBook,
  updateBook,
  deleteBook,
  updateBookStatus,
  getReadingRecords,
  createReadingRecord,
  getAllRecords,
  searchBooks,
  getStatistics,
  getTimeline,
  recognizeBook,
  healthCheck
}

// ========== 外部搜索API ==========

// 搜索外部书籍目录（豆瓣）
export function searchBooksExternal(keyword, limit = 10) {
  return request({
    url: `/api/bookshelf/search-external?keyword=${encodeURIComponent(keyword)}&limit=${limit}`
  })
}
