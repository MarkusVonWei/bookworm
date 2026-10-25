<template>
  <view class="book-detail-page">
    <!-- 顶部导航 -->
    <view class="top-bar">
      <view class="back-btn" @tap="goBack">←</view>
      <view class="delete-btn" @tap="deleteBook">删除</view>
    </view>

    <!-- 书籍封面 -->
    <view class="book-cover-section">
      <view class="book-cover" :class="{ 'book-cover--dimmed': book && book.user_status === '想读' }">
        <image v-if="book && book.cover_image" :src="resolveImageUrl(book.cover_image)" class="cover-image" mode="aspectFill" />
        <view v-else class="cover-placeholder" :style="{ backgroundColor: coverColor }">
          <text class="placeholder-text">{{ book ? book.title[0] : '?' }}</text>
        </view>
      </view>
    </view>

    <!-- 书籍信息 -->
    <view class="book-info-section" v-if="book">
      <text class="book-title">{{ book.title }}</text>
      <text class="book-author">{{ book.author || '未知作者' }}</text>

      <!-- 状态选择 -->
      <view class="status-selector">
        <view
          class="status-btn"
          :class="{ 'status-btn--active': book.user_status === status }"
          v-for="status in ['想读', '在读', '已读']"
          :key="status"
          @tap="changeStatus(status)"
        >
          {{ status }}
        </view>
      </view>

      <!-- 书籍元信息 -->
      <view class="book-meta" v-if="book.publisher || book.isbn">
        <view class="meta-item" v-if="book.publisher">
          <text class="meta-label">出版社</text>
          <text class="meta-value">{{ book.publisher }}</text>
        </view>
        <view class="meta-item" v-if="book.isbn">
          <text class="meta-label">ISBN</text>
          <text class="meta-value">{{ book.isbn }}</text>
        </view>
      </view>

      <!-- 书籍简介 -->
      <view class="book-description" v-if="book.description">
        <text class="desc-title">简介</text>
        <text class="desc-content">{{ book.description }}</text>
      </view>
    </view>

    <!-- 阅读记录 -->
    <view class="records-section">
      <view class="section-header">
        <text class="section-title">我的阅读</text>
        <view class="btn btn--primary btn--sm" @tap="showAddRecordModal">+ 记一下</view>
      </view>

      <!-- 空记录 -->
      <view v-if="records.length === 0 && !loading" class="empty-state">
        <text class="empty-icon">📝</text>
        <text class="empty-title">还没有阅读记录</text>
        <text class="empty-hint">开始记录你的阅读心得吧</text>
      </view>

      <!-- 记录列表 -->
      <view v-else class="records-list">
        <view class="record-item" v-for="record in records" :key="record.id">
          <text class="record-date">{{ record.formattedDate }}</text>
          <text class="record-content" v-if="record.content">{{ record.content }}</text>
          <view class="record-excerpt-wrap" v-if="record.excerpt">
            <text class="record-excerpt">"{{ record.excerpt }}"</text>
          </view>
          <view class="record-tags" v-if="record.tags">
            <text class="tag" v-for="tag in parseTags(record.tags)" :key="tag">{{ tag }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 添加记录弹窗 -->
    <view class="modal-mask" v-if="showAddRecord" @tap="closeAddRecordModal">
      <view class="modal-content" @tap.stop>
        <view class="modal-header">
          <text class="modal-title">记一下</text>
          <view class="modal-close" @tap="closeAddRecordModal">×</view>
        </view>

        <view class="modal-body">
          <view class="form-group">
            <text class="form-label">今天读到哪里？</text>
            <input class="form-input" v-model="newRecord.content" placeholder="随便写点什么..." />
          </view>
          <view class="form-group">
            <text class="form-label">摘录</text>
            <textarea class="form-textarea" v-model="newRecord.excerpt" placeholder="喜欢的句子或段落..." />
          </view>
          <view class="form-group">
            <text class="form-label">页码</text>
            <input class="form-input" v-model="newRecord.page_number" type="number" placeholder="第几页" />
          </view>
          <view class="form-group">
            <text class="form-label">标签</text>
            <input class="form-input" v-model="newRecord.tags" placeholder="用逗号分隔，如：感悟,摘录" />
          </view>
        </view>

        <view class="modal-footer">
          <button class="btn btn--ghost" @tap="closeAddRecordModal">取消</button>
          <button class="btn btn--primary" :disabled="addingRecord" @tap="addRecord">
            {{ addingRecord ? '保存中...' : '保存' }}
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import * as api from '../../api/index'
import { formatDateTime } from '../../utils/date'
import { getCoverColor, resolveImageUrl } from '../../utils/coverColor'
import { useToast } from '../../composables/useToast'

const toast = useToast()
const book = ref(null)
const records = ref([])
const loading = ref(true)
const showAddRecord = ref(false)
const addingRecord = ref(false)
const newRecord = ref({ content: '', excerpt: '', page_number: null, tags: '' })

const coverColor = computed(() => getCoverColor(book.value?.title))

function parseTags(tags) {
  return (tags || '').split(',').map(t => t.trim()).filter(Boolean)
}

function goBack() {
  uni.navigateBack()
}

async function loadBook(bookId) {
  loading.value = true
  try {
    book.value = await api.getBook(bookId)
  } catch (err) {
    console.error('加载书籍失败:', err)
    toast.error('加载失败')
  } finally {
    loading.value = false
  }
}

async function loadRecords(bookId) {
  try {
    const data = await api.getReadingRecords(bookId)
    records.value = (data || []).map(r => ({
      ...r,
      formattedDate: formatDateTime(r.created_at)
    }))
  } catch (err) {
    console.error('加载记录失败:', err)
  }
}

async function changeStatus(status) {
  if (!book.value) return
  try {
    await api.updateBookStatus(book.value.id, status)
    book.value.user_status = status
    toast.success('状态已更新')
  } catch (err) {
    console.error('更新状态失败:', err)
    toast.error('更新失败')
  }
}

function deleteBook() {
  if (!book.value) return
  uni.showModal({
    title: '确认删除',
    content: '确定要删除这本书吗？删除后无法恢复。',
    success: async (res) => {
      if (res.confirm) {
        try {
          await api.deleteBook(book.value.id)
          toast.success('删除成功')
          setTimeout(() => uni.navigateBack(), 1500)
        } catch (err) {
          console.error('删除失败:', err)
          toast.error('删除失败')
        }
      }
    }
  })
}

function showAddRecordModal() {
  showAddRecord.value = true
}

function closeAddRecordModal() {
  showAddRecord.value = false
  newRecord.value = { content: '', excerpt: '', page_number: null, tags: '' }
}

async function addRecord() {
  if (!book.value) return
  const r = newRecord.value
  if (!r.content && !r.excerpt) {
    toast.warning('请至少填写一项内容')
    return
  }

  addingRecord.value = true
  try {
    await api.createReadingRecord(book.value.id, {
      content: r.content,
      excerpt: r.excerpt,
      page_number: (r.page_number && r.page_number !== '') ? Number(r.page_number) : null,
      tags: r.tags
    })
    toast.success('记录成功')
    closeAddRecordModal()
    loadRecords(book.value.id)
  } catch (err) {
    console.error('添加记录失败:', err)
    toast.error('保存失败，请重试')
  } finally {
    addingRecord.value = false
  }
}

onLoad((options) => {
  const bookId = options?.id
  if (bookId) {
    loadBook(bookId)
    loadRecords(bookId)
  }
})
</script>

<style scoped>
.book-detail-page {
  min-height: 100vh;
  background: var(--color-bg-page);
  padding: 12px 16px 32px;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.back-btn {
  font-size: 20px;
  color: var(--color-text-primary);
  padding: 8px;
}

.delete-btn {
  font-size: 14px;
  color: var(--color-danger);
  padding: 8px;
}

/* 封面 */
.book-cover-section {
  text-align: center;
  margin-bottom: 24px;
}

.book-cover {
  display: inline-block;
  width: 160px;
  height: 224px;
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-float);
}

.book-cover--dimmed {
  filter: grayscale(70%);
  opacity: 0.7;
}

.cover-image {
  width: 100%;
  height: 100%;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-text {
  font-size: 48px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 700;
}

/* 书籍信息 */
.book-info-section {
  text-align: center;
  margin-bottom: 24px;
}

.book-title {
  display: block;
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 4px;
}

.book-author {
  display: block;
  font-size: 15px;
  color: var(--color-text-secondary);
  margin-bottom: 16px;
}

.status-selector {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 16px;
}

.status-btn {
  padding: 8px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  background: var(--color-bg-card);
  color: var(--color-text-secondary);
  font-size: 13px;
}

.status-btn--active {
  background: var(--color-primary);
  color: var(--color-text-white);
  border-color: var(--color-primary);
}

.book-meta {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.meta-item {
  font-size: 13px;
}

.meta-label {
  color: var(--color-text-secondary);
  margin-right: 4px;
}

.meta-value {
  color: var(--color-text-primary);
}

.book-description {
  text-align: left;
  background: var(--color-bg-soft);
  padding: 12px;
  border-radius: var(--radius-md);
}

.desc-title {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 8px;
}

.desc-content {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

/* 阅读记录 */
.records-section {
  margin-top: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.btn--sm {
  padding: 6px 12px;
  font-size: 12px;
}

.records-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.record-item {
  background: var(--color-bg-card);
  padding: 12px;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
}

.record-date {
  display: block;
  font-size: 12px;
  color: var(--color-text-muted);
  margin-bottom: 8px;
}

.record-content {
  font-size: 14px;
  color: var(--color-text-primary);
  line-height: 1.6;
  margin-bottom: 8px;
}

.record-excerpt-wrap {
  padding-left: 12px;
  border-left: 3px solid var(--color-primary);
  margin-bottom: 8px;
}

.record-excerpt {
  font-size: 13px;
  color: var(--color-text-secondary);
  font-style: italic;
}

.record-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 8px;
}

.tag {
  display: inline-block;
  background: var(--color-bg-warm);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: 11px;
  color: var(--color-text-secondary);
}

/* 弹窗 */
.modal-mask {
  position: fixed;
  inset: 0;
  background: var(--color-bg-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

.modal-content {
  background: var(--color-bg-card);
  border-radius: var(--radius-xl);
  width: 100%;
  max-width: 400px;
  max-height: 85vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--color-border-light);
}

.modal-title {
  font-size: 17px;
  font-weight: 600;
}

.modal-close {
  font-size: 22px;
  color: var(--color-text-muted);
  padding: 4px 8px;
}

.modal-body {
  padding: 16px;
}

.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}

.form-input {
  width: 100%;
  height: 44px;
  padding: 0 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  background: var(--color-bg-soft);
  box-sizing: border-box;
}

.form-textarea {
  width: 100%;
  min-height: 80px;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  background: var(--color-bg-soft);
  box-sizing: border-box;
}

.modal-footer {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid var(--color-border-light);
}

.modal-footer .btn {
  flex: 1;
}
</style>
