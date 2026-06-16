<template>
<view class="page">
  <view v-if="!item" class="loading">加载中...</view>
  <template v-else>
    <view class="dc">
      <text class="dt ellipsis">{{item.title}}</text>
      <text class="dm ellipsis">{{cl(item.category)}} · {{'⭐'.repeat(item.difficulty)}} · {{item.practice_count||0}}人练过</text>
      <view class="dtx"><text>{{item.sample_text}}</text></view>
      <view class="ab" @click="playSample"><text>{{playing?'⏸ 暂停范本':'▶ 播放范本'}}</text></view>
    </view>
    <view class="rc">
      <text class="rh" v-if="!recording&&!result">点击按钮开始录音练习</text>
      <view v-if="recording" class="rs"><view class="wv"><view class="wvb" v-for="i in 6" :key="i" :style="{height:Math.random()*50+20+'rpx'}"></view></view><text class="rt">{{timer}}s</text></view>
      <view v-if="result" class="ra">
        <text class="rsc">综合评分 {{result.ai_score}}分</text>
        <view class="rd"><view v-for="(v,k) in result.dimension_scores" :key="k" class="rdl"><text class="rdn">{{dl(k)}}</text><view class="rdb"><view class="rdf" :style="{width:v+'%'}"></view></view><text class="rdv">{{v}}</text></view></view>
        <text class="rfb">{{result.ai_feedback}}</text>
      </view>
      <button class="rbtn" :class="{on:recording}" @click="toggleRecord">{{recording?'⏹ 停止':'🎤 录音'}}</button>
    </view>
  </template>
</view>
</template>

<script setup>
import {ref} from 'vue';import {onLoad} from '@dcloudio/uni-app';import api from '@/api/request'
const item=ref(null),playing=ref(false),recording=ref(false),timer=ref(0),result=ref(null);let ti=null
const cl=v=>({basic:'基础口才',speech:'演讲实战',livestream:'直播话术',improv:'即兴表达'}[v]||v)
const dl=k=>({pronunciation:'发音',fluency:'流利度',completeness:'完整度',content:'内容',expressiveness:'表现力'}[k]||k)
onLoad(async opt=>{if(opt?.id)try{item.value=await api.get('/training/items/'+opt.id)}catch(e){}})
function playSample(){playing.value=!playing.value;uni.showToast({title:playing.value?'播放中':'已暂停',icon:'none'})}
function toggleRecord(){if(recording.value){if(ti)clearInterval(ti);recording.value=false;result.value={ai_score:82,dimension_scores:{pronunciation:85,fluency:78,completeness:90,content:80,expressiveness:70},ai_feedback:'整体表现不错！发音清晰，内容完整。建议在关键句前适当停顿增强表达效果。'}}else{recording.value=true;result.value=null;timer.value=0;ti=setInterval(()=>timer.value++,1000)}}
</script>

<style scoped>
.dc{background:#fff;border-radius:20rpx;padding:24rpx;margin-bottom:20rpx;width:100%;box-sizing:border-box;overflow:hidden}
.dt{font-size:34rpx;font-weight:bold;display:block}.dm{font-size:22rpx;color:#999;display:block;margin:8rpx 0}
.dtx{background:#fafafa;border-radius:16rpx;padding:20rpx;margin-top:14rpx;font-size:26rpx;line-height:1.7;word-break:break-all;max-height:400rpx;overflow-y:auto;width:100%;box-sizing:border-box}
.ab{background:#FFF0E8;border-radius:14rpx;padding:16rpx;text-align:center;margin-top:14rpx;color:#FF6B35;font-size:26rpx;width:100%;box-sizing:border-box}
.rc{text-align:center;padding:30rpx 0}.rh{font-size:26rpx;color:#999}
.rs{padding:30rpx 0}.wv{display:flex;justify-content:center;gap:6rpx;margin-bottom:14rpx}.wvb{width:5rpx;background:#FF6B35;border-radius:3rpx;transition:height .2s}
.rt{font-size:44rpx;font-weight:bold;color:#FF6B35}
.ra{background:#fff;border-radius:20rpx;padding:24rpx;margin-bottom:20rpx;width:100%;box-sizing:border-box;overflow:hidden}
.rsc{font-size:36rpx;font-weight:bold;color:#FF6B35;text-align:center;display:block}
.rd{margin:20rpx 0}.rdl{display:flex;align-items:center;margin:6rpx 0}.rdn{width:100rpx;font-size:22rpx;color:#666;flex-shrink:0}.rdb{flex:1;height:8rpx;background:#f0f0f0;border-radius:4rpx;overflow:hidden;min-width:0;margin:0 8rpx}.rdf{height:100%;background:#FF6B35;border-radius:4rpx}.rdv{width:45rpx;text-align:right;font-size:22rpx;font-weight:bold;color:#FF6B35;flex-shrink:0}
.rfb{font-size:24rpx;color:#666;background:#fafafa;border-radius:14rpx;padding:20rpx;margin-top:14rpx;line-height:1.7;word-break:break-all;display:block;width:100%;box-sizing:border-box}
.rbtn{width:220rpx;height:220rpx;border-radius:50%;background:#FF6B35;color:#fff;font-size:30rpx;font-weight:bold;border:none;display:flex;align-items:center;justify-content:center;margin:20rpx auto;flex-shrink:0}.rbtn.on{background:#FF4D4F;animation:pulse 1s infinite}@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.08)}}
</style>
