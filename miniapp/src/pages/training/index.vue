<template>
<view class="page">
  <view class="sb"><input class="si" v-model="keyword" placeholder="搜索训练内容..." placeholder-style="font-size:28rpx;color:#999" @confirm="search" maxlength="50"/></view>
  <view class="leader-link" @click="goLeaderboard"><text>🏆 训练排行榜</text><text class="ma">→</text></view>
  <scroll-view scroll-x class="tabs" :show-scrollbar="false"><view class="tab" v-for="t in tabs" :key="t.value" :class="{active:cat===t.value}" @click="switchCat(t.value)">{{t.label}}</view></scroll-view>
  <view v-if="list.length" class="list">
    <view class="item" v-for="it in list" :key="it.id" @click="goDetail(it)">
      <view class="it"><text class="it-title ellipsis">{{it.title}}</text><text class="it-diff">{{'⭐'.repeat(it.difficulty)}}</text></view>
      <view class="im"><text class="im-cat">{{cl(it.category)}}</text><text class="im-count">{{it.practice_count||0}}人练过</text></view>
      <view class="ifoot"><text class="im-time" v-if="it.created_at">{{fmtDate(it.created_at)}}</text><text class="ia-btn">开始练习 →</text></view>
    </view>
  </view>
  <view v-else class="empty">暂无训练内容</view>
  <view class="load-more" v-if="hasMore" @click="loadMore">加载更多</view>
  <view class="load-more dim" v-if="list.length&&!hasMore">— 已全部加载 —</view>
</view>
</template>

<script setup>
import {ref} from 'vue';import {onLoad} from '@dcloudio/uni-app';import api from '@/api/request'
const cat=ref(''),keyword=ref(''),list=ref([]),page=ref(1),hasMore=ref(true)
const PAGE_SIZE=10
const tabs=[{label:'全部',value:''},{label:'基础口才',value:'basic'},{label:'演讲实战',value:'speech'},{label:'直播话术',value:'livestream'},{label:'即兴表达',value:'improv'}]
const cl=v=>({basic:'基础口才',speech:'演讲实战',livestream:'直播话术',improv:'即兴表达'}[v]||v)
function fmtDate(s){if(!s)return '';const d=s.split('T')[0];return d.replace(/-/g,'/')}

async function load(reset=true){
  if(reset){page.value=1;list.value=[];hasMore.value=true}
  try{
    const d=await api.get('/training/items',{category:cat.value||undefined,keyword:keyword.value||undefined,page:page.value,page_size:PAGE_SIZE})
    const items=d.items||[]
    if(reset)list.value=items
    else list.value=[...list.value,...items]
    hasMore.value=items.length>=PAGE_SIZE
  }catch(e){}
}

function search(){load()}
function switchCat(v){cat.value=v;load()}
function loadMore(){page.value++;load(false)}
function goLeaderboard(){uni.navigateTo({url:'/pages/training/leaderboard'})}
function goDetail(it){uni.navigateTo({url:'/pages/training/detail?id='+it.id})}
onLoad(()=>{const c=uni.getStorageSync('training_cat');if(c){cat.value=c;uni.removeStorageSync('training_cat')};load()})
</script>

<style scoped>
.sb{padding:12rpx 0 20rpx;width:100%}.si{background:var(--bg-card);border-radius:40rpx;padding:18rpx 28rpx;font-size:28rpx;height:76rpx;line-height:40rpx;box-shadow:0 2rpx 8rpx rgba(0,0,0,.06);width:100%;box-sizing:border-box}
.tabs{white-space:nowrap;padding-bottom:16rpx;width:100%}.tab{display:inline-flex;align-items:center;padding:8rpx 24rpx;font-size:24rpx;color:#666;background:var(--bg-secondary);border-radius:32rpx;margin-right:10rpx;flex-shrink:0}.tab.active{background:#FF6B35;color:#fff}
.item{background:var(--bg-card);border-radius:20rpx;padding:24rpx;margin-bottom:14rpx;width:100%;box-sizing:border-box;overflow:hidden}
.it{display:flex;justify-content:space-between;align-items:center;width:100%}.it-title{font-size:28rpx;font-weight:bold;flex:1;min-width:0;margin-right:10rpx}.it-diff{font-size:20rpx;flex-shrink:0}
.im{display:flex;gap:12rpx;margin-top:10rpx}.im-cat{font-size:20rpx;color:#FF6B35;background:var(--bg-orange-light);padding:2rpx 14rpx;border-radius:6rpx}.im-count{font-size:20rpx;color:var(--text-hint)}
.ifoot{display:flex;justify-content:space-between;align-items:center;margin-top:14rpx}
.im-time{font-size:20rpx;color:var(--text-hint)}
.ia-btn{color:#FF6B35;font-size:24rpx;font-weight:500}
.load-more{text-align:center;padding:24rpx 0;font-size:26rpx;color:#FF6B35}.load-more.dim{color:var(--text-hint)}
</style>
