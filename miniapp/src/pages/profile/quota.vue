<template>
<view class="page">
  <view class="stc"><text class="sqn">{{quota.remaining}}</text><text class="sql">今日剩余AI生成次数</text></view>
  <view class="card">
    <text class="st2">权益详情</text>
    <view class="ir"><text>每日基础次数</text><text>{{quota.daily_quota}}次</text></view>
    <view class="ir"><text>今日已用</text><text>{{quota.daily_used}}次</text></view>
    <view class="ir"><text>打卡额外奖励</text><text>+{{quota.extra_quota}}次</text></view>
    <view class="ir"><text>当前等级</text><text>{{lv(user.growth_level)}}</text></view>
  </view>
</view>
</template>

<script setup>
import {ref,reactive} from 'vue';import {onShow} from '@dcloudio/uni-app';import api from '@/api/request'
const quota=reactive({remaining:0,daily_quota:3,daily_used:0,extra_quota:0}),user=ref({growth_level:'newbie'})
const lv=v=>({newbie:'新人',beginner:'入门',advanced:'进阶',expert:'达人',master:'大师'}[v]||'新人')
async function load(){try{const d=await api.get('/ai-text/quota');Object.assign(quota,{remaining:d.remaining||0,daily_quota:d.daily_quota||3,daily_used:d.daily_used||0,extra_quota:d.extra_from_checkin||0})}catch(e){};try{user.value=await api.get('/user/profile')}catch(e){}}
onShow(load)
</script>

<style scoped>
.stc{text-align:center;padding:36rpx;margin-bottom:24rpx;width:100%}.sqn{font-size:72rpx;font-weight:bold;color:#FF6B35;display:block}.sql{font-size:24rpx;color:#999;margin-top:6rpx;display:block}
.card{background:#fff;border-radius:20rpx;padding:24rpx;width:100%;box-sizing:border-box;overflow:hidden}
.st2{font-size:30rpx;font-weight:bold;display:block;margin-bottom:14rpx}
.ir{display:flex;justify-content:space-between;padding:16rpx 0;border-bottom:1rpx solid #f5f5f5;font-size:26rpx;width:100%}
</style>
