<template>
  <div class="my-page">
    <!-- 顶部导航 -->
    <header class="top-bar">
      <button class="back-btn" @click="$router.back()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>
      <DogEarLogo :show-text="false" />
    </header>

    <!-- 标题 -->
    <div class="page-title-section">
      <h1 class="page-title">我的阅读资产</h1>
      <p class="page-title-en">All My Reading Assets.</p>
    </div>

    <!-- 筛选标签 -->
    <div class="filter-tabs">
      <button
        v-for="tab in filterTabs"
        :key="tab"
        class="filter-tab"
        :class="{ 'filter-tab--active': activeFilter === tab }"
        @click="activeFilter = tab"
      >
        {{ tab }}
      </button>
    </div>

    <!-- 统计卡片 -->
    <section class="stats-section" v-if="activeFilter === '总览'">
      <div class="stats-grid">
        <div class="stat-card stat-card--total">
          <div class="stat-main">
            <span class="stat-number">{{ stats.total_books || 0 }}</span>
            <span class="stat-unit">本书</span>
          </div>
          <div class="stat-sub">截至 {{ currentDate }}</div>
          <div class="stat-chart">
            <div class="mini-bars">
              <div class="mini-bar" :style="{ height: '30%' }"></div>
              <div class="mini-bar" :style="{ height: '60%' }"></div>
              <div class="mini-bar" :style="{ height: '45%' }"></div>
              <div class="mini-bar" :style="{ height: '80%' }"></div>
            </div>
          </div>
        </div>

        <div class="stat-card stat-card--reading">
          <div class="stat-main">
            <span class="stat-number">{{ stats.reading || 0 }}</span>
            <span class="stat-unit">在读</span>
          </div>
          <div class="stat-icon">📖</div>
        </div>

        <div class="stat-card stat-card--want">
          <div class="stat-main">
            <span class="stat-number">{{ stats.want_to_read || 0 }}</span>
            <span class="stat-unit">想读</span>
          </div>
          <div class="stat-icon">🔖</div>
        </div>

        <div class="stat-card stat-card--finished">
          <div class="stat-main">
            <span class="stat-number">{{ stats.finished || 0 }}</span>
            <span class="stat-unit">已读</span>
          </div>
          <div class="stat-icon">✓</div>
        </div>
      </div>
    </section>

    <!-- 阅读类型分布 -->
    <section class="distribution-section" v-if="activeFilter === '总览'">
      <div class="section-header">
        <h3 class="section-title">阅读类型分布</h3>
        <button class="view-all-btn">查看全部 &rarr;</button>
      </div>
      <div class="distribution-bars">
        <div v-for="item in categoryDistribution" :key="item.name" class="dist-bar-item">
          <div class="dist-bar" :style="{ height: item.height + 'px', backgroundColor: item.color }"></div>
          <span class="dist-percent">{{ item.percent }}%</span>
          <span class="dist-name">{{ item.name }}</span>
        </div>
      </div>
    </section>

    <!-- 最近书单入口 -->
    <section class="booklist-entry" v-if="activeFilter === '总览'">
      <div class="booklist-card" @click="$router.push('/')">
        <div class="booklist-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>
          </svg>
        </div>
        <div class="booklist-info">
          <p class="booklist-text">书不是终点，<br/>而是不断靠近理想生活的线索。</p>
          <p class="booklist-author">— dog-ear</p>
        </div>
      </div>
      <button class="view-full-list-btn" @click="$router.push('/')">
        查看我的完整书单 &rarr;
      </button>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../api/index'
import DogEarLogo from '../components/DogEarLogo.vue'

const stats = ref({})
const books = ref([])
const activeFilter = ref('总览')
const filterTabs = ['总览', '时间', '类型', '关键词', '作者']

