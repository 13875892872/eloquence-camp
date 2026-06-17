<template>
<view class="page">
  <view class="tbs"><view class="tb" :class="{on:tab==='training'}" @click="sw('training')">训练题</view><view class="tb" :class="{on:tab==='ai'}" @click="sw('ai')">AI文案</view></view>
  <view v-if="list.length" class="list">
    <view class="item" v-for="f in list" :key="f.id">
      <text class="it ellipsis">{{f.item?.title||'未命名'}}</text>
      <text class="id2">{{f.created_at?.slice(0,10)}}</text>
    </view>
  </view>
  <view v-else class="empty">暂无收藏</view>
</view>
</template>

<script setup>
import {ref} from 'vue';import {onShow} from '@dcloudio/uni-app';import api from '@/api/request'
const tab=ref('training'),list=ref([])
async function load(){try{const d=await api.get('/user/favorites',{item_type:tab.value==='ai'?'ai_text':'training_item'});list.value=d.items||[]}catch(e){}}
function sw(t){tab.value=t;load()}
onShow(load)
</script>

<style scoped>
.tbs{display:flex;margin-bottom:20rpx;gap:12rpx;width:100%}.tb{flex:1;text-align:center;padding:14rpx;font-size:26rpx;background:var(--bg-secondary);border-radius:32rpx}.tb.on{background:#FF6B35;color:#fff}
.item{background:var(--bg-card);border-radius:20rpx;padding:24rpx;margin-bottom:14rpx;width:100%;box-sizing:border-box;overflow:hidden}
.it{font-size:28rpx;font-weight:bold;display:block}.id2{font-size:20rpx;color:#999;display:block;margin-top:6rpx}
</style>
