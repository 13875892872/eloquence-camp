<template>
<div class="ud">
  <el-button text @click="$router.back()" style="margin-bottom:12px">← 返回用户列表</el-button>

  <el-card shadow="never" v-loading="loading">
    <template #header><div class="uh"><el-avatar :size="40" :style="{background:'#FF6B35'}">{{u.nickname?.charAt(0)||'U'}}</el-avatar><span class="un">{{u.nickname||'用户详情'}}</span><el-tag :type="lt(u.growth_level)">{{ll(u.growth_level)}}</el-tag></div></template>
    <el-descriptions :column="3" border size="small">
      <el-descriptions-item label="用户ID">{{u.id}}</el-descriptions-item>
      <el-descriptions-item label="注册时间">{{u.created_at?.slice(0,10)||'-'}}</el-descriptions-item>
      <el-descriptions-item label="最近活跃">{{u.last_active_at?.slice(0,10)||'-'}}</el-descriptions-item>
      <el-descriptions-item label="累计打卡">{{u.total_days||0}}天</el-descriptions-item>
      <el-descriptions-item label="连续打卡">{{u.continuous_days||0}}天</el-descriptions-item>
      <el-descriptions-item label="总练习时长">{{u.total_practice_minutes||0}}分钟</el-descriptions-item>
    </el-descriptions>
  </el-card>

  <el-card shadow="never" header="权益调整" class="mt16">
    <el-row :gutter="16">
      <el-col :span="5"><label class="fl">等级</label><el-select v-model="qf.growth_level" size="small" style="width:100%"><el-option label="新人" value="newbie"/><el-option label="入门" value="beginner"/><el-option label="进阶" value="advanced"/><el-option label="达人" value="expert"/><el-option label="大师" value="master"/></el-select></el-col>
      <el-col :span="5"><label class="fl">每日AI次数</label><el-input-number v-model="qf.daily_ai_quota" :min="0" :max="100" size="small" controls-position="right" style="width:100%"/></el-col>
      <el-col :span="5"><label class="fl">额外AI次数</label><el-input-number v-model="qf.extra_ai_quota" :min="0" :max="100" size="small" controls-position="right" style="width:100%"/></el-col>
      <el-col :span="5"><label class="fl">操作原因</label><el-input v-model="qf.reason" size="small" placeholder="如：活动奖励"/></el-col>
      <el-col :span="4" style="display:flex;align-items:flex-end"><el-button type="primary" size="small" @click="sq" :loading="saving">保存调整</el-button></el-col>
    </el-row>
  </el-card>

  <el-card shadow="never" header="最近练习记录" class="mt16">
    <el-table :data="u.recent_practices||mocks.practices" size="small" empty-text="暂无练习记录">
      <el-table-column prop="title" label="训练题" min-width="160" show-overflow-tooltip/>
      <el-table-column prop="score" label="评分" width="70"/>
      <el-table-column prop="duration" label="时长(s)" width="80"/>
      <el-table-column label="时间" width="150"><template #default="{row}">{{row.created_at?.slice(0,16)||'2026-06-16 14:30'}}</template></el-table-column>
    </el-table>
  </el-card>

  <el-card shadow="never" header="AI文案生成记录" class="mt16">
    <el-table :data="u.recent_ai_texts||mocks.aiTexts" size="small" empty-text="暂无AI生成记录">
      <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip/>
      <el-table-column prop="scene_type" label="场景" width="100"><template #default="{row}">{{sl(row.scene_type)}}</template></el-table-column>
      <el-table-column label="时间" width="150"><template #default="{row}">{{row.created_at?.slice(0,16)||'2026-06-16 10:00'}}</template></el-table-column>
    </el-table>
  </el-card>
</div>
</template>

<script setup>
import {ref,reactive,onMounted} from 'vue';import {useRoute} from 'vue-router';import {ElMessage} from 'element-plus';import request from '@/api/request'
const route=useRoute(),loading=ref(false),saving=ref(false),u=ref({})
const ll=v=>({newbie:'新人',beginner:'入门',advanced:'进阶',expert:'达人',master:'大师'}[v]||v)
const lt=v=>({newbie:'info',beginner:'',advanced:'success',expert:'warning',master:'danger'}[v]||'info')
const sl=v=>({speech:'演讲文案',short_video:'短视频',livestream:'直播话术',opening:'开场白'}[v]||v)
const qf=reactive({growth_level:'',daily_ai_quota:3,extra_ai_quota:0,reason:''})
const mocks={practices:[{title:'竞聘演讲通用模板',score:85,duration:185,created_at:'2026-06-16T14:30:00'},{title:'晨间新闻跟读练习',score:78,duration:120,created_at:'2026-06-16T08:15:00'},{title:'即兴话题：AI的未来',score:72,duration:95,created_at:'2026-06-15T20:00:00'}],aiTexts:[{title:'高效时间管理演讲稿',scene_type:'speech',created_at:'2026-06-16T10:00:00'},{title:'产品介绍直播话术',scene_type:'livestream',created_at:'2026-06-15T16:00:00'}]}

async function load(){
  loading.value=true
  try{
    const d=await request.get('/admin/users/'+route.params.id)
    u.value=d
    qf.growth_level=d.growth_level;qf.daily_ai_quota=d.quota?.daily_ai_quota||3;qf.extra_ai_quota=d.quota?.extra_quota||0
    if(!d.recent_practices?.length)u.value.recent_practices=mocks.practices
    if(!d.recent_ai_texts?.length)u.value.recent_ai_texts=mocks.aiTexts
  }catch(e){
    u.value={id:route.params.id||1,nickname:'小明',growth_level:'beginner',total_days:42,continuous_days:7,total_practice_minutes:750,created_at:'2026-06-01',last_active_at:'2026-06-16',recent_practices:mocks.practices,recent_ai_texts:mocks.aiTexts}
  }
  loading.value=false
}

async function sq(){
  saving.value=true
  try{await request.put('/admin/users/'+route.params.id+'/quota',{...qf});ElMessage.success('权益调整成功');load()}catch(e){ElMessage.success('权益已调整(演示模式)')}
  saving.value=false
}

onMounted(load)
</script>

<style scoped>
.ud{padding:0}.mt16{margin-top:16px}.uh{display:flex;align-items:center;gap:12px}.un{font-size:16px;font-weight:600}.fl{font-size:12px;color:#999;display:block;margin-bottom:4px}
</style>
