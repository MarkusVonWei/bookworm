<template>
  <div class="app">
    <router-view />

    <nav class="bottom-nav" aria-label="主导航">
      <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
        <svg class="nav-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
        <span class="nav-text">首页</span>
      </router-link>
      <router-link to="/my" class="nav-item" :class="{ active: $route.path === '/my' || $route.path.startsWith('/book') }">
        <svg class="nav-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>
          <line x1="9" y1="7" x2="15" y2="7"/>
          <line x1="9" y1="11" x2="15" y2="11"/>
        </svg>
        <span class="nav-text">资产</span>
      </router-link>
      <router-link to="/records" class="nav-item" :class="{ active: $route.path === '/records' }">
        <svg class="nav-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
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
  border-top: 1px solid var(--color-border-light);
  z-index: 100;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-decoration: none;
  color: var(--color-text-muted);
  transition: color var(--transition-fast);
  gap: var(--space-xs);
  padding: var(--space-xs) var(--space-md);
}

.nav-item.active {
  color: var(--color-primary);
}

.nav-icon {
  width: 24px;
  height: 24px;
}

.nav-text {
  font-size: 11px;
  font-weight: 500;
}
</style>