const currentDate = computed(() => {
  const d = new Date()
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`
})

// 模拟分类分布数据
const categoryDistribution = computed(() => {
  const total = stats.value.total_books || 1
  const categories = [
    { name: '个人成长', percent: 28, color: '#6B8E9B' },
    { name: '商业财经', percent: 21, color: '#8FB89A' },
    { name: '文学小说', percent: 16, color: '#D4A574' },
    { name: '心理', percent: 12, color: '#B8A88A' },
    { name: '科技', percent: 9, color: '#C9B8D4' },
    { name: '历史', percent: 8, color: '#D4B8A5' },
    { name: '其他', percent: 6, color: '#A5B8D4' },
  ]
  return categories.map(c => ({
    ...c,
    height: Math.max(20, c.percent * 1.5)
  }))
})

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
</script>

<style scoped>
.my-page {
  min-height: 100dvh;
  background: var(--color-bg-page);
  padding: var(--space-md);
  padding-bottom: calc(80px + env(safe-area-inset-bottom));
}

/* ---- 顶部导航 ---- */
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-sm) 0 var(--space-md);
}

.back-btn {
  background: none;
  border: none;
  color: var(--color-text-primary);
  cursor: pointer;
  padding: var(--space-xs);
}

/* ---- 页面标题 ---- */
.page-title-section {
  margin-bottom: var(--space-lg);
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: var(--space-xs);
}

.page-title-en {
  font-family: var(--font-handwriting);
  font-size: 14px;
  color: var(--color-text-muted);
}

/* ---- 筛选标签 ---- */
.filter-tabs {
  display: flex;
  gap: var(--space-sm);
  margin-bottom: var(--space-lg);
  overflow-x: auto;
  padding-bottom: var(--space-xs);
}

.filter-tab {
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-full);
  border: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: all var(--transition-fast);
  background: var(--color-bg-card);
  color: var(--color-text-secondary);
}

.filter-tab--active {
  background: var(--color-primary);
  color: var(--color-text-white);
}

/* ---- 统计卡片 ---- */
.stats-section {
  margin-bottom: var(--space-lg);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-md);
}

.stat-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  position: relative;
  overflow: hidden;
}

.stat-card--total {
  background: var(--color-bg-warm);
  grid-column: span 2;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.stat-main {
  display: flex;
  align-items: baseline;
  gap: var(--space-xs);
}

.stat-number {
  font-size: 36px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.stat-unit {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.stat-sub {
  font-size: 12px;
  color: var(--color-text-muted);
  margin-top: var(--space-xs);
}

.stat-chart {
  width: 80px;
  height: 50px;
}

.mini-bars {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  height: 100%;
}

.mini-bar {
  flex: 1;
  background: var(--color-text-primary);
  border-radius: 2px;
  opacity: 0.6;
}

.stat-card--reading,
.stat-card--want,
.stat-card--finished {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.stat-icon {
  font-size: 28px;
  opacity: 0.8;
}

/* ---- 阅读类型分布 ---- */
.distribution-section {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  margin-bottom: var(--space-lg);
  box-shadow: var(--shadow-card);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-lg);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.view-all-btn {
  background: none;
  border: none;
  font-size: 13px;
  color: var(--color-text-secondary);
  cursor: pointer;
}

.distribution-bars {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  height: 120px;
  padding-top: var(--space-md);
}

.dist-bar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.dist-bar {
  width: 100%;
  max-width: 40px;
  border-radius: 4px 4px 0 0;
  transition: height var(--transition-normal);
}

.dist-percent {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-top: var(--space-xs);
}

.dist-name {
  font-size: 11px;
  color: var(--color-text-muted);
}

/* ---- 书单入口 ---- */
.booklist-entry {
  margin-bottom: var(--space-lg);
}

.booklist-card {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  margin-bottom: var(--space-md);
  box-shadow: var(--shadow-card);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.booklist-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-float);
}

.booklist-icon {
  width: 48px;
  height: 48px;
  background: var(--color-bg-warm);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-primary);
  flex-shrink: 0;
}

.booklist-info {
  flex: 1;
}

.booklist-text {
  font-size: 14px;
  color: var(--color-text-primary);
  line-height: 1.6;
  margin-bottom: var(--space-xs);
}

.booklist-author {
  font-family: var(--font-handwriting);
  font-size: 12px;
  color: var(--color-text-muted);
}

.view-full-list-btn {
  width: 100%;
  padding: var(--space-md);
  background: var(--color-primary);
  color: var(--color-text-white);
  border: none;
  border-radius: var(--radius-full);
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: background var(--transition-fast);
}

.view-full-list-btn:hover {
  background: var(--color-primary-hover);
}
</style>
