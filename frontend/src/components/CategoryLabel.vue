<template>
  <div class="category-label" :style="{ backgroundColor: bgColor }">
    <span class="category-number">{{ number }}</span>
    <span class="category-name">{{ name }}</span>
  </div>
</template>

<script setup>
defineProps({
  number: { type: String, required: true },
  name: { type: String, required: true },
  bgColor: { type: String, default: '#E8DFD0' }
})
</script>

<style scoped>
.category-label {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  min-width: 60px;
}

.category-number {
  font-size: 11px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.category-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
}
</style>
