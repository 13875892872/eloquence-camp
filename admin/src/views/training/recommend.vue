<template>
<div class="rc">
  <el-card shadow="never" header="首页热门推荐配置">
    <el-alert title="配置后前端首页「热门推荐」区域实时生效，支持3个推荐位" type="info" :closable="false" show-icon class="mb16"/>
    <el-form label-width="80px">
      <div v-for="s in slots" :key="s.slot" class="slot-block">
        <el-form-item :label="'推荐位 '+s.slot">
          <el-row :gutter="12" style="width:100%">
            <el-col :span="10"><el-select v-model="s.training_item_id" placeholder="选择训练题（空=用自定义标题）" clearable filterable style="width:100%" :filter-method="search"><el-option v-for="it in items" :key="it.id" :label="it.title" :value="it.id"/></el-select></el-col>
            <el-col :span="8"><el-input v-model="s.custom_title" placeholder="自定义标题（覆盖训练题标题）" clearable/></el-col>
            <el-col :span="4"><el-select v-model="s.refresh_mode"><el-option label="手动固定" value="manual"/><el-option label="每日随机" value="daily_random"/></el-select></el-col>
          </el-row>
        </el-form-item>
      </div>
    </el-form>
    <el-button type="primary" @click="save" :loading="saving">保存配置</el-button>
  </el-card>
</div>
</template>

<script setup>
import {ref,onMounted} from 'vue';import {ElMessage} from 'element-plus';import request from '@/api/request'
const slots=ref([]),items=ref([]),saving=ref(false)

const defaultSlots=[{slot:1,training_item_id:null,custom_title:'竞聘演讲通用模板',refresh_mode:'manual'},{slot:2,training_item_id:null,custom_title:'跟读练习：新闻播音腔',refresh_mode:'manual'},{slot:3,training_item_id:null,custom_title:'即兴话题："AI会取代你吗"',refresh_mode:'daily_random'}]

async function load(){
  try{const d=await request.get('/admin/recommend-config');slots.value=d.slots?.length?d.slots:defaultSlots}catch(e){slots.value=defaultSlots}
  try{const r=await request.get('/admin/training-items',{status:'online',page_size:100});items.value=r.items||[]}catch(e){}
}
async function search(kw){try{const r=await request.get('/admin/training-items',{keyword:kw,status:'online',page_size:50});items.value=r.items||[]}catch(e){}}
async function save(){
  saving.value=true
  try{
    await request.put('/admin/recommend-config',{slots:slots.value})
    ElMessage.success('推荐配置已保存')
  }catch(e){
    ElMessage.error('推荐配置保存失败')
  }finally{saving.value=false}
}
onMounted(load)
</script>

<style scoped>.rc{padding:0}.mb16{margin-bottom:16px}.slot-block{background:#fafafa;border-radius:8px;padding:16px;margin-bottom:12px}</style>
