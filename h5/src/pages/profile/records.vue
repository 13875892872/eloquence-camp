<template>
<view class="page">
  <view v-if="list.length" class="list">
    <view class="item" v-for="r in list" :key="r.id" @tap="toggleExpand(r.id)">
      <view class="ir1">
        <text class="it ellipsis">{{r.training_item?.title||'自由练习'}}</text>
        <text class="sc">{{r.ai_score||'-'}}分</text>
        <text class="arrow">{{expanded[r.id]?'▲':'▼'}}</text>
      </view>
      <view class="ir2">
        <text class="dr">{{r.duration}}s</text>
        <text class="tm">{{r.created_at?.slice(0,16)}}</text>
        <text class="pl" v-if="r.audio_url" @tap.stop="togglePlay(r)">{{playingId===r.id?'⏸ 暂停':'▶ 播放'}}</text>
        <text class="pl makeup" v-if="r.duration>=60" @tap.stop="doMakeup(r)">补签</text>
        <text class="pl nofile" v-else>无录音</text>
      </view>
      <!-- 维度分数展开 -->
      <view class="expand" v-if="expanded[r.id]">
        <view class="dim-row" v-for="(v,k) in r.dimension_scores" :key="k">
          <text class="dim-label">{{dimLabel(k)}}</text>
          <view class="dim-bar-bg"><view class="dim-bar-fg" :style="{width:v+'%'}"></view></view>
          <text class="dim-val">{{v}}</text>
        </view>
        <text class="feedback" v-if="r.ai_feedback">{{r.ai_feedback}}</text>
      </view>
    </view>
  </view>
  <view v-else class="empty">暂无练习记录</view>
</view>
</template>

<script setup>
import {ref,reactive} from 'vue';import {onShow,onUnload} from '@dcloudio/uni-app';import api from '@/api/request'
import { resolveMediaUrl } from '@/utils/media'

const list=ref([]),expanded=reactive({}),playingId=ref(-1),playingStatus=ref('')
let audioCtx=null

const dimLabel=k=>({pronunciation:'发音',fluency:'流利度',completeness:'完整度',content:'内容',expressiveness:'表现力'}[k]||k)

function toggleExpand(id){
  expanded[id]=!expanded[id]
}

function togglePlay(record){
  if(!audioCtx) initAudio()
  if(playingId.value===record.id){
    // 正在播放 → 暂停
    audioCtx.pause()
    playingId.value=-1
    return
  }
  // 停止之前的播放
  if(playingId.value!==-1) audioCtx.stop()
  const fullUrl=resolveMediaUrl(record.audio_url)
  audioCtx.src=fullUrl
  audioCtx.play()
  playingId.value=record.id
}

function initAudio(){
  audioCtx=uni.createInnerAudioContext()
  audioCtx.onEnded(()=>{ playingId.value=-1 })
  audioCtx.onError((err)=>{
    console.error('播放失败',err)
    playingId.value=-1
    uni.showToast({title:'播放失败',icon:'none'})
  })
}

async function load(){try{const d=await api.get('/user/practice-records');list.value=d.items||[]}catch(e){}}

async function doMakeup(r){
  try{
    await api.post('/checkin/makeup',{practice_record_id:r.id})
    uni.showToast({title:'补签成功',icon:'success'})
  }catch(e){
    uni.showToast({title:e?.message||'补签失败',icon:'none'})
  }
}
onShow(load)
onUnload(()=>{if(audioCtx) audioCtx.destroy()})
</script>

<style scoped>
.item{background:var(--bg-card);border-radius:20rpx;padding:24rpx;margin-bottom:14rpx;width:100%;box-sizing:border-box;overflow:hidden}
.ir1{display:flex;align-items:center;gap:10rpx;width:100%}
.it{font-size:28rpx;font-weight:bold;flex:1;min-width:0}.sc{font-size:26rpx;font-weight:bold;color:var(--brand-primary);flex-shrink:0}.arrow{font-size:20rpx;color:#999;flex-shrink:0}
.ir2{display:flex;align-items:center;gap:12rpx;margin-top:10rpx;flex-wrap:wrap;width:100%}
.dr{font-size:22rpx;color:#666}.tm{font-size:20rpx;color:#999;margin-left:auto}.pl{font-size:22rpx;color:var(--brand-primary);padding:4rpx 16rpx;border:1rpx solid var(--brand-primary);border-radius:20rpx}.pl.nofile{color:#ccc;border-color:#ddd}.pl.makeup{color:#FAAD14;border-color:#FAAD14;margin-left:8rpx}
.expand{margin-top:18rpx;padding-top:18rpx;border-top:1rpx solid #f0f0f0}
.dim-row{display:flex;align-items:center;margin:8rpx 0}
.dim-label{width:100rpx;font-size:22rpx;color:#666;flex-shrink:0}
.dim-bar-bg{flex:1;height:8rpx;background:#f0f0f0;border-radius:4rpx;overflow:hidden;min-width:0;margin:0 8rpx}
.dim-bar-fg{height:100%;background:var(--brand-primary);border-radius:4rpx;transition:width .4s}
.dim-val{width:40rpx;text-align:right;font-size:22rpx;font-weight:bold;color:var(--brand-primary);flex-shrink:0}
.feedback{font-size:22rpx;color:#999;background:#fafafa;border-radius:10rpx;padding:14rpx;margin-top:12rpx;line-height:1.6;display:block}
</style>
