<template>
  <div class="my-page">
    <header class="page-header">
      <h1 class="page-title">我的</h1>
    </header>

    <section class="stats-section">
      <div class="stats-card">
        <div class="stat-item">
          <div class="stat-value">{{ stats.total_books || 0 }}</div>
          <div class="stat-label">全部书籍</div>
        </div>
        <div class="stat-item">
          <div class="stat-value stat-value--success">{{ stats.finished || 0 }}</div>
          <div class="stat-label">已读完</div>
        </div>
        <div class="stat-item">
          <div class="stat-value stat-value--warning">{{ stats.reading || 0 }}</div>
          <div class="stat-label">在读</div>
        </div>
        <div class="stat-item">
          <div class="stat-value stat-value--muted">{{ stats.want_to_read || 0 }}</div>
          <div class="stat-label">想读</div>
        </div>
      </div>
    </section>

    <section class="shelf-age-section">
      <div class="shelf-age-card">
        <div class="age-icon" aria-hidden="true">📚</div>
        <div class="age-info">
          <p class="age-text">你的书架已经存在</p>
          <p class="age-value">{{ stats.shelf_age_days || 0 }} 天</p>
          <p v-if="stats.total_books" class="age-detail">
            {{ stats.shelf_age_days }} 天里，你放进了 {{ stats.total_books }} 本书
          </p>
          <p v-if="stats.finished" class="age-detail">
            其中 {{ stats.finished }} 本已经被你读完
          </p>
        </div>
      </div>
    </section>

    <section class="distribution-section">
      <h3 class="section-title">阅读状态分布</h3>
      <div class="distribution-bar" role="img" aria-label="阅读状态分布">
        <div
          class="bar-segment bar-segment--finished"
          :style="{ width: getPercentage(stats.finished) }"
          v-if="stats.finished"
        ></div>
        <div
          class="bar-segment bar-segment--reading"
          :style="{ width: getPercentage(stats.reading) }"
          v-if="stats.reading"
        ></div>
        <div
          class="bar-segment bar-segment--muted"
          :style="{ width: getPercentage(stats.want_to_read) }"
          v-if="stats.want_to_read"
        ></div>
      </div>
      <div class="distribution-legend">
        <span class="legend-item">
          <span class="legend-color legend-color--finished"></span> 已读 {{ getPercentage(stats.finished) }}
        </span>
        <span class="legend-item">
          <span class="legend-color legend-color--reading"></span> 在读 {{ getPercentage(stats.reading) }}
        </span>
        <span class="legend-item">
          <span class="legend-color legend-color--muted"></span> 想读 {{ getPercentage(stats.want_to_read) }}
        </span>
      </div>
    </section>

    <section class="recent-section" v-if="recentBooks.length > 0">
      <h3 class="section-title">最近阅读</h3>
      <div class="recent-list">
        <article
          v-for="book in recentBooks"
          :key="book.id"
          class="recent-item"
          tabindex="0"
          @click="$router.push(`/book/${book.id}`)"
          @keydown.enter="$router.push(`/book/${book.id}`)"
        >
          <div class="recent-cover">
            <img v-if="book.cover_image" :src="book.cover_image" :alt="book.title" />
            <div v-else class="cover-placeholder" :style="{ backgroundColor: getCoverColor(book.title) }">
              {{ book.title.charAt(0) }}
            </div>
          </div>
          <div class="recent-info">
            <h4 class="recent-title">{{ book.title }}</h4>
            <p class="recent-author">{{ book.author || '未知作者' }}</p>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../api/index'
import { useCoverColor } from '../composables/useCoverColor'

const { getCoverColor } = useCoverColor()
const stats = ref({})
const books = ref([])

const fetchStats = async () => {
  try {
    const response = await api.get('/bookshelf/statistics')
    stats.value = response.data
  } catch (error) {
    console.error('获取统计失败:', error)
  }
}

