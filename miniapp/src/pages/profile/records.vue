<template>
<view class="page">
  <view v-if="list.length" class="list">
    <view class="item" v-for="r in list" :key="r.id">
      <text class="it ellipsis">{{r.training_item?.title||'自由练习'}}</text>
      <view class="im2"><text class="sc">评分:{{r.ai_score||'-'}}</text><text class="dr">{{r.duration}}s</text><text class="tm">{{r.created_at?.slice(0,16)}}</text></view>
    </view>
  </view>
  <view v-else class="empty">暂无练习记录</view>
</view>
</template>

<script setup>
import {ref} from 'vue';import {onShow} from '@dcloudio/uni-app';import api from '@/api/request'
const list=ref([])
async function load(){try{const d=await api.get('/user/practice-records');list.value=d.items||[]}catch(e){}}
onShow(load)
</script>

<style scoped>
.item{background:var(--bg-card);border-radius:20rpx;padding:24rpx;margin-bottom:14rpx;width:100%;box-sizing:border-box;overflow:hidden}
.it{font-size:28rpx;font-weight:bold;display:block}.im2{display:flex;gap:12rpx;margin-top:10rpx;flex-wrap:wrap;width:100%}.sc{font-size:22rpx;color:#FF6B35}.dr{font-size:22rpx;color:#666}.tm{font-size:20rpx;color:#999;margin-left:auto}
</style>
