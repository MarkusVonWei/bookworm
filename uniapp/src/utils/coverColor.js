/**
 * 根据书名生成封面占位色
 * 基于字符串 hash 的确定性映射，保证同一书名总是同一颜色
 */

const COVER_COLORS = [
  '#8B7355', '#6B8E9B', '#D4A574', '#B8A88A',
  '#5B8C5A', '#9B8B7A', '#7A9B8B', '#A59B8B',
]

export function getCoverColor(title) {
  if (!title) return COVER_COLORS[0]
  let hash = 0
  for (let i = 0; i < title.length; i++) {
    hash = title.charCodeAt(i) + ((hash << 5) - hash)
  }
  return COVER_COLORS[Math.abs(hash) % COVER_COLORS.length]
}

export { COVER_COLORS }

/**
 * 解析图片 URL（后端可能返回相对路径如 /data/uploads/xxx.jpg）
 */
export function resolveImageUrl(url) {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://')) return url
  return `https://www.bookworm.icu${url.startsWith('/') ? '' : '/'}${url}`
}
