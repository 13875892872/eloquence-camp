<template>
<view class="page">
  <view v-if="list.length" class="list">
    <view class="item" v-for="r in list" :key="r.id" @click="show(r)">
      <text class="it ellipsis">{{r.title||'未命名'}}</text>
      <view class="im2"><text class="is">{{sl(r.scene_type)}}</text><text class="id">{{r.created_at?.slice(0,16)}}</text></view>
    </view>
  </view>
  <view v-else class="empty">暂无生成记录</view>
</view>
</template>

<script setup>
import {ref} from 'vue';import {onShow} from '@dcloudio/uni-app';import api from '@/api/request'
const list=ref([])
const sl=v=>({speech:'演讲',short_video:'短视频',livestream:'直播',opening:'开场白'}[v]||v)
async function load(){try{const d=await api.get('/ai-text/history');list.value=d.items||[]}catch(e){}}
function show(r){uni.showToast({title:'查看详情: '+r.title,icon:'none'})}
onShow(load)
</script>

<style scoped>
.item{background:#fff;border-radius:20rpx;padding:24rpx;margin-bottom:14rpx;width:100%;box-sizing:border-box;overflow:hidden}
.it{font-size:28rpx;font-weight:bold;display:block}.im2{display:flex;justify-content:space-between;margin-top:10rpx;width:100%}.is{font-size:20rpx;color:#FF6B35}.id{font-size:20rpx;color:#999}
</style>
