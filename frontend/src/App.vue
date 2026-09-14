<template>
  <div class="app">
    <router-view />

    <nav class="bottom-nav" aria-label="主导航">
      <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
        <span class="nav-icon" aria-hidden="true">📚</span>
        <span class="nav-text">书架</span>
      </router-link>
      <router-link to="/records" class="nav-item" :class="{ active: $route.path === '/records' }">
        <span class="nav-icon" aria-hidden="true">📝</span>
        <span class="nav-text">记录</span>
      </router-link>
      <router-link to="/my" class="nav-item" :class="{ active: $route.path === '/my' }">
        <span class="nav-icon" aria-hidden="true">👤</span>
        <span class="nav-text">我的</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
</script>

<style>
*,
*::before,
*::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-family);
  background-color: var(--color-bg-page);
  color: var(--color-text-regular);
  -webkit-font-smoothing: antialiased;
  -webkit-tap-highlight-color: transparent;
  -webkit-text-size-adjust: 100%;
  overscroll-behavior: none;
}

.app {
  min-height: 100dvh;
  padding-bottom: calc(64px + env(safe-area-inset-bottom));
}

.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--color-bg-card);
  display: flex;
  justify-content: space-around;
  padding: var(--space-sm) 0 calc(var(--space-sm) + env(safe-area-inset-bottom));
  border-top: 1px solid var(--color-border);
  z-index: 100;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-decoration: none;
  color: var(--color-text-secondary);
  transition: color var(--transition-fast);
  gap: var(--space-xs);
}

.nav-item.active {
  color: var(--color-primary);
}

.nav-icon {
  font-size: 22px;
  line-height: 1;
}

.nav-text {
  font-size: 11px;
  font-weight: 500;
}
</style>
