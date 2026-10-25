<template>
  <view class="bookshelf-page">
    <!-- 顶部 Tab -->
    <view class="page-tabs">
      <view
        class="page-tab"
        :class="{ 'page-tab--active': activeTab === 'shelf' }"
        @tap="activeTab = 'shelf'"
      >我的书架</view>
      <view
        class="page-tab"
        :class="{ 'page-tab--active': activeTab === 'timeline' }"
        @tap="goToTimeline"
      >我的动态</view>
    </view>

    <!-- 书架内容 -->
    <view v-if="activeTab === 'shelf'" class="shelf-content">
      <!-- 工具栏 -->
      <view class="toolbar">
        <view class="book-count">
          <text class="count-num">{{ displayBooks.length }}</text>
          <text class="count-label">本书</text>
        </view>
        <view class="toolbar-actions">
          <view class="toolbar-btn" @tap="goToAddBook">
            <text class="toolbar-btn-icon">⊞</text>
            <text class="toolbar-btn-text">添加藏书</text>
          </view>
          <view class="toolbar-divider"></view>
          <view class="toolbar-btn" @tap="toggleManage">
            <text class="toolbar-btn-icon">{{ manageMode ? '✓' : '☰' }}</text>
            <text class="toolbar-btn-text">{{ manageMode ? '完成' : '管理' }}</text>
          </view>
        </view>
      </view>

      <!-- 搜索栏 -->
      <view class="search-bar" v-if="showSearch">
        <input
          class="search-input"
          v-model="searchText"
          placeholder="搜索书名或作者..."
          confirm-type="search"
          @confirm="onSearch"
          @input="onSearchInput"
        />
        <view class="search-clear" @tap="clearSearch">×</view>
      </view>

      <!-- 筛选标签 -->
      <view class="filter-tabs">
        <view
          class="filter-tab"
          :class="{ 'filter-tab--active': activeFilter === '' }"
          @tap="activeFilter = ''"
        >全部</view>
        <view
          class="filter-tab"
          :class="{ 'filter-tab--active': activeFilter === '在读' }"
          @tap="activeFilter = '在读'"
        >在读</view>
        <view
          class="filter-tab"
          :class="{ 'filter-tab--active': activeFilter === '想读' }"
          @tap="activeFilter = '想读'"
        >想读</view>
        <view
          class="filter-tab"
          :class="{ 'filter-tab--active': activeFilter === '已读' }"
          @tap="activeFilter = '已读'"
        >已读</view>
      </view>

      <!-- 空状态 -->
      <view v-if="!loading && displayBooks.length === 0" class="empty-state">
        <text class="empty-icon">📚</text>
        <text class="empty-title">{{ searchText ? '未找到匹配书籍' : '书架还是空的' }}</text>
        <text class="empty-hint">{{ searchText ? '换个关键词试试' : '点击「添加藏书」开始记录' }}</text>
      </view>

      <!-- 加载中 -->
      <view v-if="loading" class="loading">
        <view class="spinner"></view>
        <text>加载中...</text>
      </view>

      <!-- 书籍网格 -->
      <view v-else class="books-grid">
        <view
          class="book-item"
          v-for="book in displayBooks"
          :key="book.id"
          @tap="manageMode ? toggleSelect(book) : goToBookDetail(book.id)"
        >
          <!-- 管理模式选择框 -->
          <view v-if="manageMode" class="book-checkbox">
            <view class="checkbox" :class="{ 'checkbox--checked': selectedIds.includes(book.id) }">
              <text v-if="selectedIds.includes(book.id)">✓</text>
            </view>
          </view>

          <!-- 封面 -->
          <view class="book-cover">
            <image
              v-if="book.cover_image"
              :src="resolveImageUrl(book.cover_image)"
              class="cover-img"
              mode="aspectFill"
            />
            <view v-else class="cover-placeholder" :style="{ backgroundColor: getCoverColor(book.title) }">
              <text class="cover-initial">{{ book.title[0] }}</text>
            </view>
          </view>

          <!-- 标题 -->
          <text class="book-title">{{ book.title }}</text>
        </view>
      </view>

      <!-- 管理模式底部操作栏 -->
      <view v-if="manageMode && selectedIds.length > 0" class="manage-bar">
        <text class="manage-count">已选 {{ selectedIds.length }} 本</text>
        <view class="manage-actions">
          <button class="manage-btn manage-btn--danger" @tap="deleteSelected">删除</button>
        </view>
      </view>
    </view>

    <!-- 搜索浮动按钮 -->
    <view class="search-fab" @tap="toggleSearch" v-if="!manageMode">
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

const toast = useToast()
const books = ref([])
const loading = ref(true)
const searchText = ref('')
const showSearch = ref(false)
const activeFilter = ref('')
const activeTab = ref('shelf')
const manageMode = ref(false)
const selectedIds = ref([])

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

