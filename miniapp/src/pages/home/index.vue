<template>
<view class="page">
  <view class="hdr"><text class="greet">{{greeting}}</text><text class="streak" v-if="user.continuous_days">🔥 连续{{user.continuous_days}}天</text></view>

  <view class="entry" @click="goCheckin">
    <view class="e-l"><text class="e-t">{{isChecked?'今日已完成 ✓':'待练 '+pendingCount+' 个任务'}}</text><text class="e-s">{{isChecked?'查看记录':'开始今日练习'}}</text></view>
    <text class="e-a">→</text>
  </view>

  <view class="grid4">
    <view class="g4-i" v-for="f in funcs" :key="f.cat" @click="goCat(f.cat)">
      <text class="g4-ico">{{f.icon}}</text><text class="g4-lbl">{{f.label}}</text>
    </view>
  </view>

  <!-- 每日一句 -->
  <view class="card quote-card" v-if="dailyQuote">
    <text class="st">💬 每日一句</text>
    <text class="qd ellipsis-2">{{dailyQuote.content}}</text>
    <text class="qs" v-if="dailyQuote.source">— {{dailyQuote.source}}</text>
  </view>

  <view class="card newbie" v-if="user.growth_level==='newbie'">
    <text class="st">🆕 7天口才入门</text><text class="sd">每天10分钟，告别当众紧张</text>
    <view class="btn-sm" @click="goCat('basic')">开始入门 →</view>
  </view>

  <view class="card"><text class="st">🔥 热门推荐</text>
    <view class="hot-i" v-for="it in hots" :key="it.id" @click="goDetail(it)"><text class="hot-t ellipsis">{{it.title}}</text><text class="hot-a">→</text></view>
  </view>
</view>
</template>

<script setup>
import {ref,computed} from 'vue';import {onShow} from '@dcloudio/uni-app';import api from '@/api/request'
const user=ref({continuous_days:0,growth_level:'newbie'}),pendingCount=ref(3),isChecked=ref(false),hots=ref([]),dailyQuote=ref(null)
const greeting=computed(()=>{const h=new Date().getHours();return h<12?'早上好 ☀️':h<18?'下午好 🌤':'晚上好 🌙'})
const funcs=[{icon:'🎤',label:'基础口才',cat:'basic'},{icon:'🎯',label:'演讲实战',cat:'speech'},{icon:'🎬',label:'直播话术',cat:'livestream'},{icon:'⚡',label:'即兴表达',cat:'improv'}]
async function load(){
  try{
    const d=await api.get('/checkin/today')
    pendingCount.value=d.tasks?.filter(t=>t.status!=='completed').length||3
    isChecked.value=d.all_completed
    Object.assign(user.value,d.stats||{})
    dailyQuote.value=d.daily_quote||null
  }catch(e){}
  try{const r=await api.get('/training/items',{page_size:3});hots.value=r.items||[]}catch(e){}
}
function goCheckin(){uni.switchTab({url:'/pages/checkin/index'})}
function goCat(cat){uni.setStorageSync('training_cat',cat);uni.switchTab({url:'/pages/training/index'})}
function goDetail(it){uni.navigateTo({url:'/pages/training/detail?id='+it.id})}
onShow(load)
</script>

<style scoped>
.hdr{padding:32rpx 0 16rpx;width:100%}.greet{font-size:40rpx;font-weight:bold;display:block}.streak{font-size:24rpx;color:#FF6B35;margin-top:6rpx}
.entry{display:flex;align-items:center;justify-content:space-between;background:linear-gradient(135deg,#FF6B35,#FF8C5A);border-radius:24rpx;padding:32rpx;margin-bottom:24rpx;color:#fff;width:100%;box-sizing:border-box}
.e-t{font-size:34rpx;font-weight:bold;display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:90vw}
.e-s{font-size:24rpx;opacity:.8;display:block}.e-a{font-size:40rpx;flex-shrink:0}
.grid4{display:flex;flex-wrap:wrap;margin-bottom:24rpx;gap:16rpx;width:100%}
.g4-i{width:calc((100vw - 64rpx)/2);background:#fff;border-radius:24rpx;padding:32rpx 8rpx;text-align:center;box-shadow:0 2rpx 12rpx rgba(0,0,0,.06);box-sizing:border-box;overflow:hidden}
.g4-ico{font-size:48rpx;display:block;margin-bottom:8rpx}.g4-lbl{font-size:26rpx;font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;display:block}
.card{background:#fff;border-radius:24rpx;padding:28rpx;margin-bottom:20rpx;width:100%;box-sizing:border-box;overflow:hidden}
.st{font-size:32rpx;font-weight:bold;display:block;margin-bottom:14rpx}
.quote-card{background:#FFF8F5}
.qd{font-size:28rpx;color:#666;line-height:1.8;display:block;margin-top:8rpx}
.qs{font-size:22rpx;color:#999;display:block;margin-top:8rpx;text-align:right}
.newbie{background:#FFF8F5}.sd{font-size:24rpx;color:#666;display:block;margin-bottom:14rpx;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.btn-sm{display:inline-block;background:#FF6B35;color:#fff;border-radius:16rpx;padding:10rpx 28rpx;font-size:24rpx}
.hot-i{display:flex;justify-content:space-between;align-items:center;padding:18rpx 0;border-bottom:1rpx solid #f0f0f0;width:100%}
.hot-t{font-size:28rpx;flex:1;min-width:0}.hot-a{color:#ccc;flex-shrink:0;margin-left:16rpx}
</style>
