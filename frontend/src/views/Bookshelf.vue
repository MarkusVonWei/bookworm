<template>
  <div class="bookshelf">
    <header class="page-header">
      <h1 class="page-title">我的书架</h1>
      <button class="btn btn--primary" @click="showAddModal = true">+ 添加书籍</button>
    </header>

    <section class="shelf-container">
      <EmptyState
        v-if="books.length === 0"
        icon="📚"
        title="书架还是空的"
        description="点击右上角添加你的第一本书"
      />

      <template v-else>
        <div
          v-for="group in statusGroups"
          :key="group.status"
          class="shelf-group"
        >
          <h2 class="shelf-group__title">{{ group.status }}</h2>
          <div class="shelf-group__track">
            <article
              v-for="book in group.books"
              :key="book.id"
              class="book-item"
              :class="{ 'book-item--dimmed': group.status === '想读' }"
              @click="goToBook(book.id)"
            >
              <div class="book-cover">
                <img v-if="book.cover_image" :src="book.cover_image" :alt="book.title" />
                <div v-else class="cover-placeholder" :style="{ backgroundColor: getCoverColor(book.title) }">
                  <span>{{ book.title.charAt(0) }}</span>
                </div>
              </div>
              <div class="book-info">
                <h3 class="book-title">{{ book.title }}</h3>
                <p class="book-author">{{ book.author || '未知作者' }}</p>
              </div>
            </article>
          </div>
        </div>
      </template>
    </section>

    <Modal v-if="showAddModal" title="添加书籍" @close="showAddModal = false">
      <div
        class="upload-area"
        tabindex="0"
        role="button"
        aria-label="上传书籍封面"
        @click="triggerUpload"
        @keydown.enter="triggerUpload"
        @keydown.space.prevent="triggerUpload"
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
          <div class="upload-icon" aria-hidden="true">📷</div>
          <p>点击或拖拽上传书籍封面</p>
          <p class="upload-hint">支持 JPG、PNG 格式</p>
        </div>
        <div v-else class="preview-container">
          <img :src="previewImage" class="preview-image" alt="封面预览" />
          <button class="remove-btn" aria-label="移除图片" @click.stop="removeImage">&times;</button>
        </div>
      </div>

      <div v-if="recognizing" class="recognizing" role="status">
        <div class="spinner"></div>
        <p>正在识别书籍信息...</p>
      </div>

      <div v-if="recognizedBook" class="recognized-info">
        <h3 class="section-title">识别结果</h3>
        <div class="info-form">
          <div class="form-group">
            <label for="book-title">书名</label>
            <input id="book-title" v-model="recognizedBook.title" placeholder="书名" />
          </div>
          <div class="form-group">
            <label for="book-author">作者</label>
            <input id="book-author" v-model="recognizedBook.author" placeholder="作者" />
          </div>
          <div class="form-group">
            <label for="book-publisher">出版社</label>
            <input id="book-publisher" v-model="recognizedBook.publisher" placeholder="出版社" />
          </div>
          <div class="form-group">
            <label for="book-isbn">ISBN</label>
            <input id="book-isbn" v-model="recognizedBook.isbn" placeholder="ISBN" />
          </div>
        </div>

        <div class="status-select">
          <label class="form-label">阅读状态</label>
          <div class="status-options">
            <label
              v-for="status in ['想读', '在读', '已读']"
              :key="status"
              class="status-option"
              :class="{ 'status-option--active': selectedStatus === status }"
            >
              <input type="radio" v-model="selectedStatus" :value="status" class="sr-only" />
              {{ status }}
            </label>
          </div>
        </div>
      </div>

      <template #footer>
        <button class="btn btn--secondary" @click="showAddModal = false">取消</button>
        <button
          class="btn btn--primary"
          :disabled="!recognizedBook || adding"
          @click="addBook"
        >
          {{ adding ? '添加中...' : '加入书架' }}
        </button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useCoverColor } from '../composables/useCoverColor'
import Modal from '../components/Modal.vue'
import EmptyState from '../components/EmptyState.vue'

const { getCoverColor } = useCoverColor()
const router = useRouter()
const books = ref([])
const showAddModal = ref(false)

const STATUS_ORDER = ['想读', '在读', '已读']

