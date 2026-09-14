<template>
  <Teleport to="body">
    <div class="modal-overlay" @click.self="$emit('close')">
      <div class="modal" :class="sizeClass" role="dialog" aria-modal="true">
        <header class="modal-header">
          <slot name="header">
            <h2>{{ title }}</h2>
          </slot>
          <button class="modal-close" @click="$emit('close')" aria-label="关闭">&times;</button>
        </header>

        <div class="modal-body">
          <slot />
        </div>

        <footer v-if="$slots.footer" class="modal-footer">
          <slot name="footer" />
        </footer>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: { type: String, default: '' },
  size: { type: String, default: 'md', validator: (v) => ['sm', 'md', 'lg'].includes(v) },
})

defineEmits(['close'])

const sizeClass = computed(() => `modal--${props.size}`)
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--color-overlay);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 1000;
  padding: var(--space-md);
}

@media (min-width: 480px) {
  .modal-overlay {
    align-items: center;
  }
}

.modal {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
  width: 100%;
  max-height: 85vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-xl);
  padding-bottom: env(safe-area-inset-bottom);
}

@media (min-width: 480px) {
  .modal {
    border-radius: var(--radius-lg);
    max-height: 90vh;
    padding-bottom: 0;
  }
}

.modal--sm { max-width: 400px; }
.modal--md { max-width: 500px; }
.modal--lg { max-width: 640px; }

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-md) var(--space-lg) var(--space-sm);
}

.modal-header h2 {
  font-size: 17px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.modal-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-hover);
  border: none;
  border-radius: var(--radius-full);
  font-size: 18px;
  color: var(--color-text-secondary);
  cursor: pointer;
  line-height: 1;
  transition: all var(--transition-fast);
}

.modal-close:hover {
  background: var(--color-border);
  color: var(--color-text-primary);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-lg);
  -webkit-overflow-scrolling: touch;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-lg) var(--space-md);
}
</style>
