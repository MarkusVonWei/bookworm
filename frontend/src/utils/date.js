/**
 * 日期格式化工具
 *
 * 后端存储精度：秒（DateTime）
 * 前端展示精度：小时（YYYY-MM-DD HH:mm）
 */

/**
 * 格式化为 YYYY-MM-DD HH:mm
 * @param {string|Date} dateStr - ISO 时间字符串或 Date 对象
 * @returns {string} 格式化后的时间，如 "2026-09-06 16:03"
 */
export function formatDateTime(dateStr) {
  const d = new Date(dateStr)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

/**
 * 格式化为 YYYY.MM.DD（仅日期）
 * @param {string|Date} dateStr
 * @returns {string}
 */
export function formatDate(dateStr) {
  const d = new Date(dateStr)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}.${pad(d.getMonth() + 1)}.${pad(d.getDate())}`
}

/**
 * 格式化为 HH:mm（仅时间）
 * @param {string|Date} dateStr
 * @returns {string}
 */
export function formatTime(dateStr) {
  const d = new Date(dateStr)
  const pad = (n) => String(n).padStart(2, '0')
  return `${pad(d.getHours())}:${pad(d.getMinutes())}`
}
