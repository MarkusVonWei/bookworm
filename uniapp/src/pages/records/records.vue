<template>
  <view class="records-page">
    <!-- 标题 -->
    <view class="page-title-section">
      <text class="page-title">阅读记录</text>
      <text class="page-title-en">Reading Timeline.</text>
    </view>

    <!-- 空状态 -->
    <view v-if="!loading && timeline.length === 0" class="empty-state">
      <text class="empty-icon">📝</text>
      <text class="empty-title">还没有阅读记录</text>
      <text class="empty-hint">去书架添加一本书，开始记录吧</text>
    </view>

    <!-- 加载中 -->
    <view v-if="loading" class="loading">
      <view class="spinner"></view>
      <text>加载中...</text>
    </view>

    <!-- 按日期分组的时间线 -->
    <view v-else class="timeline">
      <view class="date-group" v-for="group in groupedTimeline" :key="group.date">
        <view class="date-header">{{ group.date }}</view>
        <view class="date-items">
          <view
            class="timeline-item"
            v-for="event in group.events"
            :key="event._key"
            @tap="goToBook(event.book_id)"
          >
            <!-- 里程碑 -->
            <view v-if="event._isMilestone" class="milestone-card" :class="'milestone--' + event._dotClass">
              <text class="milestone-icon">{{ event._icon }}</text>
              <view class="milestone-body">
                <text class="milestone-text">
                  《{{ event.book_title }}》<text class="milestone-label">{{ event._desc }}</text>
                </text>
                <text class="milestone-time">{{ event._time }}</text>
              </view>
            </view>

            <!-- 阅读记录 -->
            <view v-else class="record-card">
              <view class="record-book">
                <text class="book-link">《{{ event.book_title }}》</text>
                <text class="record-time">{{ event._time }}</text>
              </view>
              <text class="record-content" v-if="event.content">{{ event.content }}</text>
              <view class="record-excerpt-wrap" v-if="event.excerpt">
                <text class="record-excerpt">"{{ event.excerpt }}"</text>
              </view>
              <view class="record-tags" v-if="event.tags">
                <text class="tag" v-for="tag in parseTags(event.tags)" :key="tag">{{ tag }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onShow, onPullDownRefresh } from '@dcloudio/uni-app'
import * as api from '../../api/index'
import { formatDate, formatTime } from '../../utils/date'
import { useToast } from '../../composables/useToast'

const toast = useToast()
const timeline = ref([])
const loading = ref(true)

function parseTags(tags) {
  return (tags || '').split(',').map(t => t.trim()).filter(Boolean)
}

// 预计算 + 按日期分组
const groupedTimeline = computed(() => {
  const icons = { added: '📖', started: '👁️', finished: '✅' }
  const labels = { added: '加入想读', started: '开始阅读', finished: '阅读完成' }

  const enriched = timeline.value.map(event => {
    const isMilestone = event.type === 'milestone'
    const milestone = event.milestone || event.type
    return {
      ...event,
      _key: isMilestone ? `m-${milestone}-${event.book_id}-${event.timestamp}` : `r-${event.id}`,
      _icon: isMilestone ? (icons[milestone] || '📌') : '📝',
      _time: formatTime(event.timestamp),
      _isMilestone: isMilestone,
      _desc: isMilestone ? (labels[milestone] || milestone) : (event.content ? '记录了阅读心得' : '记录了摘录'),
      _dotClass: isMilestone ? milestone : 'record'
    }
  })

  const groups = {}
  enriched.forEach(event => {
    const dateStr = formatDate(event.timestamp) || '未知日期'
    if (!groups[dateStr]) groups[dateStr] = []
    groups[dateStr].push(event)
  })

  return Object.keys(groups).map(date => ({ date, events: groups[date] }))
})

async function loadTimeline() {
  loading.value = true
  try {
    const data = await api.getTimeline()
    timeline.value = Array.isArray(data) ? data : []
  } catch (err) {
    console.error('加载时间线失败:', err)
    toast.error('加载失败')
  } finally {
    loading.value = false
  }
}

function goToBook(bookId) {
  uni.navigateTo({ url: `/pages/book-detail/book-detail?id=${bookId}` })
}

onMounted(() => loadTimeline())
onShow(() => loadTimeline())
onPullDownRefresh(async () => {
  await loadTimeline()
  uni.stopPullDownRefresh()
})
</script>

<style scoped>
.records-page {
  min-height: 100vh;
  background: var(--color-bg-page);
  padding: 12px 16px 32px;
}

.page-title-section {
  margin-bottom: 24px;
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

/* 时间线 */
.timeline {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.date-header {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
  padding-bottom: 4px;
  border-bottom: 1px solid var(--color-border-light);
}

.date-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 里程碑 */
.milestone-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: var(--radius-md);
  background: var(--color-bg-card);
  box-shadow: var(--shadow-card);
}

.milestone--added { border-left: 3px solid var(--color-text-muted); }
.milestone--started { border-left: 3px solid var(--color-primary); }
.milestone--finished { border-left: 3px solid var(--color-finished); }

.milestone-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.milestone-body {
  flex: 1;
  min-width: 0;
}

.milestone-text {
  display: block;
  font-size: 13px;
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.milestone-label {
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-left: 4px;
}

.milestone-time {
  display: block;
  font-size: 11px;
  color: var(--color-text-muted);
}

/* 记录卡片 */
.record-card {
  background: var(--color-bg-card);
  padding: 12px;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
}

.record-book {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.book-link {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-primary);
}

.record-time {
  font-size: 11px;
  color: var(--color-text-muted);
}

.record-content {
  font-size: 13px;
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
</style>
