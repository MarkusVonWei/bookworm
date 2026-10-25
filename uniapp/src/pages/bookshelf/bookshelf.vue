<template>
  <view class="bookshelf-page">
    <!-- 搜索栏 -->
    <view class="search-bar" v-if="showSearch">
      <input
        class="search-input"
        v-model="searchText"
        placeholder="搜索书籍..."
        confirm-type="search"
        @confirm="onSearch"
        @input="onSearchInput"
      />
      <view class="search-clear" @tap="clearSearch">×</view>
    </view>

    <!-- 状态入口 -->
    <view class="status-entries">
      <view
        class="status-entry"
        v-for="entry in statusEntries"
        :key="entry.status"
        @tap="filterByStatus(entry.status)"
      >
        <text class="status-icon">{{ entry.icon }}</text>
        <text class="status-name">{{ entry.status }}</text>
        <text class="status-count">{{ entry.count }}</text>
        <text class="status-arrow">→</text>
      </view>
    </view>

    <!-- 书籍列表 -->
    <view class="section-header">
      <text class="section-title">{{ activeFilter || '全部书籍' }}</text>
      <text class="section-count">{{ displayBooks.length }}本</text>
    </view>

    <!-- 空状态 -->
    <view v-if="!loading && displayBooks.length === 0" class="empty-state">
      <text class="empty-icon">📚</text>
      <text class="empty-title">{{ searchText ? '未找到匹配书籍' : '书架还是空的' }}</text>
      <text class="empty-hint">{{ searchText ? '换个关键词试试' : '点击下方按钮添加第一本书' }}</text>
    </view>

    <!-- 加载中 -->
    <view v-if="loading" class="loading">
      <view class="spinner"></view>
      <text>加载中...</text>
    </view>

    <!-- 书籍网格 -->
    <view v-else class="books-grid">
      <view
        class="book-card"
        v-for="book in displayBooks"
        :key="book.id"
        @tap="goToBookDetail(book.id)"
      >
        <view class="book-cover-wrap">
          <image
            v-if="book.cover_image"
            :src="resolveImageUrl(book.cover_image)"
            class="book-cover-img"
            mode="aspectFit"
          />
          <view v-else class="book-cover-placeholder" :style="{ backgroundColor: getCoverColor(book.title) }">
            <text class="placeholder-text">{{ book.title[0] }}</text>
          </view>
        </view>
        <view class="book-card-info">
          <text class="book-card-title">{{ book.title }}</text>
          <text class="book-card-author" v-if="book.author">{{ book.author }}</text>
          <view class="book-status-tag" :class="'status-' + statusClass(book.user_status)">
            <text>{{ book.user_status }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 快速记录入口 -->
    <view class="quick-record" @tap="goToAddBook">
      <text class="quick-record-icon">📷</text>
      <view class="quick-record-info">
        <text class="quick-record-title">快速记录</text>
        <text class="quick-record-hint">拍照 / 搜索 / 手动添加</text>
      </view>
      <text class="quick-record-arrow">→</text>
    </view>

    <!-- 搜索按钮 -->
    <view class="search-fab" @tap="toggleSearch">
      <text>🔍</text>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onShow, onPullDownRefresh } from '@dcloudio/uni-app'
import * as api from '../../api/index'
import { getCoverColor, resolveImageUrl } from '../../utils/coverColor'
import { useToast } from '../../composables/useToast'

function statusClass(status) {
  const map = { '想读': 'want', '在读': 'reading', '已读': 'finished' }
  return map[status] || 'want'
}

const toast = useToast()
const books = ref([])
const loading = ref(true)
const searchText = ref('')
const showSearch = ref(false)
const activeFilter = ref('')

// 状态统计
const statusEntries = computed(() => {
  const counts = { '想读': 0, '在读': 0, '已读': 0 }
  books.value.forEach(b => {
    if (counts[b.user_status] !== undefined) counts[b.user_status]++
  })
  return [
    { status: '在读', count: counts['在读'], icon: '👁️' },
    { status: '想读', count: counts['想读'], icon: '🔖' },
    { status: '已读', count: counts['已读'], icon: '✓' },
  ]
})

