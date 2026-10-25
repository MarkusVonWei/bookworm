<template>
  <view class="my-page">
    <!-- 标题 -->
    <view class="page-title-section">
      <text class="page-title">我的阅读资产</text>
      <text class="page-title-en">All My Reading Assets.</text>
    </view>

    <!-- 筛选标签 -->
    <view class="filter-tabs">
      <view
        class="filter-tab"
        :class="{ 'filter-tab--active': activeFilter === tab }"
        v-for="tab in filterTabs"
        :key="tab"
        @tap="activeFilter = tab"
      >
        {{ tab }}
      </view>
    </view>

    <!-- 统计卡片 -->
    <view class="stats-section" v-if="activeFilter === '总览'">
      <view class="stats-grid">
        <!-- 总计 -->
        <view class="stat-card stat-card--total">
          <view>
            <view class="stat-main">
              <text class="stat-number">{{ statistics.total_books || 0 }}</text>
              <text class="stat-unit">本书</text>
            </view>
            <text class="stat-sub">截至 {{ currentDate }}</text>
          </view>
        </view>

        <!-- 在读 -->
        <view class="stat-card">
          <view class="stat-main">
            <text class="stat-number">{{ statistics.reading || 0 }}</text>
            <text class="stat-unit">在读</text>
          </view>
          <text class="stat-icon">📖</text>
        </view>

        <!-- 想读 -->
        <view class="stat-card">
          <view class="stat-main">
            <text class="stat-number">{{ statistics.want_to_read || 0 }}</text>
            <text class="stat-unit">想读</text>
          </view>
          <text class="stat-icon">🔖</text>
        </view>

        <!-- 已读 -->
        <view class="stat-card">
          <view class="stat-main">
            <text class="stat-number">{{ statistics.finished || 0 }}</text>
            <text class="stat-unit">已读</text>
          </view>
          <text class="stat-icon">✓</text>
        </view>
      </view>
    </view>

    <!-- 状态书籍列表 -->
    <view class="status-books-section" v-if="activeFilter !== '总览'">
      <view v-if="filteredBooks.length === 0" class="empty-state">
        <text class="empty-icon">📚</text>
        <text class="empty-title">暂无{{ activeFilter }}书籍</text>
      </view>
      <view v-else class="status-books-list">
        <view
          class="status-book-item"
          v-for="book in filteredBooks"
          :key="book.id"
          @tap="goToBook(book.id)"
        >
          <view class="book-cover-sm" :style="{ backgroundColor: getCoverColor(book.title) }">
            <text class="cover-initial">{{ book.title[0] }}</text>
          </view>
          <view class="book-info-sm">
            <text class="book-title-sm">{{ book.title }}</text>
            <text class="book-author-sm">{{ book.author || '未知作者' }}</text>
          </view>
          <text class="book-arrow">→</text>
        </view>
      </view>
    </view>

    <!-- 书单入口 -->
    <view class="booklist-entry" v-if="activeFilter === '总览'">
      <view class="booklist-card" @tap="goToBookshelf">
        <text class="booklist-icon">📖</text>
        <view class="booklist-info">
          <text class="booklist-text">书不是终点，\n而是不断靠近理想生活的线索。</text>
          <text class="booklist-author">— dog-ear</text>
        </view>
      </view>
      <button class="btn btn--primary full-btn" @tap="goToBookshelf">查看我的完整书单 →</button>
    </view>

    <!-- 个人中心入口 -->
    <view class="profile-entry" @tap="goToProfile">
      <view class="profile-entry-card">
        <text class="profile-entry-icon">👤</text>
        <view class="profile-entry-info">
          <text class="profile-entry-title">个人中心</text>
          <text class="profile-entry-hint">登录 / 注册 / 账号设置</text>
        </view>
        <text class="profile-entry-arrow">→</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onShow, onLoad } from '@dcloudio/uni-app'
import * as api from '../../api/index'
import { getCoverColor } from '../../utils/coverColor'

const statistics = ref({})
const books = ref([])
const activeFilter = ref('总览')
const filterTabs = ['总览', '在读', '想读', '已读']
const currentDate = computed(() => {
  const d = new Date()
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`
})

const filteredBooks = computed(() => {
  if (activeFilter.value === '总览') return []
  return books.value.filter(b => b.user_status === activeFilter.value)
})

async function loadStats() {
  try {
    statistics.value = await api.getStatistics()
  } catch (err) {
    console.error('加载统计失败:', err)
  }
}

async function loadBooks() {
  try {
    const data = await api.getBooks()
    books.value = Array.isArray(data) ? data : []
  } catch (err) {
    console.error('加载书籍失败:', err)
  }
}

function goToBook(id) {
  uni.navigateTo({ url: `/pages/book-detail/book-detail?id=${id}` })
}

function goToProfile() {
  uni.navigateTo({ url: '/pages/profile/profile' })
}

function goToBookshelf() {
  uni.switchTab({ url: '/pages/bookshelf/bookshelf' })
}

onLoad((options) => {
  if (options?.filter) {
    activeFilter.value = options.filter
  }
})

onMounted(() => {
  loadStats()
  loadBooks()
})

onShow(() => {
  loadStats()
  loadBooks()
})
</script>

<style scoped>
.my-page {
  min-height: 100vh;
  background: var(--color-bg-page);
  padding: 12px 16px 32px;
}

.page-title-section {
  margin-bottom: 16px;
}

.page-title {
  display: block;
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 2px;
}

.page-title-en {
  font-size: 13px;
  color: var(--color-text-muted);
  font-style: italic;
}

/* 筛选标签 */
.filter-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.filter-tab {
  padding: 6px 14px;
  border-radius: var(--radius-full);
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  background: var(--color-bg-card);
  color: var(--color-text-secondary);
}

.filter-tab--active {
  background: var(--color-primary);
  color: var(--color-text-white);
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.stat-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.stat-card--total {
  grid-column: span 2;
  background: var(--color-bg-warm);
  align-items: flex-end;
}

.stat-main {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.stat-unit {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.stat-sub {
  display: block;
  font-size: 11px;
  color: var(--color-text-muted);
  margin-top: 4px;
}

.stat-icon {
  font-size: 24px;
  opacity: 0.8;
}

/* 状态书籍列表 */
.status-books-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.status-book-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
}

.book-cover-sm {
  width: 40px;
  height: 56px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.cover-initial {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 700;
}

.book-info-sm {
  flex: 1;
  min-width: 0;
}

.book-title-sm {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-author-sm {
  display: block;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.book-arrow {
  color: var(--color-text-muted);
}

/* 书单入口 */
.booklist-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: var(--shadow-card);
}

.booklist-icon {
  font-size: 32px;
  width: 48px;
  height: 48px;
  background: var(--color-bg-warm);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.booklist-info {
  flex: 1;
}

.booklist-text {
  display: block;
  font-size: 13px;
  color: var(--color-text-primary);
  line-height: 1.6;
  margin-bottom: 4px;
}

.booklist-author {
  display: block;
  font-size: 12px;
  color: var(--color-text-muted);
  font-style: italic;
}

.full-btn {
  width: 100%;
}
/* 个人中心入口 */
.profile-entry {
  margin-top: 12px;
}

.profile-entry-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}

.profile-entry-icon {
  font-size: 24px;
}

.profile-entry-info {
  flex: 1;
}

.profile-entry-title {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.profile-entry-hint {
  display: block;
  font-size: 12px;
  color: var(--color-text-muted);
}

.profile-entry-arrow {
  color: var(--color-text-muted);
}

</style>
