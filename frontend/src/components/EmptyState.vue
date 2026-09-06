<template>
  <div class="empty-state">
    <div class="empty-state__icon">{{ icon }}</div>
    <p class="empty-state__title">{{ title }}</p>
    <p v-if="description" class="empty-state__desc">{{ description }}</p>
  </div>
</template>

<script setup>
defineProps({
  icon: { type: String, default: '📭' },
  title: { type: String, required: true },
  description: { type: String, default: '' },
})
</script>

<style scoped>
.empty-state {
  text-align: center;
  padding: var(--space-2xl) var(--space-lg);
}

.empty-state__icon {
  font-size: 64px;
  margin-bottom: var(--space-lg);
}

.empty-state__title {
  font-size: 16px;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-xs);
}

.empty-state__desc {
  font-size: 14px;
  color: var(--color-text-placeholder);
}
</style>
