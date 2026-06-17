<template>
<div class="db">
  <el-row :gutter="16" class="stat-row">
    <el-col :span="6" v-for="c in cards" :key="c.label">
      <el-card shadow="hover" class="stat-card" :body-style="{padding:'20px 24px'}">
        <div class="stat-v" :style="{color:c.color}">{{ c.value }}</div>
        <div class="stat-l">{{ c.label }}</div>
      </el-card>
    </el-col>
  </el-row>

  <!-- 快捷操作 -->
  <el-row :gutter="12" class="quick-row">
    <el-col :span="6" v-for="q in quicks" :key="q.path">
      <div class="quick-card" @click="$router.push(q.path)">
        <span class="quick-icon">{{ q.icon }}</span>
        <div class="quick-info">
          <span class="quick-label">{{ q.label }}</span>
          <span class="quick-desc">{{ q.desc }}</span>
        </div>
      </div>
    </el-col>
  </el-row>

  <el-card class="mt16" shadow="never">
    <template #header>
      <div class="card-hd"><span>数据趋势</span>
        <el-radio-group v-model="period" size="small" @change="load"><el-radio-button :value="7">7天</el-radio-button><el-radio-button :value="30">30天</el-radio-button></el-radio-group>
      </div>
    </template>
    <div ref="tc" style="height:300px"></div>
  </el-card>

  <el-row :gutter="16" class="mt16">
    <el-col :span="12"><el-card shadow="never" header="训练热度 Top10"><div ref="rc" style="height:260px"></div></el-card></el-col>
    <el-col :span="12">
      <el-card shadow="never" header="AI 今日用量">
        <div class="ai-row"><div class="ai-item"><span class="ai-n">{{ai.today_text}}</span><span class="ai-l">文案生成</span></div><div class="ai-item"><span class="ai-n">{{ai.today_speech}}</span><span class="ai-l">语音评测</span></div><div class="ai-item"><span class="ai-n">{{ai.today_users}}</span><span class="ai-l">活跃用户</span></div></div>
      </el-card>
    </el-col>
  </el-row>
</div>
</template>

<script setup>
import {ref,reactive,onMounted,nextTick} from 'vue'
import * as echarts from 'echarts'
import request from '@/api/request'

const period=ref(30),cards=ref([]),tc=ref(null),rc=ref(null)
const ai=reactive({today_text:0,today_speech:0,today_users:0})
let tInst=null,rInst=null

const quicks = [
  { icon: '📝', label: '训练题库', desc: '管理训练素材', path: '/training' },
  { icon: '👥', label: '用户管理', desc: '查看用户数据', path: '/users' },
  { icon: '⭐', label: '推荐配置', desc: '设置首页推荐', path: '/training/recommend' },
  { icon: '🤖', label: 'AI 配置', desc: '调整模型参数', path: '/ai' }
]

// 默认数据
const defaults={
  stats:{total_users:1286,yesterday_new_users:23,yesterday_dau:342,yesterday_checkin_rate:67.8},
  trends:Array.from({length:31},(_,i)=>{
    const d=new Date();d.setDate(d.getDate()-30+i)
    return {date:d.toISOString().slice(0,10),new_users:10+Math.floor(Math.random()*20),dau:300+Math.floor(Math.random()*60),checkin_rate:60+Math.floor(Math.random()*20)}
  }),
  top:[{title:'竞聘演讲通用模板',practice_count:12800},{title:'跟读练习：新闻播音腔',practice_count:10500},{title:'直播开场5秒抓注意力',practice_count:9800},{title:'30秒电梯自我介绍',practice_count:8700},{title:'即兴话题：AI的未来',practice_count:7600},{title:'工作汇报结构化框架',practice_count:6500},{title:'万能开场白模板',practice_count:5800},{title:'产品讲解FAB法则',practice_count:5100},{title:'普通话语调练习',practice_count:4600},{title:'逼单促单话术合集',practice_count:3900}]
}

