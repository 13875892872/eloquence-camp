<template>
<div class="cg">
  <el-card shadow="never" header="成长目标配置">
    <el-alert title="修改后仅对新达成的用户生效，已达成用户不变" type="warning" :closable="false" show-icon class="mb16"/>

    <div v-for="g in goals" :key="g.goal_level" class="gb">
      <el-row :gutter="10" align="middle">
        <el-col :span="1"><span style="font-size:22px">{{g.badge_icon}}</span></el-col>
        <el-col :span="3"><label class="fl">目标名称</label><el-input v-model="g.goal_name" size="small"/></el-col>
        <el-col :span="3"><label class="fl">累计天数</label><el-input-number v-model="g.required_days" :min="1" :max="365" size="small" controls-position="right" style="width:100%"/></el-col>
        <el-col :span="3"><label class="fl">解锁素材等级</label><el-input v-model="g.reward_level" size="small" placeholder="中级/高级/全解锁"/></el-col>
        <el-col :span="3"><label class="fl">额外AI次数</label><el-input-number v-model="g.reward_extra_ai" :min="0" :max="999" size="small" controls-position="right" style="width:100%"/></el-col>
        <el-col :span="3"><label class="fl">徽章图标</label><el-input v-model="g.badge_icon" size="small"/></el-col>
        <el-col :span="3"><label class="fl">徽章名称</label><el-input v-model="g.badge_name" size="small"/></el-col>
        <el-col :span="2"><el-switch v-model="g.is_active" size="small"/></el-col>
      </el-row>
    </div>

    <el-button type="primary" @click="save" :loading="saving" class="mt16">保存配置</el-button>
  </el-card>
</div>
</template>

<script setup>
import {ref,onMounted} from 'vue';import {ElMessage} from 'element-plus';import request from '@/api/request'
const saving=ref(false),goals=ref([])
const defaults=[{goal_level:'beginner',goal_name:'7天入门',required_days:7,reward_level:'中级',reward_extra_ai:1,badge_icon:'🏅',badge_name:'口才新星',is_active:true},{goal_level:'advanced',goal_name:'30天进阶',required_days:30,reward_level:'高级',reward_extra_ai:3,badge_icon:'🥈',badge_name:'表达达人',is_active:true},{goal_level:'expert',goal_name:'60天达人',required_days:60,reward_level:'大师',reward_extra_ai:5,badge_icon:'🥇',badge_name:'演讲大师',is_active:true},{goal_level:'master',goal_name:'100天大师',required_days:100,reward_level:'全解锁',reward_extra_ai:-1,badge_icon:'👑',badge_name:'口才王者',is_active:true}]

async function load(){try{const d=await request.get('/admin/growth-config');goals.value=d.goals?.length?d.goals:defaults}catch(e){goals.value=defaults}}
async function save(){
  saving.value=true
  try{
    await request.put('/admin/growth-config',{goals:goals.value})
    ElMessage.success('成长目标已保存')
  }catch(e){
    ElMessage.error('成长目标保存失败')
  }finally{saving.value=false}
}
onMounted(load)
</script>

<style scoped>.cg{padding:0}.mb16{margin-bottom:16px}.mt16{margin-top:16px}.gb{background:#fafafa;border-radius:8px;padding:10px 14px;margin-bottom:8px}.fl{font-size:11px;color:#999;display:block;margin-bottom:2px}</style>
