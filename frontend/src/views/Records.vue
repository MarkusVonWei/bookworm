<template>
  <div class="records-page">
    <!-- 顶部导航 -->
    <header class="top-bar">
      <DogEarLogo :show-text="true" />
    </header>

    <!-- 标题 -->
    <div class="page-title-section">
      <h1 class="page-title">阅读记录</h1>
      <p class="page-title-en">Reading Timeline.</p>
    </div>

    <!-- 空状态 -->
    <div v-if="timeline.length === 0" class="empty-state">
      <div class="empty-icon">📝</div>
      <p class="empty-title">还没有阅读记录</p>
      <p class="empty-hint">去书架添加一本书，开始记录吧</p>
    </div>

    <!-- 时间线 -->
    <div v-else class="timeline">
      <div v-for="(group, date) in groupedTimeline" :key="date" class="date-group">
        <div class="date-header">{{ date }}</div>
        <div class="date-items">
          <template v-for="event in group" :key="eventKey(event)">
            <!-- 状态里程碑 -->
            <div
              v-if="event.type === 'milestone'"
              class="milestone-card"
              :class="`milestone-card--${event.milestone}`"
              @click="goToBook(event.book_id)"
            >
              <span class="milestone-icon">{{ milestoneIcon(event.milestone) }}</span>
              <div class="milestone-body">
                <span class="milestone-text">
                  《{{ event.book_title }}》
                  <strong>{{ milestoneLabel(event.milestone) }}</strong>
                </span>
                <span class="milestone-time">{{ formatTime(event.timestamp) }}</span>
              </div>
            </div>

            <!-- 阅读记录 -->
            <article
              v-else
              class="record-card"
              tabindex="0"
              @click="goToBook(event.book_id)"
              @keydown.enter="goToBook(event.book_id)"
            >
              <div class="record-book">
                <span class="book-link">《{{ event.book_title }}》</span>
              </div>
              <p v-if="event.content" class="record-content">{{ event.content }}</p>
              <blockquote v-if="event.excerpt" class="record-excerpt">"{{ event.excerpt }}"</blockquote>
              <div v-if="event.tags" class="record-tags">
                <span v-for="tag in event.tags.split(',')" :key="tag" class="tag">{{ tag.trim() }}</span>
              </div>
            </article>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/index'
import { formatDate, formatTime } from '../utils/date'
import DogEarLogo from '../components/DogEarLogo.vue'

const router = useRouter()
const timeline = ref([])

const fetchTimeline = async () => {
  try {
    const response = await api.get('/bookshelf/timeline')
    timeline.value = response.data
  } catch (error) {
    console.error('获取时间线失败:', error)
  }
}

onMounted(() => { fetchTimeline() })

const groupedTimeline = computed(() => {
  const groups = {}
  timeline.value.forEach(event => {
    const dateStr = formatDate(event.timestamp)
    if (!groups[dateStr]) groups[dateStr] = []
    groups[dateStr].push(event)
  })
  return groups
})

const eventKey = (event) => {
  if (event.type === 'milestone') return `m-${event.milestone}-${event.book_id}-${event.timestamp}`
  return `r-${event.id}`
}

const milestoneIcon = (milestone) => {
  const icons = { added: '📖', started: '👁️', finished: '✅' }
  return icons[milestone] || '📌'
}

const milestoneLabel = (milestone) => {
  const labels = { added: '加入想读', started: '开始阅读', finished: '阅读完成' }
  return labels[milestone] || milestone
}

const goToBook = (bookId) => { router.push(`/book/${bookId}`) }
</script>

<style scoped>
.records-page {
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

/* ---- 页面标题 ---- */
.page-title-section {
  margin-bottom: var(--space-xl);
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

/* ---- 空状态 ---- */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-2xl) var(--space-md);
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: var(--space-md);
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-sm);
}

.empty-hint {
  font-size: 14px;
  color: var(--color-text-muted);
}

/* ---- 时间线布局 ---- */
.timeline {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.date-group {
  margin-bottom: var(--space-sm);
}

.date-header {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-md);
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--color-border-light);
}

.date-items {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

/* ---- 里程碑卡片 ---- */
.milestone-card {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md);
  border-radius: var(--radius-md);
  background: var(--color-bg-card);
  box-shadow: var(--shadow-card);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.milestone-card:hover {
  box-shadow: var(--shadow-float);
  transform: translateX(4px);
}

.milestone-card--added {
  border-left: 3px solid var(--color-text-muted);
}

.milestone-card--started {
  border-left: 3px solid var(--color-primary);
}

.milestone-card--finished {
  border-left: 3px solid var(--color-finished);
}

.milestone-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.milestone-body {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.milestone-text {
  font-size: 14px;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.milestone-text strong {
  font-weight: 600;
  color: var(--color-text-secondary);
}

.milestone-time {
  font-size: 12px;
  color: var(--color-text-muted);
}

/* ---- 阅读记录卡片 ---- */
.record-card {
  background: var(--color-bg-card);
  padding: var(--space-md);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.record-card:hover {
  box-shadow: var(--shadow-float);
  transform: translateY(-2px);
}

.record-book {
  margin-bottom: var(--space-sm);
}

.book-link {
  font-size: 15px;
  font-weight: 600;
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
  color: var(--color-text-secondary);
  font-style: italic;
  padding-left: var(--space-md);
  border-left: 3px solid var(--color-primary);
  margin: 0 0 var(--space-sm) 0;
}

.record-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
  margin-top: var(--space-sm);
}

.tag {
  display: inline-block;
  background: var(--color-bg-warm);
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-sm);
  font-size: 12px;
  color: var(--color-text-secondary);
}
</style>
