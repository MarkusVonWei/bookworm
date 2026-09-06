<template>
  <div class="upload-page">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>上传书籍</span>
            </div>
          </template>

          <el-upload
            ref="uploadRef"
            class="upload-area"
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :before-upload="beforeUpload"
            accept=".pdf,.txt,.epub,.md,.markdown"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 PDF、TXT、EPUB、Markdown 格式，文件大小不超过 50MB
              </div>
            </template>
          </el-upload>

          <div class="upload-actions">
            <el-button type="primary" @click="submitUpload" :loading="uploading" :disabled="!selectedFile">
              {{ uploading ? '解析中...' : '开始解析' }}
            </el-button>
            <el-button @click="clearFile" :disabled="!selectedFile">清除</el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>上传说明</span>
            </div>
          </template>

          <div class="instructions">
            <h4>支持格式</h4>
            <ul>
              <li>PDF - 便携式文档格式</li>
              <li>TXT - 纯文本文件</li>
              <li>EPUB - 电子书格式</li>
              <li>Markdown - 标记语言文件</li>
            </ul>

            <h4>处理流程</h4>
            <el-steps direction="vertical" :active="currentStep" finish-status="success">
              <el-step title="上传文件" description="选择要解析的书籍文件" />
              <el-step title="解析结构" description="提取章节和文本内容" />
              <el-step title="知识提取" description="提取概念、观点和关系" />
              <el-step title="构建图谱" description="生成知识图谱" />
            </el-steps>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="showResult" title="解析完成" width="500">
      <el-result
        icon="success"
        title="书籍解析成功"
        :sub-title="`已成功解析《${parseResult.bookTitle}》`"
      >
        <template #extra>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="提取概念">{{ parseResult.conceptsCount }} 个</el-descriptions-item>
            <el-descriptions-item label="提取观点">{{ parseResult.argumentsCount }} 个</el-descriptions-item>
            <el-descriptions-item label="建立关系">{{ parseResult.relationsCount }} 个</el-descriptions-item>
          </el-descriptions>
        </template>
      </el-result>
      <template #footer>
        <el-button type="primary" @click="$router.push('/chat')">开始问答</el-button>
        <el-button @click="showResult = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { uploadBook } from '../api'

const uploadRef = ref(null)
const selectedFile = ref(null)
const uploading = ref(false)
const currentStep = ref(0)
const showResult = ref(false)
const parseResult = ref({
  bookTitle: '',
  conceptsCount: 0,
  argumentsCount: 0,
  relationsCount: 0
})

function handleFileChange(file) {
  selectedFile.value = file.raw
}

function beforeUpload(file) {
  const maxSize = 50 * 1024 * 1024 // 50MB
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 50MB')
    return false
  }
  return true
}

function clearFile() {
  selectedFile.value = null
  uploadRef.value.clearFiles()
  currentStep.value = 0
}

async function submitUpload() {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  uploading.value = true
  currentStep.value = 1

  try {
    // 模拟步骤进度
    setTimeout(() => { currentStep.value = 2 }, 1000)
    setTimeout(() => { currentStep.value = 3 }, 2000)

    const response = await uploadBook(selectedFile.value)
    
    parseResult.value = {
      bookTitle: response.data.book_title,
      conceptsCount: response.data.concepts_count,
      argumentsCount: response.data.arguments_count,
      relationsCount: response.data.relations_count
    }

    currentStep.value = 4
    showResult.value = true
    ElMessage.success('书籍解析成功')
  } catch (error) {
    ElMessage.error('上传失败: ' + (error.response?.data?.detail || error.message))
    currentStep.value = 0
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.upload-page {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
}

.upload-area {
  width: 100%;
}

.upload-actions {
  margin-top: 20px;
  text-align: center;
}

.instructions h4 {
  margin: 15px 0 10px;
  color: #409eff;
}

.instructions ul {
  padding-left: 20px;
  margin-bottom: 20px;
}

.instructions li {
  margin-bottom: 5px;
  color: #666;
}
</style>