<template>
  <div class="dog-ear-logo" :class="{ 'logo--large': size === 'large' }">
    <svg class="logo-icon" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <!-- 狗头轮廓 -->
      <path d="M12 8C12 8 8 4 4 8C0 12 4 20 12 24L24 28L36 24C44 20 48 12 44 8C40 4 36 8 36 8"
            stroke="currentColor" stroke-width="2.5" stroke-linecap="round" fill="none"/>
      <!-- 狗耳朵 -->
      <path d="M8 10C8 10 6 6 4 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/>
      <path d="M40 10C40 10 42 6 44 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/>
      <!-- 狗脸 -->
      <circle cx="18" cy="16" r="2" fill="currentColor"/>
      <circle cx="30" cy="16" r="2" fill="currentColor"/>
      <ellipse cx="24" cy="20" rx="3" ry="2" fill="currentColor"/>
      <!-- 嘴巴 -->
      <path d="M20 24C20 24 22 26 24 26C26 26 28 24 28 24" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" fill="none"/>
    </svg>
    <span v-if="showText" class="logo-text">dog-ear</span>
  </div>
</template>

<script setup>
defineProps({
  size: { type: String, default: 'normal' },
  showText: { type: Boolean, default: true }
})
</script>

<style scoped>
.dog-ear-logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-icon {
  width: 32px;
  height: 32px;
  color: var(--color-primary);
}

.logo--large .logo-icon {
  width: 48px;
  height: 48px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-primary);
  letter-spacing: -0.5px;
}

.logo--large .logo-text {
  font-size: 28px;
}
</style>
