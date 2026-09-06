<template>
  <div class="book-detail" v-if="book">
    <header class="page-header">
      <button class="btn btn--ghost" @click="$router.back()">← 返回</button>
      <button class="btn btn--danger-ghost" @click="deleteBook">删除</button>
    </header>

    <section class="book-cover-section">
      <div class="book-cover" :class="{ 'book-cover--dimmed': book.user_status === '想读' }">
        <img v-if="book.cover_image" :src="book.cover_image" :alt="book.title" />
        <div v-else class="cover-placeholder" :style="{ backgroundColor: getCoverColor(book.title) }">
          <span>{{ book.title.charAt(0) }}</span>
        </div>
      </div>
    </section>

    <section class="book-info-section">
      <h1 class="book-title">{{ book.title }}</h1>
      <p class="book-author">{{ book.author || '未知作者' }}</p>

      <div class="status-selector">
        <button
          v-for="status in ['想读', '在读', '已读']"
          :key="status"
          class="status-btn"
          :class="{ 'status-btn--active': book.user_status === status }"
          @click="updateStatus(status)"
        >
          {{ status }}
        </button>
      </div>

      <div class="book-meta" v-if="book.publisher || book.isbn">
        <div v-if="book.publisher" class="meta-item">
          <span class="meta-label">出版社</span>
          <span class="meta-value">{{ book.publisher }}</span>
        </div>
        <div v-if="book.publish_date" class="meta-item">
          <span class="meta-label">出版日期</span>
          <span class="meta-value">{{ book.publish_date }}</span>
        </div>
        <div v-if="book.isbn" class="meta-item">
          <span class="meta-label">ISBN</span>
          <span class="meta-value">{{ book.isbn }}</span>
        </div>
      </div>

      <div class="book-description" v-if="book.description">
        <h3>关于这本书</h3>
        <p>{{ book.description }}</p>
      </div>
    </section>

    <section class="records-section">
      <div class="section-header">
        <h2>我的阅读</h2>
        <button class="btn btn--primary btn--sm" @click="showAddRecord = true">+ 记一下</button>
      </div>

      <EmptyState
        v-if="records.length === 0"
        icon="📝"
        title="还没有阅读记录"
        description="开始记录你的阅读心得吧"
      />

      <div v-else class="records-list">
        <article v-for="record in records" :key="record.id" class="record-item">
          <time class="record-date">{{ formatDateTime(record.created_at) }}</time>
          <p v-if="record.content" class="record-content">{{ record.content }}</p>
          <blockquote v-if="record.excerpt" class="record-excerpt">"{{ record.excerpt }}"</blockquote>
          <div v-if="record.tags" class="record-tags">
            <span v-for="tag in record.tags.split(',')" :key="tag" class="tag">{{ tag.trim() }}</span>
          </div>
        </article>
      </div>
    </section>

    <Modal v-if="showAddRecord" title="记一下" @close="showAddRecord = false">
      <div class="form-group">
        <label for="record-content" class="form-label">今天读到哪里？</label>
        <input id="record-content" v-model="newRecord.content" placeholder="随便写点什么..." />
      </div>
      <div class="form-group">
        <label for="record-excerpt" class="form-label">摘录</label>
        <textarea id="record-excerpt" v-model="newRecord.excerpt" placeholder="喜欢的句子或段落..." rows="3"></textarea>
      </div>
      <div class="form-group">
        <label for="record-page" class="form-label">页码</label>
        <input id="record-page" v-model.number="newRecord.page_number" type="number" placeholder="第几页" />
      </div>
      <div class="form-group">
        <label for="record-tags" class="form-label">标签</label>
        <input id="record-tags" v-model="newRecord.tags" placeholder="用逗号分隔，如：感悟,摘录" />
      </div>

      <template #footer>
        <button class="btn btn--secondary" @click="showAddRecord = false">取消</button>
        <button class="btn btn--primary" :disabled="addingRecord" @click="addRecord">
          {{ addingRecord ? '保存中...' : '保存' }}
        </button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { formatDateTime } from '../utils/date'
import { useCoverColor } from '../composables/useCoverColor'
import Modal from '../components/Modal.vue'
import EmptyState from '../components/EmptyState.vue'