const statusGroups = computed(() => {
  const map = {}
  for (const status of STATUS_ORDER) {
    map[status] = []
  }
  for (const book of books.value) {
    if (map[book.user_status]) {
      map[book.user_status].push(book)
    }
  }
  return STATUS_ORDER
    .filter(status => map[status].length > 0)
    .map(status => ({ status, books: map[status] }))
})
const fileInput = ref(null)
const previewImage = ref(null)
const recognizing = ref(false)
const recognizedBook = ref(null)
const selectedStatus = ref('想读')
const adding = ref(false)

const fetchBooks = async () => {
  try {
    const response = await axios.get('/api/bookshelf/books')
    books.value = response.data
  } catch (error) {
    console.error('获取书籍列表失败:', error)
  }
}

onMounted(() => {
  fetchBooks()
})

const goToBook = (id) => {
  router.push(`/book/${id}`)
}

const triggerUpload = () => {
  fileInput.value.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) processFile(file)
}

const handleDrop = (event) => {
  const file = event.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) processFile(file)
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
    const response = await axios.post('/api/bookshelf/recognize', formData, {
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
    await axios.post('/api/bookshelf/books', {
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
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--space-lg);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-xl);
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.shelf-container {
  min-height: 400px;
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

.shelf-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.shelf-group__title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  padding-left: 2px;
}

.shelf-group__track {
  display: flex;
  gap: var(--space-md);
  overflow-x: auto;
  scroll-snap-type: x proximity;
  padding-bottom: var(--space-sm);
}

.shelf-group__track::-webkit-scrollbar {
  height: 4px;
}

.shelf-group__track::-webkit-scrollbar-track {
  background: transparent;
}

.shelf-group__track::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 2px;
}

.book-item {
  flex-shrink: 0;
  width: 140px;
  scroll-snap-align: start;
  cursor: pointer;
  transition: transform var(--transition-normal);
}

.book-item:hover {
  transform: translateY(-4px);
}

.book-item--dimmed .book-cover {
  filter: grayscale(70%);
  opacity: 0.7;
}

.book-cover {
  position: relative;
  width: 100%;
  padding-bottom: 140%;
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

.book-cover img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  color: white;
  font-weight: 700;
}

.status-badge {
  position: absolute;
  bottom: var(--space-sm);
  left: var(--space-sm);
  background: rgba(0, 0, 0, 0.6);
  color: white;
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-sm);
  font-size: 12px;
}

.book-info {
  padding: var(--space-sm) 0;
}

.book-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: var(--space-xs);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-author {
  font-size: 12px;
  color: var(--color-text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ---- 上传区域 ---- */
.upload-area {
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-2xl) var(--space-lg);
  text-align: center;
  cursor: pointer;
  transition: border-color var(--transition-fast);
}

.upload-area:hover,
.upload-area:focus-visible {
  border-color: var(--color-primary);
}

.upload-icon {
  font-size: 48px;
  margin-bottom: var(--space-md);
}

.upload-hint {
  font-size: 12px;
  color: var(--color-text-placeholder);
  margin-top: var(--space-sm);
}

.preview-container {
  position: relative;
  display: inline-block;
}

.preview-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: var(--radius-md);
}

.remove-btn {
  position: absolute;
  top: calc(-1 * var(--space-sm));
  right: calc(-1 * var(--space-sm));
  background: var(--color-danger);
  color: white;
  border: none;
  width: 24px;
  height: 24px;
  border-radius: var(--radius-full);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  transition: background var(--transition-fast);
}

.remove-btn:hover {
  background: #e04848;
}

.recognizing {
  text-align: center;
  padding: var(--space-lg);
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

.recognized-info {
  margin-top: var(--space-lg);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-md);
}

.info-form {
  display: grid;
  gap: var(--space-md);
}

.status-select {
  margin-top: var(--space-lg);
}

.form-label {
  display: block;
  font-size: var(--label-font-size);
  color: var(--label-color);
  margin-bottom: var(--space-sm);
}

.status-options {
  display: flex;
  gap: var(--space-sm);
}

.status-option {
  flex: 1;
  text-align: center;
  padding: var(--space-sm) var(--space-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-size: 14px;
}

.status-option--active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
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
