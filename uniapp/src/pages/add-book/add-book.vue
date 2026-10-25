<template>
  <view class="add-book-page">
    <!-- 添加方式选择 -->
    <view class="method-tabs">
      <view
        class="method-tab"
        :class="{ 'method-tab--active': addMethod === method.value }"
        v-for="method in methods"
        :key="method.value"
        @tap="selectMethod(method.value)"
      >
        <text class="method-icon">{{ method.icon }}</text>
        <text class="method-label">{{ method.label }}</text>
      </view>
    </view>

    <!-- 拍照/相册上传 -->
    <view class="upload-section" v-if="addMethod === 'camera' || addMethod === 'album'">
      <view class="upload-area" @tap="chooseImage()">
        <template v-if="!tempFilePath">
          <text class="upload-icon">📷</text>
          <text class="upload-text">{{ addMethod === 'camera' ? '拍照识别' : '从相册选择' }}</text>
          <text class="upload-hint">支持 JPG、PNG 格式</text>
        </template>
        <template v-else>
          <image :src="tempFilePath" class="preview-image" mode="aspectFit" />
          <view class="remove-btn" @tap.stop="removeImage">×</view>
        </template>
      </view>

      <!-- 识别中 -->
      <view v-if="recognizing" class="recognizing">
        <view class="spinner"></view>
        <text>{{ recognizingText }}</text>
      </view>

      <!-- 条形码识别成功提示 -->
      <view v-if="barcodeResult && !recognizing" class="barcode-hint">
        <text class="barcode-icon">📊</text>
        <text class="barcode-text">条形码识别成功: {{ barcodeResult }}</text>
      </view>
    </view>

    <!-- 搜索添加 -->
    <view class="search-section" v-if="addMethod === 'search'">
      <view class="search-bar">
        <input
          class="search-input"
          v-model="searchText"
          placeholder="输入书名搜索"
          confirm-type="search"
          @confirm="onSearch"
        />
        <view class="search-btn" @tap="onSearch">搜索</view>
      </view>

      <!-- 搜索结果 -->
      <view class="search-results" v-if="searchResults.length > 0">
        <view
          class="result-item"
          v-for="item in searchResults"
          :key="item.id || item.title"
          @tap="selectSearchResult(item)"
        >
          <view class="result-cover">
            <image v-if="item.cover_image" :src="resolveImageUrl(item.cover_image)" class="result-cover-img" mode="aspectFill" />
            <view v-else class="result-cover-placeholder" :style="{ backgroundColor: getCoverColor(item.title) }">
              <text>{{ item.title[0] }}</text>
            </view>
          </view>
          <view class="result-info">
            <text class="result-title">{{ item.title }}</text>
            <text class="result-author">{{ item.author || '未知作者' }}</text>
          </view>
          <view class="result-select">选择</view>
        </view>
      </view>

      <!-- 搜索空状态 -->
      <view v-if="searched && searchResults.length === 0" class="empty-state">
        <text class="empty-icon">🔍</text>
        <text class="empty-title">未找到相关书籍</text>
        <text class="empty-hint">换个关键词试试</text>
      </view>
    </view>

    <!-- 表单 -->
    <view class="form-section">
      <text class="form-title">书籍信息</text>

      <view class="form-group">
        <text class="form-label">书名 *</text>
        <input class="form-input" v-model="title" placeholder="请输入书名" />
      </view>

      <view class="form-group">
        <text class="form-label">作者</text>
        <input class="form-input" v-model="author" placeholder="请输入作者" />
      </view>

      <view class="form-group">
        <text class="form-label">出版社</text>
        <input class="form-input" v-model="publisher" placeholder="请输入出版社" />
      </view>

      <view class="form-group">
        <text class="form-label">ISBN</text>
        <input class="form-input" v-model="isbn" placeholder="请输入ISBN" />
      </view>

      <view class="form-group">
        <text class="form-label">出版日期</text>
        <input class="form-input" v-model="publishDate" placeholder="如：2024" />
      </view>

      <!-- 阅读状态 -->
      <view class="form-group">
        <text class="form-label">阅读状态</text>
        <view class="status-options">
          <view
            class="status-option"
            :class="{ 'status-option--active': userStatus === status }"
            v-for="status in ['想读', '在读', '已读']"
            :key="status"
            @tap="userStatus = status"
          >
            {{ status }}
          </view>
        </view>
      </view>
    </view>

    <!-- 提交按钮 -->
    <button class="btn btn--primary submit-btn" :disabled="adding || !title" @tap="addBook">
      {{ adding ? '添加中...' : '加入书架' }}
    </button>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import * as api from '../../api/index'
