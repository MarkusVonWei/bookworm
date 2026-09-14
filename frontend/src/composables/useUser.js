/**
 * 用户状态管理 composable
 *
 * 职责:
 * 1. 应用启动时根据 device_id 初始化匿名用户
 * 2. 提供用户状态 (user_id, is_anonymous, name)
 * 3. 提供注册方法 (匿名用户 → 正式用户)
 * 4. 提供登录方法
 */

import { ref, readonly } from 'vue'
import { getDeviceId } from '../utils/device'
import api from '../api/index'

// 全局状态 (单例)
const user = ref(null)
const loading = ref(false)
const initialized = ref(false)

export function useUser() {

  /**
   * 初始化用户 - 应用启动时调用
   * 根据 device_id 获取或创建匿名用户
   */
  async function initUser() {
    if (initialized.value) return user.value

    loading.value = true
    try {
      const deviceId = getDeviceId()
      const res = await api.post('/user/init', { device_id: deviceId })
      user.value = res.data
      initialized.value = true
      return user.value
    } catch (err) {
      console.error('用户初始化失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 注册正式用户 (匿名 → 正式)
   * @param {string} phone - 手机号
   * @param {string} password - 密码
   * @param {string} name - 昵称 (可选)
   */
  async function register(phone, password, name) {
    loading.value = true
    try {
      const deviceId = getDeviceId()
      const res = await api.post('/user/register-with-device', {
        device_id: deviceId,
        phone,
        password,
        name: name || '书架主人',
      })
      user.value = res.data
      return user.value
    } catch (err) {
      console.error('注册失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 登录
   * @param {string} phone - 手机号
   * @param {string} password - 密码
   */
  async function login(phone, password) {
    loading.value = true
    try {
      const res = await api.post('/user/login', { phone, password })
      user.value = res.data
      return user.value
    } catch (err) {
      console.error('登录失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取当前 user_id (用于 API 请求头)
   */
  function getUserId() {
    return user.value?.user_id || null
  }

  return {
    user: readonly(user),
    loading: readonly(loading),
    initialized: readonly(initialized),
    initUser,
    register,
    login,
    getUserId,
  }
}
