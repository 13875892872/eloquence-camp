<template>
<div class="page-wrap">
  <FilterCard @search="onSearch" @reset="resetFilters">
    <el-row :gutter="12">
      <el-col :span="10">
        <el-input v-model="kw" placeholder="搜索昵称或用户ID" clearable @keyup.enter="onSearch" />
      </el-col>
      <el-col :span="6">
        <el-select v-model="lv" placeholder="等级筛选" clearable style="width:100%">
          <el-option v-for="(label, val) in GROWTH_LEVEL" :key="val" :label="label" :value="val" />
        </el-select>
      </el-col>
    </el-row>
  </FilterCard>

  <TableCard>
    <el-table :data="list" stripe v-loading="loading" empty-text="暂无用户数据">
      <el-table-column width="50">
        <template #default="{ row }">
          <el-avatar :size="34" :style="{ background: 'var(--el-color-primary)' }">
            {{ row.nickname?.charAt(0) || 'U' }}
          </el-avatar>
        </template>
      </el-table-column>
      <el-table-column prop="nickname" label="昵称" min-width="120"/>
      <el-table-column prop="total_days" label="累计打卡" width="85"/>
      <el-table-column prop="continuous_days" label="连续" width="70"/>
      <el-table-column label="等级" width="85">
        <template #default="{ row }">
          <el-tag size="small" :type="growthLevelTag(row.growth_level)">
            {{ growthLevelLabel(row.growth_level) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="remaining_ai" label="剩余AI" width="75"/>
      <el-table-column label="注册时间" width="110">
        <template #default="{ row }">{{ row.created_at?.slice(0, 10) || '-' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="80" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" size="small" @click="$router.push('/users/' + row.id)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>
    <template #footer>
      <el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="total,prev,pager,next" @current-change="load"/>
    </template>
  </TableCard>
</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/api/request'
import FilterCard from '@/components/FilterCard.vue'
import TableCard from '@/components/TableCard.vue'
import { GROWTH_LEVEL, growthLevelLabel, growthLevelTag } from '@/utils/dict'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const kw = ref('')
const lv = ref('')

function onSearch() {
  page.value = 1
  load()
}

function resetFilters() {
  kw.value = ''
  lv.value = ''
  page.value = 1
  load()
}

async function load() {
  loading.value = true
  try {
    const d = await request.get('/admin/users', { page: page.value, keyword: kw.value, growth_level: lv.value })
    list.value = d.items || []
    total.value = d.pagination?.total || 0
  } catch (e) {
    list.value = []
    total.value = 0
  }
  loading.value = false
}

onMounted(load)
</script>

<style scoped>
.pager { display: flex; justify-content: flex-end; }
</style>
