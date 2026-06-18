<template>
<div class="page-wrap ud">
  <PageHeader :title="u.nickname || '用户详情'" show-back back-to="/users">
    <template #extra>
      <el-tag :type="growthLevelTag(u.growth_level)">{{ growthLevelLabel(u.growth_level) }}</el-tag>
    </template>
  </PageHeader>

  <el-card shadow="never" v-loading="loading">
    <el-tabs v-model="activeTab" class="detail-tabs">
      <el-tab-pane label="概览" name="overview">
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="用户ID">{{ u.id }}</el-descriptions-item>
          <el-descriptions-item label="注册时间">{{ u.created_at?.slice(0, 10) || '-' }}</el-descriptions-item>
          <el-descriptions-item label="最近活跃">{{ u.last_active_at?.slice(0, 10) || '-' }}</el-descriptions-item>
          <el-descriptions-item label="累计打卡">{{ u.total_days || 0 }} 天</el-descriptions-item>
          <el-descriptions-item label="连续打卡">{{ u.continuous_days || 0 }} 天</el-descriptions-item>
          <el-descriptions-item label="总练习时长">{{ u.total_practice_minutes || 0 }} 分钟</el-descriptions-item>
          <el-descriptions-item label="剩余 AI">{{ u.quota?.remaining_today ?? u.remaining_ai ?? '-' }} 次</el-descriptions-item>
          <el-descriptions-item label="成长等级">{{ growthLevelLabel(u.growth_level) }}</el-descriptions-item>
        </el-descriptions>
      </el-tab-pane>

      <el-tab-pane label="权益调整" name="quota">
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12" :md="6">
            <label class="fl">等级</label>
            <el-select v-model="qf.growth_level" size="small" style="width:100%">
              <el-option v-for="(label, val) in GROWTH_LEVEL" :key="val" :label="label" :value="val" />
            </el-select>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <label class="fl">每日 AI 次数</label>
            <el-input-number v-model="qf.daily_ai_quota" :min="0" :max="100" size="small" controls-position="right" style="width:100%" />
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <label class="fl">额外 AI 次数</label>
            <el-input-number v-model="qf.extra_ai_quota" :min="0" :max="100" size="small" controls-position="right" style="width:100%" />
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <label class="fl">操作原因</label>
            <el-input v-model="qf.reason" size="small" placeholder="如：活动奖励" />
          </el-col>
        </el-row>
        <el-button type="primary" size="small" class="mt16" @click="sq" :loading="saving">保存调整</el-button>
      </el-tab-pane>

      <el-tab-pane label="练习记录" name="practice">
        <TableCard>
          <el-table :data="u.recent_practices || []" size="small" empty-text="暂无练习记录">
            <el-table-column prop="title" label="训练题" min-width="160" show-overflow-tooltip />
            <el-table-column prop="score" label="评分" width="70" />
            <el-table-column prop="duration" label="时长(s)" width="80" />
            <el-table-column label="时间" width="150">
              <template #default="{ row }">{{ row.created_at?.slice(0, 16) || '-' }}</template>
            </el-table-column>
          </el-table>
        </TableCard>
      </el-tab-pane>

      <el-tab-pane label="AI 记录" name="ai">
        <TableCard>
          <el-table :data="u.recent_ai_texts || []" size="small" empty-text="暂无 AI 生成记录">
            <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
            <el-table-column prop="scene_type" label="场景" width="100">
              <template #default="{ row }">{{ aiSceneLabel(row.scene_type) }}</template>
            </el-table-column>
            <el-table-column label="时间" width="150">
              <template #default="{ row }">{{ row.created_at?.slice(0, 16) || '-' }}</template>
            </el-table-column>
          </el-table>
        </TableCard>
      </el-tab-pane>
    </el-tabs>
  </el-card>
</div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/api/request'
import PageHeader from '@/components/PageHeader.vue'
import TableCard from '@/components/TableCard.vue'
import { GROWTH_LEVEL, growthLevelLabel, growthLevelTag, aiSceneLabel } from '@/utils/dict'

const route = useRoute()
const loading = ref(false)
const saving = ref(false)
const activeTab = ref('overview')
const u = ref({})
const qf = reactive({ growth_level: '', daily_ai_quota: 3, extra_ai_quota: 0, reason: '' })

async function load() {
  loading.value = true
  try {
    const d = await request.get('/admin/users/' + route.params.id)
    u.value = d
    qf.growth_level = d.growth_level
    qf.daily_ai_quota = d.quota?.daily_ai_quota || 3
    qf.extra_ai_quota = d.quota?.extra_quota || 0
  } catch (e) {
    u.value = {}
    ElMessage.error('加载用户详情失败')
  }
  loading.value = false
}

async function sq() {
  saving.value = true
  try {
    await request.put('/admin/users/' + route.params.id + '/quota', { ...qf })
    ElMessage.success('权益调整成功')
    load()
  } catch (e) {
    ElMessage.error('权益调整失败')
  }
  saving.value = false
}

onMounted(load)
</script>

<style scoped lang="scss">
.detail-tabs :deep(.el-tabs__content) {
  padding-top: 8px;
}
.fl {
  font-size: 12px;
  color: var(--text-muted);
  display: block;
  margin-bottom: 4px;
}
</style>
