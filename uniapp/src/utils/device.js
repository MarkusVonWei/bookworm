/**
 * 设备指纹生成
 * 基于平台特征生成确定性 ID, 同一设备始终生成相同值
 */

const STORAGE_KEY = 'bookworm_device_id'

function generateFingerprint() {
  // #ifdef H5
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
  try {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    if (ctx) {
      ctx.textBaseline = 'top'
      ctx.font = '14px Arial'
      ctx.fillText('bookworm', 2, 2)
      components.push(canvas.toDataURL())
    }
  } catch (e) { /* ignore */ }
  const str = components.join('|||')
  // #endif

  // #ifdef MP-WEIXIN
  const sysInfo = uni.getSystemInfoSync()
  const str = [
    sysInfo.brand,
    sysInfo.model,
    sysInfo.system,
    sysInfo.platform,
    sysInfo.screenWidth,
    sysInfo.screenHeight,
    sysInfo.pixelRatio,
  ].join('|||')
  // #endif

  // djb2 hash
  let hash = 5381
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) + hash) + str.charCodeAt(i)
    hash = hash & hash
  }

  const hex = Math.abs(hash).toString(16).padStart(8, '0')
  return `${hex.slice(0, 8)}-${hex.slice(0, 4)}-4${hex.slice(1, 4)}-a${hex.slice(0, 3)}-${hex.slice(0, 12).padEnd(12, '0')}`
}

export function getDeviceId() {
  let deviceId = uni.getStorageSync(STORAGE_KEY)
  if (deviceId) return deviceId

  deviceId = generateFingerprint()
  uni.setStorageSync(STORAGE_KEY, deviceId)
  return deviceId
}

export function clearDeviceId() {
  uni.removeStorageSync(STORAGE_KEY)
}
