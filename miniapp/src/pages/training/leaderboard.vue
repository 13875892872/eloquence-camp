<template>
<view class="page">
  <!-- 我的排名 -->
  <view class="my-rank-card" v-if="myRank">
    <text class="mr-label">我的排名</text>
    <text class="mr-rank">#{{myRank}}</text>
    <view class="mr-stats">
      <text>连续{{myData?.continuous_days||0}}天 · 累计{{myData?.total_practice_minutes||0}}分钟</text>
    </view>
  </view>

  <!-- 前三名领奖台 -->
  <view class="podium" v-if="list.length>=3">
    <view class="podium-item" v-for="(item,i) in list.slice(0,3)" :key="item.rank"
      :class="'rank-'+item.rank">
      <text class="p-medal">{{['','🥇','🥈','🥉'][item.rank]}}</text>
      <text class="p-name ellipsis">{{item.nickname}}</text>
      <text class="p-days">{{item.continuous_days}}天</text>
    </view>
  </view>

  <!-- 排行榜 -->
  <view class="rank-list card" v-if="list.length>3">
    <view class="rank-item" v-for="item in list.slice(3)" :key="item.rank"
      :class="{me:myRank===item.rank}">
      <text class="ri-rank">{{item.rank}}</text>
      <text class="ri-name ellipsis">{{item.nickname}}</text>
      <text class="ri-score">{{item.continuous_days}}天 · {{item.total_practice_minutes}}min</text>
    </view>
  </view>

  <view v-if="!list.length" class="empty">暂无排名数据</view>
</view>
</template>

<script setup>
import {ref} from 'vue';import {onLoad} from '@dcloudio/uni-app';import api from '@/api/request'
const list=ref([]),myRank=ref(null),myData=ref(null)
async function load(){
  try{
    const d=await api.get('/user/leaderboard')
    list.value=d.items||[]
    myRank.value=d.my_rank||null
    myData.value=d.my_data||null
  }catch(e){}
}
onLoad(load)
</script>

<style scoped>
.my-rank-card{background:linear-gradient(135deg,#FF6B35,#FF8C5A);border-radius:24rpx;padding:32rpx;text-align:center;color:#fff;margin-bottom:24rpx;width:100%;box-sizing:border-box}
.mr-label{font-size:24rpx;opacity:.8;display:block}
.mr-rank{font-size:64rpx;font-weight:bold;display:block;margin:8rpx 0}
.mr-stats{font-size:24rpx;opacity:.8}
.podium{display:flex;align-items:flex-end;justify-content:center;gap:20rpx;margin-bottom:24rpx;padding:30rpx 0;width:100%}
.podium-item{display:flex;flex-direction:column;align-items:center;background:var(--bg-card);border-radius:20rpx;padding:24rpx 20rpx;box-shadow:0 2rpx 12rpx rgba(0,0,0,.06);flex:1;max-width:200rpx;overflow:hidden}
.podium-item.rank-1{order:2;transform:scale(1.15);border-top:6rpx solid #FFD700}
.podium-item.rank-2{order:1;border-top:6rpx solid #C0C0C0}
.podium-item.rank-3{order:3;border-top:6rpx solid #CD7F32}
.p-medal{font-size:40rpx;display:block}
.p-name{font-size:24rpx;margin:8rpx 0;max-width:100%}
.p-days{font-size:22rpx;color:#FF6B35;font-weight:bold}
.card{background:var(--bg-card);border-radius:24rpx;padding:8rpx 24rpx;width:100%;box-sizing:border-box;overflow:hidden}
.rank-item{display:flex;align-items:center;padding:18rpx 0;border-bottom:1rpx solid var(--border-light);width:100%}
.rank-item.me{background:#FFF8F5;margin:0 -24rpx;padding:18rpx 24rpx}
.ri-rank{width:60rpx;font-size:28rpx;font-weight:bold;color:#999;flex-shrink:0}
.ri-name{font-size:28rpx;flex:1;min-width:0;margin:0 16rpx}
.ri-score{font-size:22rpx;color:#FF6B35;flex-shrink:0}
.empty{padding:120rpx 0;text-align:center;font-size:24rpx;color:#999;display:block}
</style>
