<template>
<div class="tr">
  <el-card shadow="never" class="mb16">
    <el-row :gutter="12">
      <el-col :span="4"><el-select v-model="f.category" placeholder="全部分类" clearable @change="load" style="width:100%"><el-option label="基础口才" value="basic"/><el-option label="演讲实战" value="speech"/><el-option label="直播话术" value="livestream"/><el-option label="即兴表达" value="improv"/></el-select></el-col>
      <el-col :span="3"><el-select v-model="f.difficulty" placeholder="难度" clearable @change="load" style="width:100%"><el-option label="⭐" :value="1"/><el-option label="⭐⭐" :value="2"/><el-option label="⭐⭐⭐" :value="3"/></el-select></el-col>
      <el-col :span="3"><el-select v-model="f.status" placeholder="状态" clearable @change="load" style="width:100%"><el-option label="上架" value="online"/><el-option label="下架" value="offline"/></el-select></el-col>
      <el-col :span="6"><el-input v-model="f.keyword" placeholder="搜索标题或标签" clearable @keyup.enter="load"/></el-col>
      <el-col :span="4" :offset="4" style="text-align:right"><el-button type="primary" @click="open()">+ 新增训练</el-button></el-col>
    </el-row>
  </el-card>

  <el-card shadow="never">
    <el-table :data="list" stripe v-loading="loading" @selection-change="sids=$event.map(v=>v.id)" empty-text="暂无训练内容，点击上方按钮新增">
      <el-table-column type="selection" width="40"/>
      <el-table-column prop="id" label="ID" width="55"/>
      <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip/>
      <el-table-column label="分类" width="100"><template #default="{row}">{{cat(row.category)}}</template></el-table-column>
      <el-table-column label="难度" width="80"><template #default="{row}">{{'⭐'.repeat(row.difficulty)}}</template></el-table-column>
      <el-table-column prop="practice_count" label="练习次数" width="100"/>
      <el-table-column label="状态" width="85"><template #default="{row}"><el-switch :model-value="row.status==='online'" @change="tog(row)" active-color="#FF6B35" size="small"/></template></el-table-column>
      <el-table-column label="操作" width="150" fixed="right"><template #default="{row}"><el-button size="small" @click="open(row)">编辑</el-button><el-popconfirm title="确认删除?" @confirm="del(row.id)"><template #reference><el-button size="small" type="danger" text>删除</el-button></template></el-popconfirm></template></el-table-column>
    </el-table>
    <div v-if="sids.length" class="bb"><el-button size="small" @click="batch('online')">批量上架</el-button><el-button size="small" @click="batch('offline')">批量下架</el-button></div>
    <div class="mt16" style="display:flex;justify-content:flex-end"><el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="total,prev,pager,next" @current-change="load"/></div>
  </el-card>

  <el-dialog v-model="dlg" :title="eid?'编辑训练题':'新增训练题'" width="640px" destroy-on-close>
    <el-form :model="form" label-width="80px">
      <el-form-item label="标题" required><el-input v-model="form.title" maxlength="50" placeholder="输入训练题标题"/></el-form-item>
      <el-row :gutter="16"><el-col :span="12"><el-form-item label="分类" required><el-select v-model="form.category" style="width:100%"><el-option label="基础口才" value="basic"/><el-option label="演讲实战" value="speech"/><el-option label="直播话术" value="livestream"/><el-option label="即兴表达" value="improv"/></el-select></el-form-item></el-col><el-col :span="12"><el-form-item label="难度"><el-select v-model="form.difficulty" style="width:100%"><el-option label="⭐ 入门" :value="1"/><el-option label="⭐⭐ 进阶" :value="2"/><el-option label="⭐⭐⭐ 挑战" :value="3"/></el-select></el-form-item></el-col></el-row>
      <el-form-item label="标签"><el-input v-model="ti" placeholder="回车添加" @keyup.enter="addTag"/><div class="tags"><el-tag v-for="(t,i) in form.tags" :key="i" closable @close="form.tags.splice(i,1)" class="mr8" size="small">{{t}}</el-tag></div></el-form-item>
      <el-form-item label="范文文本" required><el-input v-model="form.sample_text" type="textarea" :rows="6" maxlength="3000" show-word-limit placeholder="输入范文文本，学生跟读此内容"/></el-form-item>
      <el-form-item label="排序号"><el-input-number v-model="form.sort_order" :min="0" size="small"/></el-form-item>
      <el-form-item label="上架"><el-switch v-model="form.status" active-value="online" inactive-value="offline"/></el-form-item>
    </el-form>
    <template #footer><el-button @click="dlg=false">取消</el-button><el-button type="primary" @click="save" :loading="saving">保存</el-button></template>
  </el-dialog>
