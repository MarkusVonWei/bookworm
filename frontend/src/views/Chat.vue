<template>
  <div class="chat-page">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="chat-card">
          <template #header>
            <div class="card-header">
              <span>智能问答</span>
              <el-select v-model="selectedBook" placeholder="选择书籍（可选）" clearable size="small">
                <el-option
                  v-for="book in books"
                  :key="book"
                  :label="book"
                  :value="book"
                />
              </el-select>
            </div>
          </template>

          <div class="chat-messages" ref="messagesContainer">
            <div
              v-for="(msg, index) in messages"
              :key="index"
              :class="['message', msg.role]"
            >
              <div class="message-content">
                <div class="message-avatar">
                  <el-icon v-if="msg.role === 'user'"><User /></el-icon>
                  <el-icon v-else><Service /></el-icon>
                </div>
                <div class="message-bubble">
                  <div class="message-text" v-html="formatMessage(msg.content)"></div>
                  <div class="message-time">{{ msg.time }}</div>
                </div>
              </div>
            </div>
            <div v-if="loading" class="message assistant">
              <div class="message-content">
                <div class="message-avatar">
                  <el-icon><Service /></el-icon>
                </div>
                <div class="message-bubble">
                  <div class="message-text typing">
                    <span class="dot"></span>
                    <span class="dot"></span>
                    <span class="dot"></span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="chat-input">
            <el-input
              v-model="inputMessage"
              placeholder="输入你的问题..."
              :rows="2"
              type="textarea"
              resize="none"
              @keydown.enter.ctrl="sendMessage"
            />
            <el-button type="primary" @click="sendMessage" :loading="loading" :disabled="!inputMessage.trim()">
              发送
            </el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>对话信息</span>
            </div>
          </template>

          <div class="chat-info">
            <h4>对话统计</h4>
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="消息数量">{{ messages.length }}</el-descriptions-item>
              <el-descriptions-item label="当前书籍">{{ selectedBook || '全部书籍' }}</el-descriptions-item>
            </el-descriptions>

            <h4>快捷问题</h4>
            <div class="quick-questions">
              <el-button
                v-for="q in quickQuestions"
                :key="q"
                size="small"
                @click="inputMessage = q"
              >
                {{ q }}
              </el-button>
            </div>

            <h4>使用提示</h4>
            <ul class="tips">
              <li>按 Ctrl + Enter 发送消息</li>
              <li>可以指定书籍进行问答</li>
              <li>支持多轮对话</li>
            </ul>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { User, Service } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { askQuestion, getConcepts } from '../api'

const inputMessage = ref('')
const messages = ref([])
const loading = ref(false)
const selectedBook = ref('')
const books = ref([])
const messagesContainer = ref(null)

const quickQuestions = [
  '这本书的主要观点是什么？',
  '核心概念有哪些？',
  '作者的论证逻辑是什么？',
  '这本书的结构是怎样的？'
]

function formatMessage(content) {
  // 简单的Markdown格式化
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
}

function getCurrentTime() {
  return new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

async function sendMessage() {
  const message = inputMessage.value.trim()
  if (!message || loading.value) return

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: message,
    time: getCurrentTime()
  })

  inputMessage.value = ''
  loading.value = true
  scrollToBottom()

  try {
    const response = await askQuestion(message, selectedBook.value || null)
    
    // 添加助手回复
    messages.value.push({
      role: 'assistant',
      content: response.data.answer,
      time: getCurrentTime()
    })
  } catch (error) {
    ElMessage.error('获取答案失败: ' + (error.response?.data?.detail || error.message))
    messages.value.push({
      role: 'assistant',
      content: '抱歉，获取答案时出现错误，请稍后重试。',
      time: getCurrentTime()
    })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

onMounted(async () => {
  try {
    const response = await getConcepts()
    // 从概念中提取书籍信息（这里简化处理）
    books.value = ['示例书籍']
  } catch (error) {
    console.error('获取书籍列表失败:', error)
  }
})
</script>

<style scoped>
.chat-page {
  max-width: 1200px;
  margin: 0 auto;
}

.chat-card {
  height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 20px;
}

.message {
  margin-bottom: 20px;
}

.message-content {
  display: flex;
  gap: 10px;
}

.message.user .message-content {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #409eff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background-color: #67c23a;
}

.message-bubble {
  max-width: 70%;
}

.message-text {
  padding: 12px 16px;
  border-radius: 8px;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  line-height: 1.6;
}

.message.user .message-text {
  background-color: #95ec69;
}

.message-time {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
  text-align: right;
}

.message.user .message-time {
  text-align: left;
}

.typing {
  display: flex;
  gap: 5px;
  padding: 15px 20px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #999;
  animation: typing 1.4s infinite ease-in-out;
}

.dot:nth-child(1) {
  animation-delay: -0.32s;
}

.dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.chat-input {
  display: flex;
  gap: 10px;
}

.chat-input .el-input {
  flex: 1;
}

.chat-info h4 {
  margin: 15px 0 10px;
  color: #409eff;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 15px;
}

.tips {
  padding-left: 20px;
  color: #666;
}

.tips li {
  margin-bottom: 5px;
}
</style>