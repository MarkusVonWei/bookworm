/**
 * 根据书名生成封面占位色
 * 基于字符串 hash 的确定性映射，保证同一书名总是同一颜色
 */

const COVER_COLORS = [
  '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4',
  '#ffeaa7', '#dfe6e9', '#fd79a8', '#a29bfe',
]

export function useCoverColor() {
  const getCoverColor = (title) => {
    let hash = 0
    for (let i = 0; i < title.length; i++) {
      hash = title.charCodeAt(i) + ((hash << 5) - hash)
    }
    return COVER_COLORS[Math.abs(hash) % COVER_COLORS.length]
  }

  return { getCoverColor }
}
