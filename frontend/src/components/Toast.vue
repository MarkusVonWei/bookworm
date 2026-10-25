<template>
  <Teleport to="body">
    <Transition name="toast">
      <div v-if="visible" class="toast" :class="`toast--${type}`">
        <span class="toast-icon">{{ icon }}</span>
        <span class="toast-message">{{ message }}</span>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed } from 'vue'

const visible = ref(false)
const message = ref('')
const type = ref('info')

const icon = computed(() => {
  const icons = { success: '✓', error: '✕', info: 'ℹ', warning: '⚠' }
  return icons[type.value] || icons.info
})

let timer = null

function show(msg, toastType = 'info', duration = 2500) {
  message.value = msg
  type.value = toastType
  visible.value = true
  if (timer) clearTimeout(timer)
  timer = setTimeout(() => { visible.value = false }, duration)
}

defineExpose({ show })
</script>

<style scoped>
.toast {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-lg);
  background: var(--color-bg-card);
  border-radius: var(--radius-full);
  box-shadow: var(--shadow-float);
  z-index: 2000;
  font-size: 14px;
  color: var(--color-text-primary);
  max-width: 90vw;
}

.toast-icon {
  font-weight: 700;
  font-size: 16px;
}

.toast--success .toast-icon { color: var(--color-success); }
.toast--error .toast-icon { color: var(--color-danger); }
.toast--warning .toast-icon { color: var(--color-warning); }
.toast--info .toast-icon { color: var(--color-primary); }

.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-10px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-10px);
}
</style>