function goToBookDetail(id) {
  uni.navigateTo({ url: `/pages/book-detail/book-detail?id=${id}` })
}

function goToAddBook() {
  uni.navigateTo({ url: '/pages/add-book/add-book' })
}

function goToTimeline() {
  activeTab.value = 'timeline'
  uni.switchTab({ url: '/pages/records/records' })
}

function toggleManage() {
  manageMode.value = !manageMode.value
  if (!manageMode.value) {
    selectedIds.value = []
  }
}

function toggleSelect(book) {
  const idx = selectedIds.value.indexOf(book.id)
  if (idx >= 0) {
    selectedIds.value.splice(idx, 1)
  } else {
    selectedIds.value.push(book.id)
  }
}

async function deleteSelected() {
  if (selectedIds.value.length === 0) return
  uni.showModal({
    title: '确认删除',
    content: `确定要删除选中的 ${selectedIds.value.length} 本书吗？`,
    success: async (res) => {
      if (res.confirm) {
        try {
          for (const id of selectedIds.value) {
            await api.deleteBook(id)
          }
          toast.success('删除成功')
          selectedIds.value = []
          manageMode.value = false
          loadBooks()
        } catch (err) {
          console.error('删除失败:', err)
          toast.error('删除失败')
        }
      }
    }
  })
}

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
  background: #FFFFFF;
  padding-bottom: 20px;
}

/* 顶部 Tab */
.page-tabs {
  display: flex;
  justify-content: center;
  gap: 32px;
  padding: 16px 0 12px;
  background: #FFFFFF;
  border-bottom: 1px solid #F5F5F5;
}

.page-tab {
  font-size: 16px;
  color: #999;
  padding-bottom: 8px;
  border-bottom: 2px solid transparent;
}

.page-tab--active {
  color: #1A1A1A;
  font-weight: 600;
  border-bottom-color: #1A1A1A;
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 16px 8px;
}

.book-count {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.count-num {
  font-size: 22px;
  font-weight: 700;
  color: #1A1A1A;
}

.count-label {
  font-size: 13px;
  color: #999;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border: 1px solid #E5E5E5;
  border-radius: 20px;
  background: #FFF;
}

.toolbar-btn-icon {
  font-size: 14px;
  color: #333;
}

.toolbar-btn-text {
  font-size: 13px;
  color: #333;
}

.toolbar-divider {
  width: 1px;
  height: 16px;
  background: #E5E5E5;
}

/* 搜索栏 */
.search-bar {
  display: flex;
  align-items: center;
  background: #F5F5F5;
  border-radius: 8px;
  padding: 8px 12px;
  margin: 8px 16px;
}

.search-input {
  flex: 1;
  font-size: 14px;
  color: #333;
}

.search-clear {
  font-size: 18px;
  color: #999;
  padding: 0 4px;
}

/* 筛选标签 */
.filter-tabs {
  display: flex;
  gap: 8px;
  padding: 8px 16px;
  overflow-x: auto;
}

.filter-tab {
  padding: 4px 12px;
  border-radius: 14px;
  font-size: 12px;
  background: #F5F5F5;
  color: #666;
  white-space: nowrap;
}

.filter-tab--active {
  background: #1A1A1A;
  color: #FFF;
}

/* 书籍网格 */
.books-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  padding: 8px 16px;
}

.book-item {
  position: relative;
}

.book-cover {
  width: 100%;
  padding-top: 133.33%; /* 4:3 ratio */
  position: relative;
  border-radius: 6px;
  overflow: hidden;
  background: #F5F5F5;
}

.cover-img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.cover-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cover-initial {
  font-size: 28px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 700;
}

.book-title {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  color: #333;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 管理模式选择框 */
.book-checkbox {
  position: absolute;
  top: 6px;
  left: 6px;
  z-index: 10;
}

.checkbox {
  width: 22px;
  height: 22px;
  border: 2px solid #FFF;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFF;
  font-size: 12px;
}

.checkbox--checked {
  background: #E74C3C;
  border-color: #FFF;
}

/* 管理模式底部操作栏 */
.manage-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #FFF;
  border-top: 1px solid #F0F0F0;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.06);
}

.manage-count {
  font-size: 14px;
  color: #666;
}

.manage-btn {
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 14px;
  border: none;
}

.manage-btn--danger {
  background: #E74C3C;
  color: #FFF;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 16px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.empty-hint {
  font-size: 13px;
  color: #999;
}

/* 加载 */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  color: #999;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid #E5E5E5;
  border-top-color: #1A1A1A;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 搜索浮动按钮 */
.search-fab {
  position: fixed;
  bottom: 24px;
  right: 20px;
  width: 44px;
  height: 44px;
  background: #1A1A1A;
  color: #FFF;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}
</style>
