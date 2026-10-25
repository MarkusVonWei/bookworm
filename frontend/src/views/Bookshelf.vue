<template>
  <div class="bookshelf">
    <!-- 顶部栏 -->
    <header class="top-bar">
      <DogEarLogo :show-text="true" />
      <div class="top-actions">
        <button class="icon-btn" @click="showSearch = !showSearch" aria-label="搜索">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.35-4.35"/>
          </svg>
        </button>
        <button class="icon-btn icon-btn--primary" @click="showAddModal = true" aria-label="添加书籍">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M12 5v14M5 12h14"/>
          </svg>
        </button>
      </div>
    </header>

    <!-- 搜索栏 -->
    <div v-if="showSearch" class="search-bar">
      <input
        ref="searchInput"
        v-model="searchText"
        type="text"
        placeholder="搜索书籍..."
        class="search-input"
        @input="onSearchInput"
      />
      <button class="search-clear" @click="clearSearch">&times;</button>
    </div>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 左侧: 文案 + 状态入口 -->
      <div class="left-section">
        <!-- 品牌标语 -->
        <div class="tagline">
          <h1 class="tagline-title">把读过的，<br/>变成看得见的自己。</h1>
          <p class="tagline-subtitle">一本书,不止是读过，<br/>而是成为你的一部分。</p>
        </div>

        <!-- 状态入口 -->
        <div class="status-entries">
          <div
            v-for="entry in statusEntries"
            :key="entry.status"
            class="status-entry"
            @click="filterByStatus(entry.status)"
          >
            <span class="status-icon" v-html="entry.icon"></span>
            <span class="status-name">{{ entry.status }}</span>
            <span class="status-count">{{ entry.count }}</span>
            <span class="status-arrow">&rarr;</span>
          </div>
        </div>

        <!-- 英文装饰 -->
        <p class="decorative-text">
          Reading<br/>Builds<br/>a Softer,<br/>Stronger You.
        </p>
      </div>

      <!-- 右侧: 书籍展示 -->
      <div class="right-section">
        <div class="books-scattered">
          <div
            v-for="(book, index) in displayBooks"
            :key="book.id"
            class="scattered-book"
            :style="getBookStyle(index)"
            @click="goToBook(book.id)"
          >
            <div class="book-card">
              <img
                v-if="book.cover_image"
                :src="book.cover_image"
                :alt="book.title"
                class="book-cover-img"
              />
              <div v-else class="book-cover-placeholder" :style="{ backgroundColor: getCoverColor(book.title) }">
                <span>{{ book.title.charAt(0) }}</span>
              </div>
              <div class="book-card-info">
                <p class="book-card-title">{{ book.title }}</p>
                <p class="book-card-author" v-if="book.author">{{ book.author }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 快速记录入口 -->
    <div class="quick-record" @click="showAddModal = true">
      <div class="quick-record-icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>
        </svg>
      </div>
      <div class="quick-record-info">
        <span class="quick-record-title">快速记录</span>
        <span class="quick-record-hint">拍照 / 搜索 / 手动添加</span>
      </div>
      <span class="quick-record-arrow">&rarr;</span>
    </div>

    <!-- 添加书籍弹窗 -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal">
        <div class="modal-header">
          <h2>添加书籍</h2>
          <button class="modal-close" @click="showAddModal = false">&times;</button>
        </div>

        <div class="modal-body">
          <!-- 上传区域 -->
          <div
            class="upload-area"
            @click="triggerUpload"
            @dragover.prevent
            @drop.prevent="handleDrop"
          >
            <input
              ref="fileInput"
              type="file"
              accept="image/*"
              class="sr-only"
              @change="handleFileSelect"
            />
            <div v-if="!previewImage" class="upload-placeholder">
              <div class="upload-icon">📷</div>
              <p>点击或拖拽上传书籍封面</p>
              <p class="upload-hint">支持 JPG、PNG 格式</p>
            </div>
            <div v-else class="preview-container">
              <img :src="previewImage" class="preview-image" alt="封面预览" />
              <button class="remove-btn" @click.stop="removeImage">&times;</button>
            </div>
          </div>

          <!-- 识别状态 -->
          <div v-if="recognizing" class="recognizing">
            <div class="spinner"></div>
            <p>正在识别书籍信息...</p>
          </div>

          <!-- 识别结果 -->
          <div v-if="recognizedBook" class="recognized-info">
            <h3 class="form-title">识别结果</h3>
            <div class="form-group">
              <label>书名</label>
              <input v-model="recognizedBook.title" placeholder="书名" />
            </div>
            <div class="form-group">
              <label>作者</label>
              <input v-model="recognizedBook.author" placeholder="作者" />
            </div>
            <div class="form-group">
              <label>出版社</label>
              <input v-model="recognizedBook.publisher" placeholder="出版社" />
            </div>
            <div class="form-group">
              <label>ISBN</label>
              <input v-model="recognizedBook.isbn" placeholder="ISBN" />
            </div>

            <!-- 阅读状态 -->
            <div class="status-select">
              <label>阅读状态</label>
              <div class="status-options">
                <button
                  v-for="status in ['想读', '在读', '已读']"
                  :key="status"
                  class="status-btn"
                  :class="{ 'status-btn--active': selectedStatus === status }"
                  @click="selectedStatus = status"
                >
                  {{ status }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn--ghost" @click="showAddModal = false">取消</button>
          <button
            class="btn btn--primary"
            :disabled="!recognizedBook || adding"
            @click="addBook"
          >
            {{ adding ? '添加中...' : '加入书架' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/index'
import { useCoverColor } from '../composables/useCoverColor'
import DogEarLogo from '../components/DogEarLogo.vue'

const { getCoverColor } = useCoverColor()
const router = useRouter()
const books = ref([])
const showAddModal = ref(false)
const showSearch = ref(false)
const searchText = ref('')
const searchInput = ref(null)
const fileInput = ref(null)
const previewImage = ref(null)
const recognizing = ref(false)
const recognizedBook = ref(null)
const selectedStatus = ref('想读')
const adding = ref(false)

// 状态统计
const statusEntries = computed(() => {
  const counts = { '想读': 0, '在读': 0, '已读': 0 }
  books.value.forEach(book => {
    if (counts[book.user_status] !== undefined) {
      counts[book.user_status]++
    }
  })
  return [
    { status: '在读', count: counts['在读'], icon: '👁️' },
    { status: '想读', count: counts['想读'], icon: '🔖' },
    { status: '已读', count: counts['已读'], icon: '✓' },
  ]
})

// 展示的书籍 (最多6本散落展示)
const displayBooks = computed(() => {
  let filtered = books.value
  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    filtered = books.value.filter(b =>
      b.title?.toLowerCase().includes(keyword) ||
      b.author?.toLowerCase().includes(keyword)
    )
  }
  return filtered.slice(0, 6)
})

// 书籍散落布局样式
const getBookStyle = (index) => {
  const styles = [
    { top: '5%', left: '35%', transform: 'rotate(-5deg)' },
    { top: '0%', left: '60%', transform: 'rotate(3deg)' },
    { top: '35%', left: '25%', transform: 'rotate(-2deg)' },
    { top: '30%', left: '55%', transform: 'rotate(4deg)' },
    { top: '60%', left: '30%', transform: 'rotate(-3deg)' },
    { top: '55%', left: '60%', transform: 'rotate(2deg)' },
  ]
  return styles[index % styles.length]
}

const fetchBooks = async () => {
  try {
    const response = await api.get('/bookshelf/books')
    books.value = response.data
  } catch (error) {
    console.error('获取书籍列表失败:', error)
  }
}

onMounted(() => { fetchBooks() })

const goToBook = (id) => { router.push(`/book/${id}`) }

const filterByStatus = (status) => {
  // 可以跳转到资产页面并筛选
  router.push({ path: '/my', query: { filter: status } })
}

const onSearchInput = () => {}

const clearSearch = () => { searchText.value = '' }

const triggerUpload = () => { fileInput.value?.click() }

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) processFile(file)
}

const handleDrop = (event) => {
  const file = event.dataTransfer.files[0]
  if (file?.type.startsWith('image/')) processFile(file)
}

const processFile = async (file) => {
  const reader = new FileReader()
  reader.onload = (e) => { previewImage.value = e.target.result }
  reader.readAsDataURL(file)

  recognizing.value = true
  recognizedBook.value = null

  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await api.post('/bookshelf/recognize', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    recognizedBook.value = response.data
  } catch (error) {
    console.error('识别失败:', error)
    alert('识别失败，请手动输入书籍信息')
  } finally {
    recognizing.value = false
  }
}

const removeImage = () => {
  previewImage.value = null
  recognizedBook.value = null
}

const addBook = async () => {
  if (!recognizedBook.value) return
  adding.value = true
  try {
    await api.post('/bookshelf/books', {
      title: recognizedBook.value.title,
      author: recognizedBook.value.author,
      publisher: recognizedBook.value.publisher,
      isbn: recognizedBook.value.isbn,
      cover_image: recognizedBook.value.cover_image || recognizedBook.value.image_url,
      description: recognizedBook.value.description,
      category: recognizedBook.value.category,
      user_status: selectedStatus.value
    })
    await fetchBooks()
    showAddModal.value = false
    previewImage.value = null
    recognizedBook.value = null
    selectedStatus.value = '想读'
  } catch (error) {
    console.error('添加书籍失败:', error)
    alert('添加失败，请重试')
  } finally {
    adding.value = false
  }
}
</script>

<style scoped>
.bookshelf {
  min-height: 100dvh;
  background: var(--color-bg-page);
  padding: var(--space-md);
  padding-bottom: calc(80px + env(safe-area-inset-bottom));
}

/* ---- 顶部栏 ---- */
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-sm) 0 var(--space-md);
}

