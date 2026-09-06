<template>
  <div class="concepts-page">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>知识图谱</span>
              <el-input
                v-model="searchKeyword"
                placeholder="搜索概念..."
                style="width: 300px"
                clearable
                @input="handleSearch"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>
          </template>

          <div class="graph-container" v-loading="loading">
            <div v-if="!selectedConcept" class="concept-list">
              <el-empty v-if="filteredConcepts.length === 0" description="暂无概念数据" />
              <el-row :gutter="10" v-else>
                <el-col :span="6" v-for="concept in filteredConcepts" :key="concept.name">
                  <el-card
                    class="concept-card"
                    shadow="hover"
                    @click="selectConcept(concept)"
                  >
                    <div class="concept-name">{{ concept.name }}</div>
                    <div class="concept-definition">{{ concept.definition }}</div>
                    <div class="concept-importance">
                      <el-rate
                        v-model="concept.importance"
                        disabled
                        :max="5"
                        :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
                      />
                    </div>
                  </el-card>
                </el-col>
              </el-row>
            </div>

            <div v-else class="concept-detail">
              <el-button @click="selectedConcept = null" style="margin-bottom: 20px">
                <el-icon><ArrowLeft /></el-icon> 返回列表
              </el-button>
              
              <el-descriptions :column="1" border>
                <el-descriptions-item label="概念名称">{{ selectedConcept.name }}</el-descriptions-item>
                <el-descriptions-item label="定义">{{ selectedConcept.definition }}</el-descriptions-item>
                <el-descriptions-item label="重要性">
                  <el-rate
                    v-model="selectedConcept.importance"
                    disabled
                    :max="5"
                  />
                </el-descriptions-item>
                <el-descriptions-item label="上下文">{{ selectedConcept.context }}</el-descriptions-item>
              </el-descriptions>

              <h4 style="margin: 20px 0 10px">相关概念</h4>
              <el-table :data="relatedConcepts" border style="width: 100%">
                <el-table-column prop="name" label="概念" width="180" />
                <el-table-column prop="relation_type" label="关系类型" width="120" />
                <el-table-column prop="definition" label="定义" />
                <el-table-column prop="strength" label="关系强度" width="100">
                  <template #default="scope">
                    <el-progress :percentage="Math.round(scope.row.strength * 100)" :stroke-width="10" />
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>图谱统计</span>
            </div>
          </template>

          <div class="stats">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="总概念数">{{ concepts.length }}</el-descriptions-item>
              <el-descriptions-item label="已搜索">{{ filteredConcepts.length }}</el-descriptions-item>
              <el-descriptions-item label="当前概念">{{ selectedConcept?.name || '无' }}</el-descriptions-item>
            </el-descriptions>

            <h4>关系类型</h4>
            <div class="relation-types">
              <el-tag v-for="type in relationTypes" :key="type" class="relation-tag">
                {{ type }}
              </el-tag>
            </div>

            <h4>使用说明</h4>
            <ul class="instructions">
              <li>点击概念卡片查看详情</li>
              <li>使用搜索框快速查找概念</li>
              <li>查看概念间的关系网络</li>
            </ul>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getConcepts, getConcept } from '../api'

const concepts = ref([])
const selectedConcept = ref(null)
const relatedConcepts = ref([])
const searchKeyword = ref('')
const loading = ref(false)

const relationTypes = ['DEFINES', 'SUPPORTS', 'CONTRADICTS', 'CAUSES', 'EXEMPLIFIES', 'RELATES_TO', 'PART_OF', 'SIMILAR_TO']

const filteredConcepts = computed(() => {
  if (!searchKeyword.value) {
    return concepts.value
  }
  const keyword = searchKeyword.value.toLowerCase()
  return concepts.value.filter(c => 
    c.name.toLowerCase().includes(keyword) || 
    c.definition.toLowerCase().includes(keyword)
  )
})

function handleSearch() {
  // 搜索由computed自动处理
}

async function selectConcept(concept) {
  selectedConcept.value = concept
  loading.value = true
  
  try {
    const response = await getConcept(concept.name)
    relatedConcepts.value = response.data.related_concepts.map(item => ({
      name: item.concept.name,
      definition: item.concept.definition,
      relation_type: item.relation_type,
      strength: item.strength
    }))
  } catch (error) {
    ElMessage.error('获取概念详情失败')
    relatedConcepts.value = []
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const response = await getConcepts()
    concepts.value = response.data.concepts
  } catch (error) {
    ElMessage.error('获取概念列表失败')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.concepts-page {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
}

.graph-container {
  min-height: 500px;
}

.concept-card {
  cursor: pointer;
  margin-bottom: 10px;
  transition: all 0.3s;
}

.concept-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.concept-name {
  font-size: 16px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.concept-definition {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.concept-importance {
  text-align: center;
}

.concept-detail {
  padding: 20px;
}

.stats h4 {
  margin: 20px 0 10px;
  color: #409eff;
}

.relation-types {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 15px;
}

.relation-tag {
  margin: 0;
}

.instructions {
  padding-left: 20px;
  color: #666;
}

.instructions li {
  margin-bottom: 5px;
}
</style>