import { getCoverColor, resolveImageUrl } from '../../utils/coverColor'
import { useToast } from '../../composables/useToast'

const toast = useToast()
const addMethod = ref('camera')
const methods = [
  { value: 'camera', icon: '📷', label: '拍照' },
  { value: 'album', icon: '🖼️', label: '相册' },
  { value: 'search', icon: '🔍', label: '搜索' }
]

const recognizing = ref(false)
const recognizingText = ref('正在识别书籍信息...')
const barcodeResult = ref('')
const tempFilePath = ref('')
const searchText = ref('')
const searchResults = ref([])
const searched = ref(false)

const title = ref('')
const author = ref('')
const publisher = ref('')
const isbn = ref('')
const description = ref('')
const category = ref('')
const userStatus = ref('想读')
const coverImage = ref('')
const publishDate = ref('')
const adding = ref(false)

function selectMethod(method) {
  addMethod.value = method
}

function chooseImage(sourceType) {
  const type = sourceType || (addMethod.value === 'camera' ? 'camera' : 'album')
  uni.chooseImage({
    count: 1,
    sourceType: [type],
    success: (res) => {
      tempFilePath.value = res.tempFilePaths[0]
      recognizeBook(tempFilePath.value)
    }
  })
}

async function recognizeBook(filePath) {
  recognizing.value = true
  recognizingText.value = '正在识别条形码...'
  barcodeResult.value = ''
  
  try {
    const result = await api.recognizeBook(filePath)
    
    // 显示识别来源
    if (result.source === 'barcode') {
      recognizingText.value = '条形码识别成功，正在查询图书信息...'
      barcodeResult.value = result.isbn || result.barcode_data || ''
    } else {
      recognizingText.value = 'AI 识别成功，正在完善信息...'
    }
    
    // 填充表单
    title.value = result.title || ''
    author.value = result.author || ''
    publisher.value = result.publisher || ''
    isbn.value = result.isbn || ''
    publishDate.value = result.publish_date || ''
    description.value = result.description || ''
    category.value = result.category || ''
    coverImage.value = resolveImageUrl(result.cover_image || result.image_url || '')
    
    // 显示成功提示
    if (result.source === 'barcode') {
      toast.success(`条形码识别成功: ${result.isbn}`)
    } else {
      toast.success('识别成功')
    }
  } catch (err) {
    console.error('识别失败:', err)
    toast.error(err.message || '识别失败，请手动输入')
  } finally {
    recognizing.value = false
    recognizingText.value = '正在识别书籍信息...'
  }
}

async function onSearch() {
  const kw = searchText.value.trim()
  if (!kw) return
  try {
    const results = await api.searchBooksExternal(kw)
    searchResults.value = Array.isArray(results) ? results : []
    searched.value = true
  } catch (err) {
    console.error('搜索失败:', err)
    toast.error('搜索失败')
  }
}

function selectSearchResult(item) {
  title.value = item.title || ''
  author.value = item.author || ''
  publisher.value = item.publisher || ''
  isbn.value = item.isbn || ''
  description.value = item.description || ''
  category.value = item.category || ''
  publishDate.value = item.publish_date || ''
  coverImage.value = resolveImageUrl(item.cover_image || '')
  searchResults.value = []
  searchText.value = ''
  searched.value = false
}