.top-actions {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.icon-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  background: transparent;
  border: none;
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.icon-btn:hover {
  background: var(--color-bg-warm);
}

.icon-btn--primary {
  background: var(--color-primary);
  color: var(--color-text-white);
}

.icon-btn--primary:hover {
  background: var(--color-primary-hover);
}

/* ---- 搜索栏 ---- */
.search-bar {
  display: flex;
  align-items: center;
  background: var(--color-bg-card);
  border-radius: var(--radius-full);
  padding: var(--space-sm) var(--space-md);
  margin-bottom: var(--space-md);
  box-shadow: var(--shadow-card);
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  color: var(--color-text-primary);
  outline: none;
}

.search-input::placeholder {
  color: var(--color-text-muted);
}

.search-clear {
  background: none;
  border: none;
  font-size: 20px;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 0 var(--space-xs);
}

/* ---- 主内容区 ---- */
.main-content {
  display: flex;
  gap: var(--space-md);
  min-height: calc(100dvh - 200px);
}

.left-section {
  flex: 0 0 45%;
  display: flex;
  flex-direction: column;
  padding-right: var(--space-md);
}

.right-section {
  flex: 1;
  position: relative;
  min-height: 500px;
}

/* ---- 品牌标语 ---- */
.tagline {
  margin-bottom: var(--space-xl);
}

.tagline-title {
  font-size: 24px;
  font-weight: 700;
  line-height: 1.4;
  color: var(--color-text-primary);
  margin-bottom: var(--space-md);
}

.tagline-subtitle {
  font-size: 13px;
  line-height: 1.6;
  color: var(--color-text-secondary);
}

/* ---- 状态入口 ---- */
.status-entries {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  margin-bottom: var(--space-xl);
}

.status-entry {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md) var(--space-lg);
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-card);
}

