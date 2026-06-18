<template>
<div class="page-wrap">
  <FilterCard @search="onSearch" @reset="resetFilters">
    <el-row :gutter="12">
      <el-col :span="5">
        <el-select v-model="f.category" placeholder="全部分类" clearable style="width:100%">
          <el-option v-for="(label, val) in TRAINING_CATEGORY" :key="val" :label="label" :value="val" />
        </el-select>
      </el-col>
      <el-col :span="4">
        <el-select v-model="f.difficulty" placeholder="难度" clearable style="width:100%">
          <el-option label="⭐" :value="1" />
          <el-option label="⭐⭐" :value="2" />
          <el-option label="⭐⭐⭐" :value="3" />
        </el-select>
      </el-col>
      <el-col :span="4">
        <el-select v-model="f.status" placeholder="状态" clearable style="width:100%">
          <el-option label="上架" value="online" />
          <el-option label="下架" value="offline" />
        </el-select>
      </el-col>
      <el-col :span="4">
        <el-select v-model="f.source" placeholder="来源" clearable style="width:100%">
          <el-option label="人工创建" value="manual" />
          <el-option label="AI生成" value="ai_generated" />
        </el-select>
      </el-col>
      <el-col :span="7">
        <el-input v-model="f.keyword" placeholder="搜索标题或标签" clearable @keyup.enter="onSearch" />
      </el-col>
    </el-row>
    <template #actions>
      <el-button type="primary" plain @click="open()">+ 新增训练</el-button>
    </template>
  </FilterCard>

  <TableCard>
    <el-table :data="list" stripe v-loading="loading" @selection-change="sids=$event.map(v=>v.id)" empty-text="暂无训练内容，点击上方按钮新增">
      <el-table-column type="selection" width="40"/>
      <el-table-column prop="id" label="ID" width="55"/>
      <el-table-column prop="title" label="标题" min-width="160" show-overflow-tooltip/>
      <el-table-column label="分类" width="100">
        <template #default="{ row }">{{ trainingCategoryLabel(row.category) }}</template>
      </el-table-column>
      <el-table-column label="难度" width="70">
        <template #default="{ row }">{{ '⭐'.repeat(row.difficulty) }}</template>
      </el-table-column>
      <el-table-column label="来源" width="70">
        <template #default="{ row }">
          <el-tag :type="row.source==='ai_generated'?'warning':''" size="small">
            {{ row.source==='ai_generated' ? 'AI' : '人工' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="practice_count" label="练习次数" width="90"/>
      <el-table-column label="状态" width="75">
        <template #default="{ row }">
          <el-switch :model-value="row.status==='online'" @change="tog(row)" size="small"/>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" size="small" @click="open(row)">编辑</el-button>
          <el-popconfirm title="确认删除?" @confirm="del(row.id)">
            <template #reference>
              <el-button link type="danger" size="small">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    <div v-if="sids.length" class="batch-bar">
      <el-button size="small" type="success" @click="batch('online')">批量上架</el-button>
      <el-button size="small" type="danger" @click="batch('offline')">批量下架</el-button>
    </div>
    <template #footer>
      <el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="total,prev,pager,next" @current-change="load"/>
    </template>
  </TableCard>

  <el-dialog v-model="dlg" :title="eid?'编辑训练题':'新增训练题'" width="640px" destroy-on-close>
    <el-form :model="form" label-width="80px">
      <el-form-item label="标题" required>
        <el-input v-model="form.title" maxlength="50" placeholder="输入训练题标题"/>
      </el-form-item>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="分类" required>
            <el-select v-model="form.category" style="width:100%">
              <el-option v-for="(label, val) in TRAINING_CATEGORY" :key="val" :label="label" :value="val" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="难度">
            <el-select v-model="form.difficulty" style="width:100%">
              <el-option label="⭐ 入门" :value="1"/>
              <el-option label="⭐⭐ 进阶" :value="2"/>
              <el-option label="⭐⭐⭐ 挑战" :value="3"/>
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="标签">
        <el-input v-model="ti" placeholder="回车添加" @keyup.enter="addTag"/>
        <div class="tags">
          <el-tag v-for="(t,i) in form.tags" :key="i" closable @close="form.tags.splice(i,1)" class="mr8" size="small">{{ t }}</el-tag>
        </div>
      </el-form-item>
      <el-form-item label="范文文本" required>
        <el-input v-model="form.sample_text" type="textarea" :rows="6" maxlength="3000" show-word-limit placeholder="输入范文文本，学生跟读此内容"/>
      </el-form-item>
      <el-form-item label="来源">
        <el-radio-group v-model="form.source">
          <el-radio label="manual">人工创建</el-radio>
          <el-radio label="ai_generated">AI生成</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="排序号">
        <el-input-number v-model="form.sort_order" :min="0" size="small"/>
      </el-form-item>
      <el-form-item label="上架">
        <el-switch v-model="form.status" active-value="online" inactive-value="offline"/>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dlg=false">取消</el-button>
      <el-button type="primary" @click="save" :loading="saving">保存</el-button>
    </template>
  </el-dialog>
</div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'
import FilterCard from '@/components/FilterCard.vue'
import TableCard from '@/components/TableCard.vue'
import { TRAINING_CATEGORY, trainingCategoryLabel } from '@/utils/dict'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const sids = ref([])
const dlg = ref(false)
const eid = ref(0)
const saving = ref(false)
const ti = ref('')
const f = reactive({ category: '', difficulty: '', status: '', keyword: '', source: '' })
const form = reactive({ title: '', category: '', difficulty: 1, tags: [], sample_text: '', sort_order: 0, status: 'online', source: 'manual' })

function onSearch() {
  page.value = 1
  load()
}

function resetFilters() {
  Object.assign(f, { category: '', difficulty: '', status: '', keyword: '', source: '' })
  page.value = 1
  load()
}

async function load() {
  loading.value = true
  try {
    const d = await request.get('/admin/training-items', { ...f, page: page.value })
    list.value = d.items || []
    total.value = d.pagination?.total || 0
  } catch (e) {
    list.value = []
    total.value = 0
  }
  loading.value = false
}

async function tog(row) {
  const s = row.status === 'online' ? 'offline' : 'online'
  try {
    await request.patch(`/admin/training-items/${row.id}/status`, { status: s })
    row.status = s
    ElMessage.success(s === 'online' ? '已上架' : '已下架')
  } catch (e) {}
}

async function batch(s) {
  try {
    await request.post('/admin/training-items/batch-status', { ids: sids.value, status: s })
    ElMessage.success(`已批量${s === 'online' ? '上架' : '下架'}`)
    load()
  } catch (e) {}
}

async function del(id) {
  try {
    await request.delete(`/admin/training-items/${id}`)
    ElMessage.success('已删除')
    load()
  } catch (e) {}
}

function reset() {
  Object.assign(form, { title: '', category: '', difficulty: 1, tags: [], sample_text: '', sort_order: 0, status: 'online', source: 'manual' })
  ti.value = ''
  eid.value = 0
}

function open(row) {
  if (row) {
    eid.value = row.id
    Object.assign(form, {
      title: row.title, category: row.category, difficulty: row.difficulty,
      tags: [...row.tags || []], sample_text: row.sample_text,
      sort_order: row.sort_order, status: row.status, source: row.source || 'manual',
    })
  } else {
    reset()
  }
  dlg.value = true
}

function addTag() {
  const t = ti.value.trim()
  if (t && !form.tags.includes(t)) form.tags.push(t)
  ti.value = ''
}

async function save() {
  if (!form.title || !form.sample_text) return ElMessage.warning('标题和范文文本必填')
  saving.value = true
  try {
    if (eid.value) await request.put(`/admin/training-items/${eid.value}`, { ...form })
    else await request.post('/admin/training-items', { ...form })
    ElMessage.success(eid.value ? '已更新' : '已创建')
    dlg.value = false
    load()
  } catch (e) {}
  finally { saving.value = false }
}

onMounted(load)
</script>

<style scoped>
.tags { margin-top: 6px; display: flex; flex-wrap: wrap; gap: 6px; }
.mr8 { margin-right: 8px; }
.batch-bar {
  background: #fafafa;
  padding: 10px 16px;
  border-radius: 6px;
  margin-top: 10px;
  display: flex;
  gap: 8px;
}
.pager { display: flex; justify-content: flex-end; }
</style>