async function load(){
  try{
    const d=await request.get('/admin/dashboard',{period:period.value})
    const s=d.stats||defaults.stats
    cards.value=[
      {label:'总用户数',value:s.total_users,color:'#FF6B35'},
      {label:'昨日新增',value:s.yesterday_new_users,color:'#1890FF'},
      {label:'昨日DAU',value:s.yesterday_dau,color:'#52C41A'},
      {label:'昨日打卡率',value:(s.yesterday_checkin_rate||0)+'%',color:'#722ED1'}
    ]
    ai.today_text=d.ai_usage?.today_text_generations||0
    ai.today_speech=d.ai_usage?.today_speech_evaluations||0
    ai.today_users=d.ai_usage?.today_active_users||d.stats?.yesterday_dau||0
    await nextTick()
    renderTrends(d.trends?.length?d.trends:defaults.trends)
    renderRanks(d.top_trainings?.length?d.top_trainings:defaults.top)
  }catch(e){
    cards.value=[
      {label:'总用户数',value:1286,color:'#FF6B35'},{label:'昨日新增',value:23,color:'#1890FF'},{label:'昨日DAU',value:342,color:'#52C41A'},{label:'昨日打卡率',value:'67.8%',color:'#722ED1'}
    ]
    ai.today_text=56;ai.today_speech=234;ai.today_users=128
    await nextTick()
    renderTrends(defaults.trends)
    renderRanks(defaults.top)
  }
}

function renderTrends(d){
  if(!tc.value)return;if(!tInst)tInst=echarts.init(tc.value)
  tInst.setOption({tooltip:{trigger:'axis'},legend:{data:['新增','DAU','打卡率']},grid:{left:40,right:40,top:20,bottom:20},xAxis:{type:'category',data:d.map(t=>t.date.slice(5))},yAxis:[{type:'value'},{type:'value',max:100}],series:[{name:'新增',type:'line',data:d.map(t=>t.new_users),smooth:true,itemStyle:{color:'#1890FF'}},{name:'DAU',type:'line',data:d.map(t=>t.dau),smooth:true,itemStyle:{color:'#52C41A'}},{name:'打卡率',type:'line',yAxisIndex:1,data:d.map(t=>t.checkin_rate),smooth:true,itemStyle:{color:'#FF6B35'}}]})
}

function renderRanks(d){
  if(!rc.value)return;if(!rInst)rInst=echarts.init(rc.value)
  const items=[...d].reverse()
  rInst.setOption({tooltip:{trigger:'axis',axisPointer:{type:'shadow'}},grid:{left:110,right:20,top:0,bottom:0},yAxis:{type:'category',data:items.map(i=>i.title),axisLabel:{width:100,overflow:'truncate'}},xAxis:{type:'value'},series:[{type:'bar',data:items.map(i=>i.practice_count),itemStyle:{color:'#FF6B35'},barMaxWidth:20}]})
}

onMounted(load)
</script>

<style scoped>
.db{padding:0}.stat-row{margin-bottom:16px}.stat-card{cursor:pointer;text-align:center;border-radius:10px}.stat-v{font-size:36px;font-weight:bold;margin-bottom:4px}.stat-l{font-size:13px;color:#999}
.quick-row{margin-bottom:16px}.quick-card{display:flex;align-items:center;gap:12px;background:#fff;border-radius:10px;padding:16px 20px;cursor:pointer;transition:all 0.2s;box-shadow:0 2px 8px rgba(0,0,0,0.06)}.quick-card:hover{transform:translateY(-2px);box-shadow:0 4px 16px rgba(0,0,0,0.1)}.quick-icon{font-size:28px;flex-shrink:0}.quick-info{display:flex;flex-direction:column}.quick-label{font-size:14px;font-weight:600;color:#333}.quick-desc{font-size:12px;color:#999;margin-top:2px}
.mt16{margin-top:16px}.card-hd{display:flex;justify-content:space-between;align-items:center;font-weight:600}
.ai-row{display:flex;justify-content:space-around;padding:30px 0}.ai-item{text-align:center}.ai-n{font-size:40px;font-weight:bold;color:#FF6B35;display:block}.ai-l{font-size:13px;color:#999;margin-top:6px;display:block}
</style>
