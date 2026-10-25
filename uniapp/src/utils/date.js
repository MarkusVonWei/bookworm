/**
 * 日期格式化工具
 * 后端存储精度：秒（DateTime）
 * 前端展示精度：小时（YYYY-MM-DD HH:mm）
 */

function pad(n) {
  return String(n).padStart(2, '0')
}

/**
 * 格式化为 YYYY-MM-DD HH:mm
 */
export function formatDateTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

/**
 * 格式化为 YYYY.MM.DD（仅日期）
 */
export function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}.${pad(d.getMonth() + 1)}.${pad(d.getDate())}`
}

/**
 * 格式化为 HH:mm（仅时间）
 */
export function formatTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${pad(d.getHours())}:${pad(d.getMinutes())}`
}
