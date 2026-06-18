<template>
  <el-card shadow="never" class="set-card">
    <template #header>
      <div class="card-top">
        <span class="card-hd">📋 操作日志</span>
        <el-pagination
          v-model:current-page="page" small layout="prev,next"
          :page-size="pageSize" :total="total" background @current-change="load"
        />
      </div>
    </template>

    <div v-loading="loading" class="timeline">
      <el-empty v-if="!logs.length && !loading" description="暂无操作日志"/>
      <div class="tl-item" v-for="(item,i) in logs" :key="item.id||i">
        <div class="tl-dot" :style="{background: tagColor(item.action)}"></div>
        <div class="tl-line" v-if="i < logs.length-1"></div>
        <div class="tl-body">
          <div class="tl-head">
            <el-tag size="small" effect="plain">{{ item.action }}</el-tag>
            <span class="tl-target">{{ item.target_type }}{{ item.target_id ? ' #' + item.target_id : '' }}</span>
          </div>
          <div class="tl-detail">{{ formatDetail(item.detail) }}</div>
          <div class="tl-time">{{ item.time }}</div>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/api/request'

const page = ref(1)
const pageSize = 20
const total = ref(0)
const logs = ref([])
const loading = ref(false)

function tagColor(action) {
  if (!action) return '#999'
  if (action.includes('新增')) return '#52C41A'
  if (action.includes('编辑') || action.includes('更新')) return '#1890FF'
  if (action.includes('删除')) return '#FF4D4F'
  return '#FAAD14'
}

function formatDetail(d) {
  if (!d) return '-'
  if (typeof d === 'string') return d
  if (d.title) return d.title
  return JSON.stringify(d)
}

async function load() {
  loading.value = true
  try {
    const d = await request.get('/admin/operation-logs', { page: page.value, page_size: pageSize })
    logs.value = d.items || []
    total.value = d.pagination?.total || 0
  } catch (e) {
    logs.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.page{padding:0}.set-card{border-radius:10px}
.card-top{display:flex;justify-content:space-between;align-items:center}
.card-hd{font-weight:600}
.timeline{padding:8px 0 0 12px;min-height:120px}
.tl-item{display:flex;gap:12px;position:relative;padding-bottom:20px}
.tl-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0;margin-top:6px;z-index:1}
.tl-line{position:absolute;left:4px;top:22px;width:2px;height:calc(100% - 16px);background:#e8e8e8}
.tl-body{flex:1;min-width:0}
.tl-head{display:flex;align-items:center;gap:8px;margin-bottom:4px}
.tl-target{font-size:13px;color:#333;font-weight:500}
.tl-detail{font-size:13px;color:#666;line-height:1.5;margin-bottom:2px}
.tl-time{font-size:11px;color:#bbb}
</style>