.status-entry:hover {
  transform: translateX(4px);
  box-shadow: var(--shadow-float);
}

.status-icon {
  font-size: 20px;
}

.status-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.status-count {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-left: auto;
}

.status-arrow {
  font-size: 18px;
  color: var(--color-text-muted);
}

/* ---- 装饰文字 ---- */
.decorative-text {
  font-family: var(--font-handwriting);
  font-size: 14px;
  color: var(--color-text-muted);
  line-height: 1.8;
  opacity: 0.7;
  margin-top: auto;
}

/* ---- 书籍散落展示 ---- */
.books-scattered {
  position: relative;
  width: 100%;
  height: 100%;
}

.scattered-book {
  position: absolute;
  width: 120px;
  transition: transform var(--transition-normal);
}

.scattered-book:hover {
  transform: scale(1.05) !important;
  z-index: 10;
}

.book-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-book);
  cursor: pointer;
}

.book-cover-img {
  width: 100%;
  height: 160px;
  object-fit: cover;
}

.book-cover-placeholder {
  width: 100%;
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: white;
  font-weight: 700;
}

.book-card-info {
  padding: var(--space-sm);
}

.book-card-title {
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-card-author {
  font-size: 11px;
  color: var(--color-text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ---- 快速记录 ---- */
.quick-record {
  position: fixed;
  bottom: calc(70px + env(safe-area-inset-bottom));
  left: var(--space-md);
  right: var(--space-md);
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-lg);
  background: var(--color-bg-card);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-float);
  cursor: pointer;
  transition: all var(--transition-fast);
  max-width: 500px;
  margin: 0 auto;
}

.quick-record:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(139, 115, 85, 0.16);
}