// 展示的书籍
const displayBooks = computed(() => {
  let list = books.value
  if (activeFilter.value) {
    list = list.filter(b => b.user_status === activeFilter.value)
  }
  if (searchText.value) {
    const kw = searchText.value.toLowerCase()
    list = list.filter(b =>
      (b.title || '').toLowerCase().includes(kw) ||
      (b.author || '').toLowerCase().includes(kw)
    )
  }
  return list
})

// 加载书籍列表
async function loadBooks() {
  loading.value = true
  try {
    const data = await api.getBooks()
    books.value = Array.isArray(data) ? data : []
  } catch (err) {
    console.error('加载书籍失败:', err)
    toast.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 跳转到书籍详情
function goToBookDetail(id) {
  uni.navigateTo({ url: `/pages/book-detail/book-detail?id=${id}` })
}

// 跳转到添加书籍
function goToAddBook() {
  uni.navigateTo({ url: '/pages/add-book/add-book' })
}

// 按状态筛选
function filterByStatus(status) {
  activeFilter.value = activeFilter.value === status ? '' : status
}

// 搜索
function onSearch() {
  // 搜索通过 displayBooks computed 实时过滤
}

function onSearchInput() {
  // 实时过滤
}

function clearSearch() {
  searchText.value = ''
}

function toggleSearch() {
  showSearch.value = !showSearch.value
  if (!showSearch.value) clearSearch()
}

// 生命周期
onMounted(() => loadBooks())
onShow(() => loadBooks())
onPullDownRefresh(async () => {
  await loadBooks()
  uni.stopPullDownRefresh()
})
</script>

<style scoped>
.bookshelf-page {
  min-height: 100vh;
  background: var(--color-bg-page);
  padding: 12px 16px 100px;
}

/* 搜索栏 */
.search-bar {
  display: flex;
  align-items: center;
  background: var(--color-bg-card);
  border-radius: var(--radius-full);
  padding: 8px 16px;
  margin-bottom: 16px;
  box-shadow: var(--shadow-card);
}

.search-input {
  flex: 1;
  font-size: 14px;
  color: var(--color-text-primary);
}

.search-clear {
  font-size: 20px;
  color: var(--color-text-muted);
  padding: 0 8px;
}

/* 状态入口 */
.status-entries {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.status-entry {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}

.status-icon {
  font-size: 18px;
}

.status-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.status-count {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-left: auto;
}

.status-arrow {
  font-size: 16px;
  color: var(--color-text-muted);
}

/* 区域标题 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.section-count {
  font-size: 12px;
  color: var(--color-text-muted);
}

/* 书籍网格 */
.books-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.book-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-book);
}

.book-cover-wrap {
  width: 100%;
  height: 160px;
}

.book-cover-img {
  width: 100%;
  height: 100%;
}

.book-cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-warm);
}

.placeholder-text {
  font-size: 32px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 700;
}

.book-card-info {
  padding: 8px;
}

.book-card-title {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-card-author {
  display: block;
  font-size: 11px;
  color: var(--color-text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-status-tag {
  display: inline-block;
  margin-top: 4px;
  padding: 1px 6px;
  border-radius: var(--radius-sm);
  font-size: 10px;
}

.status-want {
  background: var(--color-bg-warm);
  color: var(--color-text-secondary);
}

.status-reading {
  background: var(--color-primary);
  color: var(--color-text-white);
}

.status-finished {
  background: var(--color-finished);
  color: var(--color-text-white);
}

/* 快速记录 */
.quick-record {
  position: fixed;
  bottom: 70px;
  left: 16px;
  right: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--color-bg-card);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-float);
}

.quick-record-icon {
  width: 40px;
  height: 40px;
  background: var(--color-bg-warm);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.quick-record-info {
  flex: 1;
}

.quick-record-title {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.quick-record-hint {
  display: block;
  font-size: 11px;
  color: var(--color-text-muted);
}

.quick-record-arrow {
  font-size: 16px;
  color: var(--color-text-muted);
}

/* 搜索浮动按钮 */
.search-fab {
  position: fixed;
  bottom: 130px;
  right: 20px;
  width: 44px;
  height: 44px;
  background: var(--color-primary);
  color: var(--color-text-white);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  box-shadow: var(--shadow-float);
}
</style>
