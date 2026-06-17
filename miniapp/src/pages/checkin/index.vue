<template>
<view class="page">
  <view class="stats"><view class="si" v-for="s in statsArr" :key="s.l"><text class="sn">{{s.v}}</text><text class="sl">{{s.l}}</text></view></view>

  <!-- 日历入口 -->
  <view class="calendar-link" @click="goCalendar">
    <text>📅 打卡日历</text><text class="ma">→</text>
  </view>

  <view class="card" v-if="ability"><text class="st">口才能力评分</text>
    <view v-for="(v,k) in ability" :key="k" class="radar"><text class="rl ellipsis">{{dl(k)}}</text><view class="rb"><view class="rf" :style="{width:v+'%'}"></view></view><text class="rv">{{v}}</text></view>
  </view>

  <text class="st2">📋 今日任务</text>
  <view class="task" v-for="t in tasks" :key="t.task_index" :class="{locked:t.status==='locked',done:t.status==='completed'}" @click="startTask(t)">
    <view class="th"><text class="ts">{{t.status==='completed'?'✅':t.status==='locked'?'🔒':'⏳'}}</text><text class="tt ellipsis">{{t.title}}</text></view>
    <text class="tsb ellipsis">{{t.subtitle}} · 最低{{t.min_duration}}s</text>
    <text v-if="t.my_record" class="tsc">评分:{{t.my_record.score}}分</text>
  </view>

  <text class="st2">🎯 成长目标</text>
  <view class="card" v-for="g in goals" :key="g.level">
    <view class="gh"><text class="ellipsis" style="flex:1;min-width:0">{{g.badge}} {{g.name}}</text><text class="gp">{{g.my_days}}/{{g.required_days}}天</text></view>
    <view class="gb"><view class="gf" :style="{width:g.progress+'%'}"></view></view>
    <text v-if="g.achieved" class="gd">✅ 已达成！</text>
  </view>
</view>
</template>

<script setup>
import {ref,computed} from 'vue';import {onShow} from '@dcloudio/uni-app';import api from '@/api/request'
const stats=ref({continuous_days:0,total_days:0,total_minutes:0}),tasks=ref([]),ability=ref(null),goals=ref([])
const dl=k=>({pronunciation:'发音',fluency:'流利度',completeness:'完整度',content:'内容',expressiveness:'表现力'}[k]||k)
const statsArr=computed(()=>[{l:'连续打卡',v:stats.value.continuous_days},{l:'累计天数',v:stats.value.total_days},{l:'总时长(min)',v:stats.value.total_minutes}])
async function load(){try{const d=await api.get('/checkin/today');tasks.value=d.tasks||[];Object.assign(stats.value,d.stats||{})}catch(e){};try{const p=await api.get('/user/profile');ability.value=p.ability_score;Object.assign(stats.value,{continuous_days:p.continuous_days,total_days:p.total_days,total_minutes:p.total_practice_minutes})}catch(e){};try{const g=await api.get('/checkin/growth-progress');goals.value=(g.goals||[]).map(g=>({...g,badge:g.badge?.icon||'🎯',progress:g.achieved?100:g.progress||0}))}catch(e){}}
function startTask(t){if(t.status==='locked')return uni.showToast({title:'请先完成前一个任务',icon:'none'});if(t.status==='completed')return uni.showToast({title:'已完成',icon:'none'});if(t.training_item?.id){uni.navigateTo({url:'/pages/training/detail?id='+t.training_item.id+'&tk='+t.task_index})}else{uni.showToast({title:'请在训练题库中选择题目练习',icon:'none'})}}
function goCalendar(){uni.navigateTo({url:'/pages/checkin/calendar'})}
onShow(()=>{load();requestSubscribe()})

// 请求微信订阅消息授权
async function requestSubscribe(){
  try{
    const u=await api.get('/user/profile')
    if(!u.subscribe_status){
      // 获取可用的模板ID列表
      const tplData=await api.get('/checkin/push-template-ids')
      const tmplIds=tplData.tmpl_ids||[]
      if(tmplIds.length>0){
        await uni.requestSubscribeMessage({tmplIds})
      }
      await api.put('/user/profile/subscribe',{subscribe_status:true})
    }
  }catch(e){}
}
</script>

<style scoped>
.stats{display:flex;background:linear-gradient(135deg,#FF6B35,#FF8C5A);border-radius:24rpx;padding:36rpx 0;margin-bottom:16rpx;width:100%}
.si{flex:1;text-align:center;color:#fff;min-width:0}.sn{font-size:40rpx;font-weight:bold;display:block}.sl{font-size:22rpx;opacity:.8;display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.calendar-link{display:flex;justify-content:space-between;align-items:center;background:#FFF8F5;border-radius:16rpx;padding:18rpx 24rpx;margin-bottom:20rpx;font-size:26rpx;color:#FF6B35;width:100%;box-sizing:border-box}
.ma{color:#FF6B35;flex-shrink:0}
.card{background:var(--bg-card);border-radius:24rpx;padding:24rpx;margin-bottom:16rpx;width:100%;box-sizing:border-box;overflow:hidden}
.st{font-size:30rpx;font-weight:bold;display:block;margin-bottom:14rpx}
.st2{font-size:30rpx;font-weight:bold;display:block;margin:24rpx 0 14rpx}
.radar{display:flex;align-items:center;margin:8rpx 0;width:100%}.rl{width:110rpx;font-size:22rpx;color:#666;flex-shrink:0}.rb{flex:1;height:10rpx;background:#f0f0f0;border-radius:5rpx;overflow:hidden;min-width:0;margin:0 10rpx}.rf{height:100%;background:#FF6B35;border-radius:5rpx;transition:width .5s}.rv{width:50rpx;text-align:right;font-size:22rpx;color:#FF6B35;font-weight:bold;flex-shrink:0}
.task{background:var(--bg-card);border-radius:24rpx;padding:24rpx;margin-bottom:14rpx;width:100%;box-sizing:border-box;overflow:hidden}.task.locked{opacity:.5}.task.done{border-left:6rpx solid #52C41A}
.th{display:flex;align-items:center;gap:10rpx;margin-bottom:6rpx;width:100%}.ts{flex-shrink:0}.tt{font-size:28rpx;font-weight:bold;flex:1;min-width:0}.tsb{font-size:22rpx;color:#999;display:block}.tsc{font-size:22rpx;color:#FF6B35;margin-top:4rpx}
.gh{display:flex;justify-content:space-between;align-items:center;margin-bottom:6rpx;width:100%}.gp{font-size:24rpx;color:#FF6B35;flex-shrink:0;margin-left:16rpx}.gb{height:10rpx;background:#f0f0f0;border-radius:5rpx;overflow:hidden;margin:10rpx 0;width:100%}.gf{height:100%;background:#52C41A;border-radius:5rpx}.gd{font-size:22rpx;color:#52C41A;display:block}
</style>
