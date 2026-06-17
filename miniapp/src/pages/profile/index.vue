<template>
<view class="page">
  <view class="uc">
    <image class="av" :src="user.avatar_url||''" mode="aspectFill"/>
    <text class="un ellipsis">{{user.nickname||'微信用户'}}</text>
    <text class="ul">{{lv(user.growth_level)}}</text>
    <view class="us">
      <view class="usi"><text class="usn">{{user.total_days||0}}</text><text class="usl">累计打卡</text></view>
      <view class="usi"><text class="usn">{{user.continuous_days||0}}</text><text class="usl">连续打卡</text></view>
      <view class="usi"><text class="usn">{{user.total_practice_minutes||0}}</text><text class="usl">练习分钟</text></view>
    </view>
  </view>

  <view class="mc">
    <view class="mi" @click="nav('records')"><text>🎤 录音记录</text><text class="ma">→</text></view>
    <view class="mi" @click="nav('favorites')"><text>⭐ 我的收藏</text><text class="ma">→</text></view>
    <view class="mi" @click="nav('quota')"><text>🎁 权益中心</text><text class="ma">→</text></view>
  </view>

  <view class="mc mt">
    <view class="mi"><text>🌙 深色模式</text><switch :checked="isDark" @change="onDarkChange" color="#FF6B35" style="flex-shrink:0"/></view>
    <view class="mi"><text>🔔 消息提醒</text><switch :checked="remind" @change="onRemindChange" color="#FF6B35" style="flex-shrink:0"/></view>
    <view class="mi" @click="cc"><text>🗑 清除缓存</text><text class="ma">→</text></view>
    <view class="mi"><text>ℹ️ 关于我们</text><text class="ma">→</text></view>
  </view>
</view>
</template>

<script setup>
import {ref} from 'vue';import {onShow} from '@dcloudio/uni-app';import api from '@/api/request'
const user=ref({}),remind=ref(true),isDark=ref(false)
const lv=v=>({newbie:'新人',beginner:'入门',advanced:'进阶',expert:'达人',master:'大师'}[v]||'新人')
const nav=p=>uni.navigateTo({url:'/pages/profile/'+p})
async function load(){
  try{const d=await api.get('/user/profile');user.value=d;remind.value=!!d.subscribe_status}catch(e){}
}
async function onRemindChange(e){
  const val=e.detail.value
  if(val){
    // 请求微信订阅授权 — 使用真实模板ID
    try{
      const tplData=await api.get('/checkin/push-template-ids')
      const tmplIds=tplData.tmpl_ids||[]
      if(tmplIds.length>0){
        await uni.requestSubscribeMessage({tmplIds})
      }
    }catch(e){}
  }
  remind.value=val
  try{await api.put('/user/profile/subscribe',{subscribe_status:val})}catch(e){
    remind.value=!val;uni.showToast({title:'设置失败',icon:'none'})
  }
}
async function onDarkChange(e){const val=e.detail.value;isDark.value=val;uni.setStorageSync('dark_mode',val);uni.showToast({title:val?'深色模式已开启':'深色模式已关闭',icon:'none'})}
function cc(){uni.showToast({title:'缓存已清除',icon:'success'})}
onShow(()=>{load();isDark.value=!!uni.getStorageSync('dark_mode')})
</script>

<style scoped>
.uc{background:linear-gradient(135deg,#FF6B35,#FF8C5A);border-radius:24rpx;padding:36rpx 24rpx;text-align:center;color:#fff;margin-bottom:24rpx;width:100%;box-sizing:border-box;overflow:hidden}
.av{width:90rpx;height:90rpx;border-radius:50%;border:3rpx solid rgba(255,255,255,.4);background:#eee}
.un{font-size:34rpx;font-weight:bold;display:block;margin-top:8rpx;max-width:80vw;margin-left:auto;margin-right:auto}
.ul{font-size:22rpx;opacity:.8;display:block}
.us{display:flex;margin-top:20rpx;width:100%}.usi{flex:1;min-width:0}.usn{font-size:32rpx;font-weight:bold;display:block}.usl{font-size:20rpx;opacity:.8;display:block}
.mc{background:var(--bg-card);border-radius:24rpx;overflow:hidden;width:100%;box-sizing:border-box}.mt{margin-top:20rpx}
.mi{display:flex;justify-content:space-between;align-items:center;padding:24rpx;border-bottom:1rpx solid var(--border-light);font-size:28rpx;width:100%;box-sizing:border-box}.ma{color:#ccc;flex-shrink:0}
</style>
