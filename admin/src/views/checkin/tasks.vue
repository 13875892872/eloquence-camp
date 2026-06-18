<template>
<div class="ct">
  <el-card shadow="never" header="每日打卡任务配置">
    <el-alert title="修改后次日零点生效。每个任务按序解锁，前序完成后才开放下一个" type="info" :closable="false" show-icon class="mb16"/>

    <el-form label-width="100px">
      <el-form-item label="每日任务数量"><el-radio-group v-model="cfg.task_count" size="small"><el-radio-button :value="2">2个</el-radio-button><el-radio-button :value="3">3个</el-radio-button></el-radio-group></el-form-item>
      <el-form-item label="顺序完成"><el-switch v-model="cfg.sequential_mode"/></el-form-item>
    </el-form>

    <el-divider/>
    <div v-for="(t,i) in cfg.tasks" :key="t.task_index" class="tb">
      <div class="th"><strong>任务{{t.task_index}}</strong> <el-switch v-model="t.is_active" size="small" active-text="启用"/></div>
      <el-row :gutter="12">
        <el-col :span="8"><label class="fl">标题</label><el-input v-model="t.title" size="small"/></el-col>
        <el-col :span="8"><label class="fl">副标题</label><el-input v-model="t.subtitle" size="small"/></el-col>
        <el-col :span="4"><label class="fl">最小时长(s)</label><el-input-number v-model="t.min_duration" :min="10" :max="300" size="small" controls-position="right" style="width:100%"/></el-col>
      </el-row>
      <el-row :gutter="12" class="mt8">
        <el-col :span="8"><label class="fl">范本来源</label><el-select v-model="t.source_type" size="small" style="width:100%"><el-option label="随机抽取" value="random"/><el-option label="固定内容" value="fixed"/></el-select></el-col>
        <el-col :span="6"><label class="fl">抽取分类</label><el-select v-model="t.source_category" size="small" style="width:100%"><el-option label="基础口才" value="basic"/><el-option label="演讲实战" value="speech"/><el-option label="直播话术" value="livestream"/><el-option label="即兴表达" value="improv"/><el-option label="面试模拟" value="interview"/></el-select></el-col>
        <el-col :span="3"><label class="fl">难度低</label><el-select v-model="t.source_difficulty_min" size="small" style="width:100%"><el-option :value="1" label="⭐"/><el-option :value="2" label="⭐⭐"/><el-option :value="3" label="⭐⭐⭐"/></el-select></el-col>
        <el-col :span="3"><label class="fl">难度高</label><el-select v-model="t.source_difficulty_max" size="small" style="width:100%"><el-option :value="1" label="⭐"/><el-option :value="2" label="⭐⭐"/><el-option :value="3" label="⭐⭐⭐"/></el-select></el-col>
      </el-row>
    </div>

    <el-button type="primary" @click="save" :loading="saving" class="mt16">保存配置</el-button>
  </el-card>
</div>
</template>

<script setup>
import {reactive,onMounted,ref} from 'vue';import {ElMessage} from 'element-plus';import request from '@/api/request'
const saving=ref(false)
const defaults={task_count:3,sequential_mode:true,tasks:[{task_index:1,title:'跟读朗读',subtitle:'晨间新闻跟读 3min',min_duration:60,source_type:'random',source_category:'basic',source_difficulty_min:1,source_difficulty_max:2,is_active:true},{task_index:2,title:'短句表达',subtitle:'给定场景组织语言 5min',min_duration:30,source_type:'random',source_category:'improv',source_difficulty_min:1,source_difficulty_max:2,is_active:true},{task_index:3,title:'即兴口述',subtitle:'随机话题即兴发挥 5min',min_duration:30,source_type:'random',source_category:'improv',source_difficulty_min:1,source_difficulty_max:3,is_active:true}]}
const cfg=reactive(JSON.parse(JSON.stringify(defaults)))

async function load(){try{const d=await request.get('/admin/checkin-config');if(d.tasks?.length)Object.assign(cfg,d)}catch(e){}}
async function save(){
  saving.value=true
  try{
    await request.put('/admin/checkin-config',{tasks:cfg.tasks,task_count:cfg.task_count,sequential_mode:cfg.sequential_mode})
    ElMessage.success('打卡配置已保存')
  }catch(e){
    ElMessage.error('打卡配置保存失败')
  }finally{saving.value=false}
}
onMounted(load)
</script>

<style scoped>.ct{padding:0}.mb16{margin-bottom:16px}.mt8{margin-top:8px}.mt16{margin-top:16px}.tb{background:#fafafa;border-radius:8px;padding:16px;margin-bottom:12px}.th{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}.fl{font-size:12px;color:#999;display:block;margin-bottom:4px}</style>