.quick-record-icon {
  width: 44px;
  height: 44px;
  background: var(--color-bg-warm);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-primary);
}

.quick-record-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.quick-record-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.quick-record-hint {
  font-size: 12px;
  color: var(--color-text-muted);
}

.quick-record-arrow {
  font-size: 18px;
  color: var(--color-text-muted);
}

/* ---- 弹窗 ---- */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--color-bg-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--space-md);
}

.modal {
  background: var(--color-bg-card);
  border-radius: var(--radius-xl);
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-lg);
  border-bottom: 1px solid var(--color-border-light);
}

.modal-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  color: var(--color-text-muted);
  cursor: pointer;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-lg);
}

.modal-footer {
  display: flex;
  gap: var(--space-sm);
  padding: var(--space-md) var(--space-lg);
  border-top: 1px solid var(--color-border-light);
}

/* ---- 上传区域 ---- */
.upload-area {
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-2xl) var(--space-lg);
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.upload-area:hover {
  border-color: var(--color-primary);
  background: var(--color-bg-soft);
}

.upload-placeholder {
  color: var(--color-text-secondary);
}

.upload-icon {
  font-size: 48px;
  margin-bottom: var(--space-md);
}

.upload-hint {
  font-size: 12px;
  color: var(--color-text-muted);
  margin-top: var(--space-sm);
}

.preview-container {
  position: relative;
  display: inline-block;
}

.preview-image {
  max-width: 100%;
  max-height: 200px;
  border-radius: var(--radius-md);
}

.remove-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  background: var(--color-danger);
  color: white;
  border: none;
  width: 24px;
  height: 24px;
  border-radius: var(--radius-full);
  cursor: pointer;
  font-size: 14px;
}

/* ---- 识别状态 ---- */
.recognizing {
  text-align: center;
  padding: var(--space-lg);
  color: var(--color-text-secondary);
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: var(--radius-full);
  animation: spin 0.8s linear infinite;
  margin: 0 auto var(--space-sm);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ---- 表单 ---- */
.form-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-md);
}

.form-group {
  margin-bottom: var(--space-md);
}

.form-group label {
  display: block;
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-xs);
}

.form-group input {
  width: 100%;
  padding: var(--space-sm) var(--space-md);
  border: var(--input-border);
  border-radius: var(--input-radius);
  font-size: 14px;
  color: var(--color-text-primary);
  background: var(--color-bg-soft);
  transition: border-color var(--transition-fast);
}

.form-group input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.status-select {
  margin-top: var(--space-lg);
}

.status-select label {
  display: block;
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-sm);
}

.status-options {
  display: flex;
  gap: var(--space-sm);
}

.status-btn {
  flex: 1;
  padding: var(--space-sm) var(--space-md);
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-full);
  background: var(--color-bg-soft);
  color: var(--color-text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.status-btn:hover {
  border-color: var(--color-primary);
}

.status-btn--active {
  background: var(--color-primary);
  color: var(--color-text-white);
  border-color: var(--color-primary);
}

/* ---- 按钮 ---- */
.btn {
  flex: 1;
  padding: var(--space-sm) var(--space-lg);
  border-radius: var(--radius-full);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  border: none;
}

.btn--ghost {
  background: var(--color-bg-soft);
  color: var(--color-text-secondary);
}

.btn--ghost:hover {
  background: var(--color-bg-warm);
}

.btn--primary {
  background: var(--color-primary);
  color: var(--color-text-white);
}

.btn--primary:hover {
  background: var(--color-primary-hover);
}

.btn--primary:disabled {
  background: var(--color-text-muted);
  cursor: not-allowed;
}

/* ---- 响应式 ---- */
@media (max-width: 640px) {
  .main-content {
    flex-direction: column;
  }

  .left-section {
    flex: none;
    padding-right: 0;
    margin-bottom: var(--space-lg);
  }

  .right-section {
    min-height: 400px;
  }

  .tagline-title {
    font-size: 22px;
  }

  .scattered-book {
    width: 100px;
  }

  .book-cover-img,
  .book-cover-placeholder {
    height: 130px;
  }
}
</style>
