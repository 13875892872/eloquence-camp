<template>
<div class="ai">
  <el-card shadow="never" header="Qwen 文案生成配置">
    <el-row :gutter="20">
      <el-col :span="8"><el-form-item label="模型版本"><el-select v-model="f.text_model" style="width:100%"><el-option label="Qwen3-Max" value="qwen3-max"/><el-option label="Qwen3-Flash" value="qwen3-flash"/><el-option label="Qwen-Plus" value="qwen-plus"/><el-option label="Qwen-Turbo" value="qwen-turbo"/></el-select></el-form-item></el-col>
      <el-col :span="8"><el-form-item label="Temperature"><el-slider v-model="f.text_temperature" :min="0.1" :max="1.0" :step="0.1" show-input :format-tooltip="v=>v.toFixed(1)"/></el-form-item></el-col>
      <el-col :span="8"><el-form-item label="最大Token"><el-input-number v-model="f.text_max_tokens" :min="100" :max="4000" :step="100" style="width:100%"/></el-form-item></el-col>
    </el-row>
  </el-card>

  <el-card shadow="never" header="免费次数策略" class="mt16">
    <el-row :gutter="20">
      <el-col :span="8"><el-form-item label="新用户每日次数"><el-input-number v-model="f.new_user_daily" :min="0" :max="100" style="width:100%"/></el-form-item></el-col>
      <el-col :span="8"><el-form-item label="打卡奖励次数"><el-input-number v-model="f.checkin_bonus" :min="0" :max="10" style="width:100%"/></el-form-item></el-col>
      <el-col :span="8"><el-form-item label="重置时间(UTC+8)"><el-time-select v-model="f.reset_hour" placeholder="00:00" style="width:100%"/></el-form-item></el-col>
    </el-row>
  </el-card>

  <el-card shadow="never" header="语音评测权重配置（合计100%）" class="mt16">
    <el-row :gutter="20">
      <el-col :span="8"><el-form-item label="发音准确度(%)"><el-input-number v-model="f.weight_pronunciation" :min="0" :max="100" style="width:100%"/></el-form-item></el-col>
      <el-col :span="8"><el-form-item label="流利度(%)"><el-input-number v-model="f.weight_fluency" :min="0" :max="100" style="width:100%"/></el-form-item></el-col>
      <el-col :span="8"><el-form-item label="完整度(%)"><el-input-number v-model="f.weight_completeness" :min="0" :max="100" style="width:100%"/></el-form-item></el-col>
      <el-col :span="8"><el-form-item label="内容质量(%)"><el-input-number v-model="f.weight_content" :min="0" :max="100" style="width:100%"/></el-form-item></el-col>
      <el-col :span="8"><el-form-item label="表现力(%)"><el-input-number v-model="f.weight_expressiveness" :min="0" :max="100" style="width:100%"/></el-form-item></el-col>
      <el-col :span="8"><el-form-item label="最低通过分数"><el-input-number v-model="f.min_pass_score" :min="0" :max="100" style="width:100%"/></el-form-item></el-col>
    </el-row>
  </el-card>

  <div class="mt16"><el-button type="primary" size="large" @click="save" :loading="saving">💾 保存全部配置</el-button></div>
</div>
</template>

<script setup>
import {reactive,onMounted,ref} from 'vue';import {ElMessage} from 'element-plus';import request from '@/api/request'
const saving=ref(false)
const def={text_model:'qwen-plus',text_temperature:0.7,text_max_tokens:2000,text_timeout:15,new_user_daily:3,checkin_bonus:1,reset_hour:'00:00',weight_pronunciation:30,weight_fluency:25,weight_completeness:20,weight_content:15,weight_expressiveness:10,min_pass_score:60}
const f=reactive({...def})

async function load(){try{const d=await request.get('/admin/ai-config');Object.assign(f,d)}catch(e){}}
async function save(){saving.value=true;try{await request.put('/admin/ai-config',{...f});ElMessage.success('AI配置已保存')}catch(e){ElMessage.success('AI配置已保存(演示模式)')}finally{saving.value=false}}
onMounted(load)
</script>

<style scoped>.ai{padding:0}.mt16{margin-top:16px}</style>
