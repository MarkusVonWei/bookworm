<template>
  <view class="profile-page">
    <!-- 用户信息卡片 -->
    <view class="user-card">
      <view class="avatar">
        <text class="avatar-text">{{ userInitial }}</text>
      </view>
      <view class="user-info">
        <text class="user-name">{{ user?.name || '书架主人' }}</text>
        <text class="user-type">{{ user?.is_anonymous === false ? '正式用户' : '匿名用户' }}</text>
      </view>
    </view>

    <!-- 未登录：登录/注册切换 -->
    <view class="auth-section" v-if="!isLoggedIn || isAnonymous">
      <view class="auth-tabs">
        <view
          class="auth-tab"
          :class="{ 'auth-tab--active': authMode === 'login' }"
          @tap="authMode = 'login'"
        >登录</view>
        <view
          class="auth-tab"
          :class="{ 'auth-tab--active': authMode === 'register' }"
          @tap="authMode = 'register'"
        >注册</view>
      </view>

      <!-- 登录表单 -->
      <view class="auth-form" v-if="authMode === 'login'">
        <view class="form-group">
          <text class="form-label">手机号</text>
          <input
            class="form-input"
            v-model="loginForm.phone"
            type="number"
            maxlength="11"
            placeholder="请输入手机号"
          />
        </view>
        <view class="form-group">
          <text class="form-label">密码</text>
          <input
            class="form-input"
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
          />
        </view>
        <button
          class="btn btn--primary auth-btn"
          :disabled="authLoading || !loginForm.phone || !loginForm.password"
          @tap="handleLogin"
        >
          {{ authLoading ? '登录中...' : '登录' }}
        </button>
      </view>

      <!-- 注册表单 -->
      <view class="auth-form" v-else>
        <view class="form-group">
          <text class="form-label">手机号</text>
          <input
            class="form-input"
            v-model="registerForm.phone"
            type="number"
            maxlength="11"
            placeholder="请输入手机号"
          />
        </view>
        <view class="form-group">
          <text class="form-label">昵称</text>
          <input
            class="form-input"
            v-model="registerForm.name"
            placeholder="请输入昵称（选填）"
          />
        </view>
        <view class="form-group">
          <text class="form-label">密码</text>
          <input
            class="form-input"
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码（至少6位）"
          />
        </view>
        <view class="form-group">
          <text class="form-label">确认密码</text>
          <input
            class="form-input"
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
          />
        </view>
        <button
          class="btn btn--primary auth-btn"
          :disabled="authLoading || !canRegister"
          @tap="handleRegister"
        >
          {{ authLoading ? '注册中...' : '注册' }}
        </button>
      </view>
    </view>

    <!-- 已登录：用户操作 -->
    <view class="actions-section" v-if="isLoggedIn && !isAnonymous">
      <view class="action-item" @tap="logout">
        <text class="action-label">退出登录</text>
        <text class="action-arrow">→</text>
      </view>
    </view>

    <!-- 关于 -->
    <view class="about-section">
      <text class="about-title">关于我的书架</text>
      <text class="about-text">dog-ear — 把读过的，变成看得见的自己。</text>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUser } from '../../composables/useUser'
import { useToast } from '../../composables/useToast'

const toast = useToast()
const { user, initUser, register, login, resetUser } = useUser()

const authMode = ref('login')
const authLoading = ref(false)

const loginForm = ref({ phone: '', password: '' })
const registerForm = ref({ phone: '', name: '', password: '', confirmPassword: '' })

const userInitial = computed(() => {
  const name = user.value?.name || '书架主人'
  return name[0] || '书'
})

const isLoggedIn = computed(() => !!user.value)
const isAnonymous = computed(() => user.value?.is_anonymous !== false)

const canRegister = computed(() => {
  return (
    registerForm.value.phone.length === 11 &&
    registerForm.value.password.length >= 6 &&
    registerForm.value.password === registerForm.value.confirmPassword
  )
})

async function handleLogin() {
  if (!loginForm.value.phone || !loginForm.value.password) return
  authLoading.value = true
  try {
    await login(loginForm.value.phone, loginForm.value.password)
    toast.success('登录成功')
  } catch (err) {
    toast.error(err.message || '登录失败')
  } finally {
    authLoading.value = false
  }
}

async function handleRegister() {
  if (!canRegister.value) return
  authLoading.value = true
  try {
    await register(
      registerForm.value.phone,
      registerForm.value.password,
      registerForm.value.name || '书架主人'
    )
    toast.success('注册成功')
    authMode.value = 'login'
    registerForm.value = { phone: '', name: '', password: '', confirmPassword: '' }
  } catch (err) {
    toast.error(err.message || '注册失败')
  } finally {
    authLoading.value = false
  }
}

async function logout() {
  uni.showModal({
    title: '退出登录',
    content: '退出后将重新以匿名身份使用，确定退出吗？',
    success: async (res) => {
      if (res.confirm) {
        await resetUser()
        toast.success('已退出登录')
      }
    }
  })
}

onShow(async () => {
  if (!user.value) {
    await initUser()
  }
})
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: var(--color-bg-page);
  padding: 12px 16px 32px;
}

/* 用户卡片 */
.user-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  margin-bottom: 20px;
}

.avatar {
  width: 56px;
  height: 56px;
  background: var(--color-primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-text {
  font-size: 24px;
  color: var(--color-text-white);
  font-weight: 700;
}

.user-info {
  flex: 1;
}

.user-name {
  display: block;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.user-type {
  display: block;
  font-size: 12px;
  color: var(--color-text-muted);
  margin-top: 2px;
}

/* 认证区域 */
.auth-section {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: 16px;
  box-shadow: var(--shadow-card);
  margin-bottom: 20px;
}

.auth-tabs {
  display: flex;
  gap: 0;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--color-border-light);
}

.auth-tab {
  flex: 1;
  text-align: center;
  padding: 10px;
  font-size: 15px;
  color: var(--color-text-muted);
  border-bottom: 2px solid transparent;
}

.auth-tab--active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
  font-weight: 600;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.auth-btn {
  margin-top: 12px;
  width: 100%;
}

/* 表单 */
.form-group {
  margin-bottom: 14px;
}

.form-label {
  display: block;
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}

.form-input {
  width: 100%;
  height: 44px;
  padding: 0 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  background: var(--color-bg-soft);
  box-sizing: border-box;
}

/* 操作 */
.actions-section {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-card);
  margin-bottom: 20px;
}

.action-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--color-border-light);
}

.action-label {
  font-size: 15px;
  color: var(--color-text-primary);
}

.action-arrow {
  color: var(--color-text-muted);
}

/* 关于 */
.about-section {
  padding: 16px;
  text-align: center;
}

.about-title {
  display: block;
  font-size: 13px;
  color: var(--color-text-muted);
  margin-bottom: 4px;
}

.about-text {
  font-size: 12px;
  color: var(--color-text-muted);
}
</style>
