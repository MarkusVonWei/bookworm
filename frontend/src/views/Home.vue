<template>
  <div class="home">
    <el-row :gutter="20">
      <el-col :span="24">
        <div class="welcome-section">
          <h2>欢迎使用书虫LLM Agent</h2>
          <p>基于《如何阅读一本书》方法论的智能阅读助手</p>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="feature-section">
      <el-col :span="8">
        <el-card class="feature-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Upload /></el-icon>
              <span>上传书籍</span>
            </div>
          </template>
          <p>支持PDF、TXT、EPUB、Markdown等格式</p>
          <p>自动解析书籍结构和内容</p>
          <el-button type="primary" @click="$router.push('/upload')">开始上传</el-button>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="feature-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><ChatDotRound /></el-icon>
              <span>智能问答</span>
            </div>
          </template>
          <p>基于书籍内容回答问题</p>
          <p>支持多轮对话和深度分析</p>
          <el-button type="success" @click="$router.push('/chat')">开始问答</el-button>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="feature-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Share /></el-icon>
              <span>知识图谱</span>
            </div>
          </template>
          <p>可视化概念关系网络</p>
          <p>探索知识结构和关联</p>
          <el-button type="warning" @click="$router.push('/concepts')">查看图谱</el-button>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="stats-section">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统状态</span>
            </div>
          </template>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="服务状态">
              <el-tag :type="healthStatus === 'healthy' ? 'success' : 'danger'">
                {{ healthStatus === 'healthy' ? '正常运行' : '连接失败' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="已上传书籍">{{ bookCount }} 本</el-descriptions-item>
            <el-descriptions-item label="已提取概念">{{ conceptCount }} 个</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Upload, ChatDotRound, Share } from '@element-plus/icons-vue'
import { healthCheck, getConcepts } from '../api'

const healthStatus = ref('unknown')
const bookCount = ref(0)
const conceptCount = ref(0)

onMounted(async () => {
  try {
    const healthResponse = await healthCheck()
    healthStatus.value = healthResponse.data.status
  } catch (error) {
    healthStatus.value = 'error'
  }

  try {
    const conceptsResponse = await getConcepts()
    conceptCount.value = conceptsResponse.data.concepts.length
  } catch (error) {
    conceptCount.value = 0
  }
})
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-section {
  text-align: center;
  padding: 40px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  color: white;
  margin-bottom: 30px;
}

.welcome-section h2 {
  font-size: 32px;
  margin-bottom: 10px;
}

.welcome-section p {
  font-size: 18px;
  opacity: 0.9;
}

.feature-section {
  margin-bottom: 30px;
}

.feature-card {
  height: 100%;
}

.feature-card .card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
}

.feature-card p {
  color: #666;
  margin-bottom: 15px;
}

.stats-section {
  margin-bottom: 30px;
}
</style>