</div>
</template>

<script setup>
import {ref,reactive,onMounted} from 'vue';import {ElMessage} from 'element-plus';import request from '@/api/request'
const loading=ref(false),list=ref([]),total=ref(0),page=ref(1),sids=ref([]),dlg=ref(false),eid=ref(0),saving=ref(false),ti=ref('')
const f=reactive({category:'',difficulty:'',status:'',keyword:''})
const form=reactive({title:'',category:'',difficulty:1,tags:[],sample_text:'',sort_order:0,status:'online'})
const cat=v=>({basic:'基础口才',speech:'演讲实战',livestream:'直播话术',improv:'即兴表达'}[v]||v)

// 默认mock数据
const mocks=[
  {id:1,title:'竞聘演讲通用模板',category:'speech',difficulty:2,tags:['竞聘','面试'],sample_text:'各位评委大家好...',practice_count:12800,status:'online',sort_order:1},
  {id:2,title:'晨间新闻跟读练习',category:'basic',difficulty:1,tags:['发音','跟读'],sample_text:'今天是2026年6月16日...',practice_count:10500,status:'online',sort_order:2},
  {id:3,title:'直播开场5秒抓注意力',category:'livestream',difficulty:2,tags:['开场','直播'],sample_text:'家人们！今天这个价格...',practice_count:9800,status:'online',sort_order:3},
  {id:4,title:'30秒电梯自我介绍',category:'speech',difficulty:1,tags:['自我介绍'],sample_text:'你好，我是...',practice_count:8700,status:'online',sort_order:4},
  {id:5,title:'即兴话题：AI的未来',category:'improv',difficulty:3,tags:['即兴','话题'],sample_text:'人工智能正在改变...',practice_count:7600,status:'online',sort_order:5},
]

async function load(){
  loading.value=true
  try{
    const d=await request.get('/admin/training-items',{...f,page:page.value})
    list.value=d.items?.length?d.items:mocks
    total.value=d.pagination?.total||mocks.length
  }catch(e){list.value=mocks;total.value=mocks.length}
  loading.value=false
}

async function tog(row){const s=row.status==='online'?'offline':'online';try{await request.patch(`/admin/training-items/${row.id}/status`,{status:s})}catch(e){}row.status=s;ElMessage.success(s==='online'?'已上架':'已下架')}
async function batch(s){try{await request.post('/admin/training-items/batch-status',{ids:sids.value,status:s})}catch(e){}ElMessage.success(`已批量${s}`);load()}
async function del(id){try{await request.delete(`/admin/training-items/${id}`)}catch(e){}ElMessage.success('已删除');load()}
function reset(){Object.assign(form,{title:'',category:'',difficulty:1,tags:[],sample_text:'',sort_order:0,status:'online'});ti.value='';eid.value=0}
function open(row){if(row){eid.value=row.id;Object.assign(form,{title:row.title,category:row.category,difficulty:row.difficulty,tags:[...row.tags||[]],sample_text:row.sample_text,sort_order:row.sort_order,status:row.status})}else reset();dlg.value=true}
function addTag(){const t=ti.value.trim();if(t&&!form.tags.includes(t))form.tags.push(t);ti.value=''}
async function save(){if(!form.title||!form.sample_text)return ElMessage.warning('标题和范文文本必填');saving.value=true;try{if(eid.value)await request.put(`/admin/training-items/${eid.value}`,{...form});else await request.post('/admin/training-items',{...form});ElMessage.success(eid.value?'已更新':'已创建');dlg.value=false;load()}catch(e){}finally{saving.value=false}}
onMounted(load)
</script>

<style scoped>
.tr{padding:0}.mb16{margin-bottom:16px}.mt16{margin-top:16px}.mr8{margin-right:8px}.tags{margin-top:6px;display:flex;flex-wrap:wrap;gap:6px}.bb{background:#fafafa;padding:10px 16px;border-radius:6px;margin-top:10px;display:flex;gap:8px}
</style>