const fetchBooks = async () => {
  try {
    const response = await api.get('/bookshelf/books')
    books.value = response.data
  } catch (error) {
    console.error('获取书籍失败:', error)
  }
}

onMounted(() => {
  fetchStats()
  fetchBooks()
})

const recentBooks = computed(() => books.value.slice(0, 5))

const getPercentage = (value) => {
  if (!stats.value.total_books || !value) return '0%'
  return `${Math.round((value / stats.value.total_books) * 100)}%`
}
</script>

<style scoped>
.my-page {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--space-md) var(--space-md) calc(var(--space-md) + env(safe-area-inset-bottom));
}

@media (min-width: 768px) {
  .my-page {
    padding: var(--space-lg);
  }
}

.page-header {
  margin-bottom: var(--space-xl);
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  color: var(--color-text-primary);
}

@media (min-width: 480px) {
  .page-title {
    font-size: 28px;
  }
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-md);
}

/* ---- 统计卡片 ---- */
.stats-section {
  margin-bottom: var(--space-lg);
}

.stats-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-md);
  box-shadow: var(--shadow-sm);
}

@media (min-width: 480px) {
  .stats-card {
    grid-template-columns: repeat(4, 1fr);
    padding: var(--space-lg);
  }
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-primary);
  margin-bottom: var(--space-xs);
}

@media (min-width: 480px) {
  .stat-value {
    font-size: 28px;
  }
}

.stat-value--success { color: var(--color-success); }
.stat-value--warning { color: var(--color-warning); }
.stat-value--muted { color: var(--color-text-placeholder); }

.stat-label {
  font-size: 12px;
  color: var(--color-text-secondary);
}

/* ---- 书架年龄 ---- */
.shelf-age-section {
  margin-bottom: var(--space-lg);
}

.shelf-age-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
  display: flex;
  align-items: center;
  color: white;
  gap: var(--space-md);
}

@media (min-width: 480px) {
  .shelf-age-card {
    padding: var(--space-lg);
  }
}

.age-icon {
  font-size: 36px;
  flex-shrink: 0;
}

@media (min-width: 480px) {
  .age-icon {
    font-size: 48px;
  }
}

.age-text {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: var(--space-xs);
}

.age-value {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: var(--space-sm);
}

@media (min-width: 480px) {
  .age-value {
    font-size: 32px;
  }
}

.age-detail {
  font-size: 14px;
  opacity: 0.8;
}

/* ---- 阅读分布 ---- */
.distribution-section {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  margin-bottom: var(--space-lg);
  box-shadow: var(--shadow-sm);
}

.distribution-bar {
  height: 12px;
  background: var(--color-bg-hover);
  border-radius: var(--radius-full);
  overflow: hidden;
  display: flex;
  margin-bottom: var(--space-md);
}

.bar-segment {
  height: 100%;
  transition: width var(--transition-normal);
}

.bar-segment--finished { background: var(--color-primary); }
.bar-segment--reading { background: var(--color-success); }
.bar-segment--muted { background: var(--color-text-placeholder); }

.distribution-legend {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm) var(--space-md);
  font-size: 12px;
  color: var(--color-text-regular);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: var(--radius-sm);
}

.legend-color--finished { background: var(--color-primary); }
.legend-color--reading { background: var(--color-success); }
.legend-color--muted { background: var(--color-text-placeholder); }

/* ---- 最近阅读 ---- */
.recent-section {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  box-shadow: var(--shadow-sm);
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.recent-item {
  display: flex;
  align-items: center;
  padding: var(--space-sm);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.recent-item:hover {
  background: var(--color-bg-hover);
}

.recent-item:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.recent-cover {
  width: 48px;
  height: 64px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  margin-right: var(--space-md);
  flex-shrink: 0;
  box-shadow: var(--shadow-sm);
}

.recent-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: white;
  font-weight: 700;
}

.recent-info {
  flex: 1;
  min-width: 0;
}

.recent-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recent-author {
  font-size: 12px;
  color: var(--color-text-secondary);
}
</style>
