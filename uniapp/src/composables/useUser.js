/**
 * 用户状态管理
 * 负责用户初始化、验证、注册、登录
 */

import { ref, readonly } from 'vue'
import { getDeviceId, clearDeviceId } from '../utils/device'
import * as api from '../api/index'

const user = ref(null)
const loading = ref(false)
const initialized = ref(false)

export function useUser() {

  /**
   * 初始化用户 - 应用启动时调用
   * 1. 检查本地缓存 userId
   * 2. 有则验证有效性（GET /api/user/me）
   * 3. 无效则清除缓存重新初始化
   * 4. 无缓存则直接初始化
   */
  async function initUser() {
    if (initialized.value) return user.value

    loading.value = true
    try {
      const cachedUserId = uni.getStorageSync('userId')

      if (cachedUserId) {
        // 验证缓存用户是否有效
        try {
          const res = await api.getMe()
          user.value = res
          initialized.value = true
          return user.value
        } catch (err) {
          if (err.statusCode) {
            // 后端明确拒绝 → 用户无效，清除缓存重建
            console.warn('缓存用户无效，重新初始化:', err.statusCode)
            resetUser()
          } else {
            // 网络异常 → 保留缓存用户
            user.value = { user_id: cachedUserId }
            initialized.value = true
            return user.value
          }
        }
      } else {
        // 无缓存 → 初始化新用户
        await initAnonymousUser()
      }
    } finally {
      loading.value = false
    }
    return user.value
  }

  /**
   * 初始化匿名用户
   */
  async function initAnonymousUser() {
    const deviceId = getDeviceId()
    const res = await api.initUser(deviceId)
    user.value = res
    uni.setStorageSync('userId', res.user_id)
    initialized.value = true
    return user.value
  }

  /**
   * 重置用户：清除缓存重新初始化
   */
  async function resetUser() {
    uni.removeStorageSync('userId')
    clearDeviceId()
    user.value = null
    return initAnonymousUser()
  }

  /**
   * 注册正式用户 (匿名 → 正式)
   */
  async function register(phone, password, name) {
    loading.value = true
    try {
      const deviceId = getDeviceId()
      const res = await api.registerUser({
        device_id: deviceId,
        phone,
        password,
        name: name || '书架主人'
      })
      user.value = res
      uni.setStorageSync('userId', res.user_id)
      return user.value
    } finally {
      loading.value = false
    }
  }

  /**
   * 登录
   */
  async function login(phone, password) {
    loading.value = true
    try {
      const res = await api.loginUser({ phone, password })
      user.value = res
      uni.setStorageSync('userId', res.user_id)
      return user.value
    } finally {
      loading.value = false
    }
  }

  function getUserId() {
    return user.value?.user_id || uni.getStorageSync('userId') || null
  }

  return {
    user: readonly(user),
    loading: readonly(loading),
    initialized: readonly(initialized),
    initUser,
    register,
    login,
    resetUser,
    getUserId
  }
}
