/**
 * 设备指纹生成
 *
 * 基于浏览器特征生成确定性 ID, 同一设备/浏览器始终生成相同值.
 * 用于匿名用户标识 (localStorage 持久化).
 */

const STORAGE_KEY = 'bookworm_device_id'

/**
 * 生成设备指纹 (基于浏览器特征的简单 hash)
 * 不依赖外部库, 纯前端实现
 */
function generateFingerprint() {
  const components = [
    navigator.userAgent,
    navigator.language,
    screen.colorDepth,
    `${screen.width}x${screen.height}`,
    `${screen.availWidth}x${screen.availHeight}`,
    new Date().getTimezoneOffset(),
    navigator.hardwareConcurrency || 'unknown',
    navigator.platform || 'unknown',
  ]

  // Canvas fingerprint (更稳定)
  try {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    if (ctx) {
      ctx.textBaseline = 'top'
      ctx.font = '14px Arial'
      ctx.fillText('bookworm', 2, 2)
      components.push(canvas.toDataURL())
    }
  } catch (e) {
    // canvas 不可用时忽略
  }

  // WebGL fingerprint
  try {
    const canvas = document.createElement('canvas')
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl')
    if (gl) {
      const debugInfo = gl.getExtension('WEBGL_debug_renderer_info')
      if (debugInfo) {
        components.push(gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL))
        components.push(gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL))
      }
    }
  } catch (e) {
    // webgl 不可用时忽略
  }

  // 简单 hash (djb2)
  let hash = 5381
  const str = components.join('|||')
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) + hash) + str.charCodeAt(i)
    hash = hash & hash // 转为 32 位整数
  }

  // 转为 UUID 格式
  const hex = Math.abs(hash).toString(16).padStart(8, '0')
  return `${hex.slice(0, 8)}-${hex.slice(0, 4)}-4${hex.slice(1, 4)}-a${hex.slice(0, 3)}-${hex.slice(0, 12).padEnd(12, '0')}`
}

/**
 * 获取设备 ID (幂等: 同一设备始终返回相同值)
 * 优先从 localStorage 读取, 不存在则生成并持久化
 */
export function getDeviceId() {
  let deviceId = localStorage.getItem(STORAGE_KEY)
  if (deviceId) {
    return deviceId
  }

  deviceId = generateFingerprint()
  localStorage.setItem(STORAGE_KEY, deviceId)
  return deviceId
}