function removeImage() {
  tempFilePath.value = ''
}

async function addBook() {
  if (!title.value) {
    toast.warning('请输入书名')
    return
  }

  adding.value = true
  try {
    await api.createBook({
      title: title.value,
      author: author.value,
      publisher: publisher.value,
      isbn: isbn.value,
      publish_date: publishDate.value,
      description: description.value,
      category: category.value,
      cover_image: coverImage.value,
      user_status: userStatus.value
    })
    toast.success('添加成功')
    setTimeout(() => uni.navigateBack(), 1500)
  } catch (err) {
    console.error('添加书籍失败:', err)
    toast.error('添加失败，请重试')
  } finally {
    adding.value = false
  }
}
</script>

<style scoped>
.add-book-page {
  min-height: 100vh;
  background: var(--color-bg-page);
  padding: 12px 16px 32px;
}

/* 添加方式 */
.method-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.method-tab {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px;
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  border: 2px solid transparent;
}

.method-tab--active {
  border-color: var(--color-primary);
  background: var(--color-bg-warm);
}

.method-icon {
  font-size: 20px;
}

.method-label {
  font-size: 12px;
  color: var(--color-text-secondary);
}

/* 上传 */
.upload-area {
  position: relative;
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
  padding: 32px 16px;
  text-align: center;
  margin-bottom: 16px;
  background: var(--color-bg-card);
}

.upload-icon {
  display: block;
  font-size: 36px;
  margin-bottom: 8px;
}

.upload-text {
  display: block;
  font-size: 14px;
  color: var(--color-text-primary);
  margin-bottom: 4px;
}

.upload-hint {
  display: block;
  font-size: 12px;
  color: var(--color-text-muted);
}

.preview-image {
  width: 100%;
  max-height: 200px;
  border-radius: var(--radius-md);
}

.remove-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 24px;
  height: 24px;
  background: var(--color-danger);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.recognizing {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  color: var(--color-text-secondary);
}

/* 条形码识别提示 */
.barcode-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: #E8F5E9;
  border-radius: 8px;
  margin-bottom: 12px;
}

.barcode-icon {
  font-size: 18px;
}

.barcode-text {
  font-size: 13px;
  color: #2E7D32;
  font-weight: 500;
}

/* 搜索 */
.search-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.search-input {
  flex: 1;
  height: 44px;
  padding: 0 12px;
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  font-size: 14px;
  border: 1px solid var(--color-border);
  box-sizing: border-box;
}

.search-btn {
  padding: 10px 16px;
  background: var(--color-primary);
  color: var(--color-text-white);
  border-radius: var(--radius-md);
  font-size: 14px;
}

.search-results {
  margin-bottom: 16px;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  margin-bottom: 8px;
  box-shadow: var(--shadow-card);
}

.result-cover {
  width: 40px;
  height: 56px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  flex-shrink: 0;
}

.result-cover-img {
  width: 100%;
  height: 100%;
}

.result-cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 700;
}

.result-info {
  flex: 1;
  min-width: 0;
}

.result-title {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-author {
  display: block;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.result-select {
  padding: 4px 10px;
  background: var(--color-bg-warm);
  border-radius: var(--radius-full);
  font-size: 12px;
  color: var(--color-primary);
}

/* 表单 */
.form-section {
  margin-bottom: 20px;
}

.form-title {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 12px;
}

.form-group {
  margin-bottom: 14px;
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
  background: var(--color-bg-card);
  box-sizing: border-box;
}

.status-options {
  display: flex;
  gap: 8px;
}

.status-option {
  flex: 1;
  padding: 8px;
  text-align: center;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-full);
  background: var(--color-bg-soft);
  color: var(--color-text-secondary);
  font-size: 13px;
}

.status-option--active {
  background: var(--color-primary);
  color: var(--color-text-white);
  border-color: var(--color-primary);
}

.submit-btn {
  width: 100%;
}
</style>