const { getCoverColor } = useCoverColor()
const route = useRoute()
const router = useRouter()
const book = ref(null)
const records = ref([])
const showAddRecord = ref(false)
const addingRecord = ref(false)
const newRecord = ref({ content: '', excerpt: '', page_number: null, tags: '' })

const fetchBook = async () => {
  try {
    const response = await axios.get(`/api/bookshelf/books/${route.params.id}`)
    book.value = response.data
  } catch (error) {
    console.error('获取书籍详情失败:', error)
    router.push('/')
  }
}

const fetchRecords = async () => {
  try {
    const response = await axios.get(`/api/bookshelf/books/${route.params.id}/records`)
    records.value = response.data
  } catch (error) {
    console.error('获取阅读记录失败:', error)
  }
}

onMounted(() => {
  fetchBook()
  fetchRecords()
})

const updateStatus = async (status) => {
  try {
    await axios.put(`/api/bookshelf/books/${book.value.id}/status`, null, { params: { status } })
    book.value.user_status = status
  } catch (error) {
    console.error('更新状态失败:', error)
  }
}

const deleteBook = async () => {
  if (!confirm('确定要删除这本书吗？')) return
  try {
    await axios.delete(`/api/bookshelf/books/${book.value.id}`)
    router.push('/')
  } catch (error) {
    console.error('删除书籍失败:', error)
  }
}

const addRecord = async () => {
  if (!newRecord.value.content && !newRecord.value.excerpt) {
    alert('请至少填写一项内容')
    return
  }
  addingRecord.value = true
  try {
    await axios.post(`/api/bookshelf/books/${book.value.id}/records`, newRecord.value)
    await fetchRecords()
    showAddRecord.value = false
    newRecord.value = { content: '', excerpt: '', page_number: null, tags: '' }
  } catch (error) {
    console.error('添加记录失败:', error)
    alert('保存失败，请重试')
  } finally {
    addingRecord.value = false
  }
}
</script>

<style scoped>
.book-detail {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--space-lg);
}

.page-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--space-lg);
}

.book-cover-section {
  text-align: center;
  margin-bottom: var(--space-xl);
}

.book-cover {
  display: inline-block;
  width: 200px;
  height: 280px;
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-lg);
}

.book-cover--dimmed {
  filter: grayscale(70%);
  opacity: 0.7;
}

.book-cover img {
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
  font-size: 64px;
  color: white;
  font-weight: 700;
}

.book-info-section {
  text-align: center;
  margin-bottom: var(--space-xl);
}

.book-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-sm);
}

.book-author {
  font-size: 16px;
  color: var(--color-text-regular);
  margin-bottom: var(--space-lg);
}

.status-selector {
  display: flex;
  justify-content: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-lg);
}

.status-btn {
  padding: var(--space-sm) var(--space-lg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  background: var(--color-bg-card);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-size: 14px;
  color: var(--color-text-regular);
}

.status-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.status-btn--active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.book-meta {
  display: flex;
  justify-content: center;
  gap: var(--space-lg);
  margin-bottom: var(--space-lg);
  flex-wrap: wrap;
}

.meta-item {
  font-size: 14px;
}

.meta-label {
  color: var(--color-text-secondary);
  margin-right: var(--space-sm);
}

.meta-value {
  color: var(--color-text-primary);
}

.book-description {
  text-align: left;
  background: var(--color-bg-page);
  padding: var(--space-md);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-xl);
}

.book-description h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-sm);
}

.book-description p {
  font-size: 14px;
  color: var(--color-text-regular);
  line-height: 1.6;
}

.records-section {
  margin-top: var(--space-xl);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.records-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.record-item {
  background: var(--color-bg-card);
  padding: var(--space-md);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.record-date {
  display: block;
  font-size: 12px;
  color: var(--color-text-placeholder);
  margin-bottom: var(--space-sm);
}

.record-content {
  font-size: 14px;
  color: var(--color-text-primary);
  line-height: 1.6;
  margin-bottom: var(--space-sm);
}

.record-excerpt {
  font-size: 14px;
  color: var(--color-text-regular);
  font-style: italic;
  padding-left: var(--space-md);
  border-left: 3px solid var(--color-primary);
  margin: 0 0 var(--space-sm) 0;
}

.record-tags {
  margin-top: var(--space-sm);
}

.tag {
  display: inline-block;
  background: var(--color-bg-hover);
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-sm);
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-right: var(--space-sm);
}

/* ---- 共用工具类 ---- */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
</style>
