<template>
<view class="page">
  <view class="qb">今日剩余 <text class="qn">{{quota}}</text> 次</view>

  <view class="sg">
    <view class="sc" v-for="s in scenes" :key="s.value" :class="{on:form.scene_type===s.value}" @click="form.scene_type=s.value">
      <text class="sci">{{s.icon}}</text><text class="scl">{{s.label}}</text>
    </view>
  </view>

  <view class="card">
    <view class="fi"><text class="fl">主题 *</text><input class="finp" v-model="form.topic" placeholder="例：如何做好时间管理" placeholder-style="font-size:26rpx;color:#999" maxlength="50"/></view>
    <view class="fi"><text class="fl">场景</text><input class="finp" v-model="form.scene_desc" placeholder="例：部门周会3分钟分享" placeholder-style="font-size:26rpx;color:#999" maxlength="50"/></view>
    <view class="fr">
      <view class="fi h"><text class="fl">时长</text><picker :range="durs" @change="form.duration=durs[$event.detail.value]"><text class="fp">{{form.duration||'选择'}}</text></picker></view>
      <view class="fi h"><text class="fl">风格</text><picker :range="sty" @change="form.style=sty[$event.detail.value]"><text class="fp">{{form.style||'选择'}}</text></picker></view>
    </view>
    <button class="gbn" @click="generate" :loading="gen">✨ AI生成文案</button>
  </view>

  <view v-if="result" class="card rc">
    <text class="rtit ellipsis">{{result.title}}</text>
    <view class="rct"><text>{{result.content}}</text></view>
    <view class="rbtns"><button size="mini" @click="cp">📋 复制</button><button size="mini" @click="im">🔊 导入练习</button></view>
  </view>
</view>
</template>

<script setup>
import {ref,reactive} from 'vue';import {onShow} from '@dcloudio/uni-app';import api from '@/api/request'
const quota=ref(3),gen=ref(false),result=ref(null)
const scenes=[{icon:'🎤',label:'演讲文案',value:'speech'},{icon:'📱',label:'短视频',value:'short_video'},{icon:'🛒',label:'直播话术',value:'livestream'},{icon:'🌟',label:'开场白',value:'opening'}]
const durs=['1min','3min','5min','10min'];const sty=['专业正式','轻松幽默','情感共鸣','数据驱动']
const form=reactive({scene_type:'speech',topic:'',scene_desc:'',duration:'3min',style:'专业正式'})
async function lq(){try{const d=await api.get('/ai-text/quota');quota.value=d.remaining||3}catch(e){}}
async function generate(){if(!form.topic)return uni.showToast({title:'请输入主题',icon:'none'});if(quota.value<=0)return uni.showToast({title:'今日次数已用完',icon:'none'});gen.value=true;try{result.value=await api.post('/ai-text/generate',{...form});quota.value=result.value.remaining_quota||quota.value-1}catch(e){}finally{gen.value=false}}
function cp(){uni.setClipboardData({data:result.value?.content||'',success:()=>uni.showToast({title:'已复制'})})}
function im(){uni.showToast({title:'已导入练习库',icon:'none'})}
onShow(lq)
</script>

<style scoped>
.qb{text-align:center;font-size:24rpx;color:#666;margin-bottom:16rpx;width:100%}.qn{color:#FF6B35;font-weight:bold}
.sg{display:flex;gap:10rpx;margin-bottom:20rpx;width:100%}
.sc{flex:1;min-width:0;text-align:center;background:#fff;border-radius:16rpx;padding:18rpx 4rpx;box-shadow:0 2rpx 8rpx rgba(0,0,0,.06);box-sizing:border-box;overflow:hidden}
.sc.on{background:#FFF0E8;border:2rpx solid #FF6B35}
.sci{font-size:32rpx;display:block;margin-bottom:4rpx}.scl{font-size:18rpx;color:#666;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;display:block}
.card{background:#fff;border-radius:20rpx;padding:24rpx;margin-bottom:20rpx;width:100%;box-sizing:border-box;overflow:hidden}
.fi{margin-bottom:14rpx;width:100%}.fl{font-size:24rpx;color:#333;display:block;margin-bottom:6rpx}
.finp{background:#f5f5f5;border-radius:10rpx;padding:16rpx 18rpx;font-size:26rpx;height:68rpx;line-height:36rpx;width:100%;box-sizing:border-box}
.fr{display:flex;gap:14rpx;width:100%}.h{flex:1;min-width:0}.fp{background:#f5f5f5;border-radius:10rpx;padding:16rpx 18rpx;font-size:26rpx;height:68rpx;line-height:36rpx;color:#999;width:100%;box-sizing:border-box;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;display:flex;align-items:center}
.gbn{width:100%;height:80rpx;background:linear-gradient(135deg,#FF6B35,#FF8C5A);color:#fff;border-radius:40rpx;border:none;font-size:30rpx;font-weight:bold;margin-top:4rpx;box-sizing:border-box}
.rc{margin-top:20rpx}.rtit{font-size:30rpx;font-weight:bold;display:block}
.rct{background:#fafafa;border-radius:14rpx;padding:20rpx;margin:14rpx 0;font-size:26rpx;line-height:1.7;word-break:break-all;max-height:500rpx;overflow-y:auto;width:100%;box-sizing:border-box}
.rbtns{display:flex;gap:12rpx}
</style>
