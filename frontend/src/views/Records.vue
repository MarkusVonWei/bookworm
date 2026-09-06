<template>
  <div class="records-page">
    <header class="page-header">
      <h1 class="page-title">阅读记录</h1>
    </header>

    <EmptyState
      v-if="records.length === 0"
      icon="📝"
      title="还没有阅读记录"
      description="去书架添加一本书，开始记录吧"
    />

    <div v-else class="timeline">
      <div v-for="(group, date) in groupedRecords" :key="date" class="date-group">
        <div class="date-header">{{ date }}</div>
        <article
          v-for="record in group"
          :key="record.id"
          class="record-card"
          tabindex="0"
          @click="goToBook(record.book_id)"
          @keydown.enter="goToBook(record.book_id)"
        >
          <div class="record-book" v-if="getBook(record.book_id)">
            <span class="book-link">《{{ getBook(record.book_id).title }}》</span>
          </div>
          <p v-if="record.content" class="record-content">{{ record.content }}</p>
          <blockquote v-if="record.excerpt" class="record-excerpt">"{{ record.excerpt }}"</blockquote>
          <div v-if="record.tags" class="record-tags">
            <span v-for="tag in record.tags.split(',')" :key="tag" class="tag">{{ tag.trim() }}</span>
          </div>
        </article>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { formatDate } from '../utils/date'
import EmptyState from '../components/EmptyState.vue'

const router = useRouter()
const records = ref([])
const books = ref([])

const fetchRecords = async () => {
  try {
    const response = await axios.get('/api/bookshelf/records')
    records.value = response.data
  } catch (error) {
    console.error('获取记录失败:', error)
  }
}

const fetchBooks = async () => {
  try {
    const response = await axios.get('/api/bookshelf/books')
    books.value = response.data
  } catch (error) {
    console.error('获取书籍失败:', error)
  }
}

onMounted(() => {
  fetchRecords()
  fetchBooks()
})

const groupedRecords = computed(() => {
  const groups = {}
  records.value.forEach(record => {
    const dateStr = formatDate(record.created_at)
    if (!groups[dateStr]) groups[dateStr] = []
    groups[dateStr].push(record)
  })
  return groups
})

const getBook = (bookId) => books.value.find(b => b.id === bookId)

const goToBook = (bookId) => {
  router.push(`/book/${bookId}`)
}
</script>

<style scoped>
.records-page {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--space-lg);
}

.page-header {
  margin-bottom: var(--space-xl);
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.date-group {
  margin-bottom: var(--space-sm);
}

.date-header {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-md);
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--color-border);
}

.record-card {
  background: var(--color-bg-card);
  padding: var(--space-md);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: box-shadow var(--transition-fast), transform var(--transition-fast);
}

.record-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.record-card:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.record-book {
  margin-bottom: var(--space-sm);
}

.book-link {
  font-size: 16px;
  font-weight: 500;
  color: var(--color-primary);
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
</style>
