<template>
<view class="page">
  <view v-if="!item" class="loading">加载中...</view>
  <template v-else>
    <view class="dc">
      <view class="dc-header">
        <text class="dt ellipsis">{{item.title}}</text>
        <text class="fav-icon" :class="{faved:isFavorited}" @tap.stop="toggleFav">{{isFavorited ? '⭐' : '☆'}}</text>
      </view>
      <text class="dm ellipsis">{{cl(item.category)}} · {{'⭐'.repeat(item.difficulty)}} · {{item.practice_count||0}}人练过</text>
      <view class="dtx"><text>{{item.sample_text}}</text></view>
      <view class="ab" @tap="playSample">
        <text>{{sampleStatus}}</text>
      </view>
    </view>

    <view class="rc">
      <!-- 初始状态 -->
      <text class="rh" v-if="!recording&&!uploading&&!result">点击按钮开始录音练习</text>

      <!-- 录音中 -->
      <view v-if="recording" class="rs">
        <view class="wv">
          <view class="wvb" v-for="i in 6" :key="i" :style="{height:waveHeights[i-1]+'rpx'}"></view>
        </view>
        <text class="rt">{{formatTime(timer)}}</text>
      </view>

      <!-- 上传中 -->
      <view v-if="uploading" class="rs">
        <text class="rt" style="font-size:28rpx">上传中 {{uploadProgress}}%</text>
        <view class="up-bar"><view class="up-fill" :style="{width:uploadProgress+'%'}"></view></view>
      </view>

      <!-- 评测结果 -->
      <view v-if="result" class="ra">
        <text class="rsc">综合评分 {{result.ai_score}}分</text>
        <view class="rd">
          <view v-for="(v,k) in result.dimension_scores" :key="k" class="rdl">
            <text class="rdn">{{dl(k)}}</text>
            <view class="rdb"><view class="rdf" :style="{width:v+'%'}"></view></view>
            <text class="rdv">{{v}}</text>
          </view>
        </view>
        <text class="rfb">{{result.ai_feedback}}</text>
      </view>

      <!-- 录音按钮 -->
      <button class="rbtn" :class="{on:recording||uploading}" @tap="toggleRecord" :disabled="uploading">
        {{recording?'⏹ 停止':'🎤 录音'}}
      </button>
      <text class="rtip" v-if="!recording&&!result">最长5分钟</text>
    </view>
  </template>
</view>
</template>

<script setup>
import {ref,reactive} from 'vue';import {onLoad,onUnload} from '@dcloudio/uni-app';import api,{BASE_API} from '@/api/request'

const item=ref(null),playing=ref(false),recording=ref(false),uploading=ref(false),timer=ref(0),result=ref(null),uploadProgress=ref(0)
const waveHeights=reactive([20,30,40,50,40,30]),isFavorited=ref(false)
let ti=null,wi=null,recorderManager=null,audioContext=null

const cl=v=>({basic:'基础口才',speech:'演讲实战',livestream:'直播话术',improv:'即兴表达'}[v]||v)
const dl=k=>({pronunciation:'发音',fluency:'流利度',completeness:'完整度',content:'内容',expressiveness:'表现力'}[k]||k)
const formatTime=s=>{const m=Math.floor(s/60),sec=s%60;return m+':'+(sec<10?'0':'')+sec}

const sampleStatus=ref('▶ 播放范本')

// ========== 收藏功能 ==========
async function checkFav(){
  if(!item.value?.id) return
  try{
    const d=await api.get('/user/favorites',{item_type:'training_item'})
    isFavorited.value=(d.items||[]).some(f=>f.item_id===item.value.id)
  }catch(e){}
}

async function toggleFav(){
  if(!item.value?.id) return
  try{
    const d=await api.post('/user/favorites/toggle',{item_type:'training_item',item_id:item.value.id})
    isFavorited.value=d.is_favorited
    uni.showToast({title:d.message,icon:'none'})
  }catch(e){uni.showToast({title:'操作失败',icon:'none'})}
}

// ========== 录音管理 ==========
function initRecorder(){
  recorderManager=uni.getRecorderManager()
  recorderManager.onStart(()=>{
    console.log('录音开始')
  })
  recorderManager.onStop(async (res)=>{
    console.log('录音结束',res.tempFilePath)
    if(ti)clearInterval(ti)
    recording.value=false
    // 上传录音
    await uploadAudio(res.tempFilePath,res.duration)
  })
  recorderManager.onError((err)=>{
    console.error('录音错误',err)
    recording.value=false
    if(ti)clearInterval(ti)
    uni.showToast({title:'录音失败，请重试',icon:'none'})
  })
  // 监听录音音量 (用于波形动画)
  recorderManager.onFrameRecorded((res)=>{
    if(res.frameBuffer){
      // 更新波形高度
      const avg=Math.abs(new Int8Array(res.frameBuffer).reduce((a,b)=>a+b,0))/res.frameBuffer.byteLength
      for(let i=0;i<6;i++){
        waveHeights[i]=Math.max(15,Math.min(80,avg*3+Math.random()*20))
      }
    }
  })
}

// ========== 音频播放 ==========
function initAudio(){
  audioContext=uni.createInnerAudioContext()
  audioContext.onEnded(()=>{
    playing.value=false
    sampleStatus.value='▶ 播放范本'
  })
  audioContext.onError((err)=>{
    console.error('播放错误',err)
    playing.value=false
    sampleStatus.value='▶ 播放范本'
    uni.showToast({title:'播放失败',icon:'none'})
  })
}

// ========== 播放范本 ==========
async function playSample(){
  if(playing.value){
    // 暂停
    audioContext.pause()
    playing.value=false
    sampleStatus.value='▶ 播放范本'
    return
  }

  // 如果已有样本音频URL，直接播放
  if(item.value?.sample_audio_url){
    const fullUrl=item.value.sample_audio_url.startsWith('http')?item.value.sample_audio_url:(BASE_API.replace('/api','')+item.value.sample_audio_url)
    audioContext.src=fullUrl
    audioContext.play()
    playing.value=true
    sampleStatus.value='⏸ 暂停范本'
    return
  }

  // 否则调用 TTS 生成音频
  if(item.value?.sample_text){
    sampleStatus.value='🔊 生成中...'
    uni.showLoading({title:'生成范本...'})
    try{
      const data=await api.post('/ai-speech/tts',{text:item.value.sample_text.substring(0,200)})
      uni.hideLoading()
      if(data.audio_url){
        const fullUrl=data.audio_url.startsWith('http')?data.audio_url:(BASE_API.replace('/api','')+data.audio_url)
        audioContext.src=fullUrl
        audioContext.play()
        playing.value=true
        sampleStatus.value='⏸ 暂停范本'
      }else{
        sampleStatus.value='▶ 播放范本'
        uni.showToast({title:'范本生成失败',icon:'none'})
      }
    }catch(e){
      uni.hideLoading()
      sampleStatus.value='▶ 播放范本'
      uni.showToast({title:'TTS服务未配置API Key',icon:'none'})
    }
  }else{
    uni.showToast({title:'暂无范本内容',icon:'none'})
  }
}

// ========== 上传音频 ==========
function uploadAudio(filePath,duration){
  return new Promise((resolve,reject)=>{
    uploading.value=true
    uploadProgress.value=0
    result.value=null

    const token=uni.getStorageSync('token')||''
    const uploadTask=uni.uploadFile({
      url:BASE_API+'/upload/audio',
      filePath:filePath,
      name:'file',
      header:{'Authorization':token?`Bearer ${token}`:''},
      success:async (res)=>{
        try{
          const data=JSON.parse(res.data)
          if(data.code===200&&data.data.audio_url){
            const audioUrl=data.data.audio_url
            // 调用评测
            await evaluateAudio(audioUrl,duration)
            resolve()
          }else{
            uni.showToast({title:data.message||'上传失败',icon:'none'})
            reject(new Error('upload failed'))
          }
        }catch(e){
          uni.showToast({title:'上传解析失败',icon:'none'})
          reject(e)
        }
      },
      fail:(err)=>{
        console.error('上传失败',err)
        uni.showToast({title:'上传失败，请检查网络',icon:'none'})
        reject(err)
      },
      complete:()=>{
        uploading.value=false
        uploadProgress.value=0
      }
    })

    // 监听上传进度
    uploadTask.onProgressUpdate((res)=>{
      uploadProgress.value=res.progress
    })
  })
}

// ========== 语音评测 ==========
async function evaluateAudio(audioUrl,duration){
  try{
    const data=await api.post('/ai-speech/evaluate',{
      audio_url:audioUrl,
      reference_text:item.value?.sample_text||'',
      duration:Math.round(duration||timer.value),
      training_item_id:item.value?.id
    })
    result.value={
      ai_score:data.ai_score,
      dimension_scores:data.dimension_scores,
      ai_feedback:data.ai_feedback
    }
    uni.showToast({title:`评分 ${data.ai_score} 分`,icon:'success'})
  }catch(e){
    console.error('评测失败',e)
    // 即使评测失败也给出基础结果
    result.value={
      ai_score:70,
      dimension_scores:{pronunciation:70,fluency:70,completeness:70,content:70,expressiveness:70},
      ai_feedback:'评测服务暂不可用，请稍后重试'
    }
  }
}

// ========== 录音控制 ==========
function toggleRecord(){
  if(recording.value){
    // 停止录音
    recorderManager.stop()
    if(wi)clearInterval(wi)
  }else{
    // 检查录音权限
    uni.authorize({
      scope:'scope.record',
      success:()=>startRecord(),
      fail:()=>{
        uni.showModal({
          title:'需要录音权限',
          content:'请在设置中开启麦克风权限',
          success:(res)=>{
            if(res.confirm){
              uni.openSetting()
            }
          }
        })
      }
    })
  }
}

function startRecord(){
  recording.value=true
  result.value=null
  timer.value=0
  // 启动计时器
  ti=setInterval(()=>{
    timer.value++
    if(timer.value>=300){// 5分钟上限
      recorderManager.stop()
      if(ti)clearInterval(ti)
    }
  },1000)
  // 启动波形动画
  wi=setInterval(()=>{
    for(let i=0;i<6;i++){
      waveHeights[i]=Math.max(15,Math.min(80,waveHeights[i]+(Math.random()-0.5)*30))
    }
  },200)
  // 开始录音
  recorderManager.start({duration:300000,sampleRate:16000,numberOfChannels:1,encodeBitRate:48000,format:'mp3'})
}

// ========== 生命周期 ==========
onLoad(async opt=>{
  initRecorder()
  initAudio()
  if(opt?.id){
    try{item.value=await api.get('/training/items/'+opt.id)}catch(e){}
    checkFav()
  }
})

onUnload(()=>{
  // 清理资源
  if(ti)clearInterval(ti)
  if(wi)clearInterval(wi)
  if(recorderManager){
    try{recorderManager.stop()}catch(e){}
  }
  if(audioContext){
    audioContext.destroy()
  }
})
</script>

<style scoped>
.dc{background:var(--bg-card);border-radius:20rpx;padding:24rpx;margin-bottom:20rpx;width:100%;box-sizing:border-box;overflow:hidden}
.dc-header{display:flex;justify-content:space-between;align-items:flex-start;width:100%}
.dt{font-size:34rpx;font-weight:bold;display:block;flex:1;min-width:0}
.fav-icon{font-size:40rpx;flex-shrink:0;margin-left:16rpx;color:#ccc}
.fav-icon.faved{color:#FAAD14}
.dm{font-size:22rpx;color:#999;display:block;margin:8rpx 0}
.dtx{background:var(--bg-secondary);border-radius:16rpx;padding:20rpx;margin-top:14rpx;font-size:26rpx;line-height:1.7;word-break:break-all;max-height:400rpx;overflow-y:auto;width:100%;box-sizing:border-box}
.ab{background:#FFF0E8;border-radius:14rpx;padding:16rpx;text-align:center;margin-top:14rpx;color:#FF6B35;font-size:26rpx;width:100%;box-sizing:border-box}
.ab:active{background:#FFE4D6}
.rc{text-align:center;padding:30rpx 0}.rh{font-size:26rpx;color:#999}
.rs{padding:30rpx 0}.wv{display:flex;justify-content:center;align-items:flex-end;gap:6rpx;margin-bottom:14rpx;height:90rpx}
.wvb{width:5rpx;background:#FF6B35;border-radius:3rpx;transition:height .15s;min-height:10rpx}
.rt{font-size:44rpx;font-weight:bold;color:#FF6B35}
.rtip{font-size:22rpx;color:#999;display:block;margin-top:10rpx}
.up-bar{width:300rpx;height:8rpx;background:#f0f0f0;border-radius:4rpx;margin:16rpx auto 0;overflow:hidden}
.up-fill{height:100%;background:#FF6B35;border-radius:4rpx;transition:width .3s}
.ra{background:var(--bg-card);border-radius:20rpx;padding:24rpx;margin-bottom:20rpx;width:100%;box-sizing:border-box;overflow:hidden}
.rsc{font-size:36rpx;font-weight:bold;color:#FF6B35;text-align:center;display:block}
.rd{margin:20rpx 0}.rdl{display:flex;align-items:center;margin:6rpx 0}.rdn{width:100rpx;font-size:22rpx;color:#666;flex-shrink:0}.rdb{flex:1;height:8rpx;background:#f0f0f0;border-radius:4rpx;overflow:hidden;min-width:0;margin:0 8rpx}.rdf{height:100%;background:#FF6B35;border-radius:4rpx;transition:width .5s}.rdv{width:45rpx;text-align:right;font-size:22rpx;font-weight:bold;color:#FF6B35;flex-shrink:0}
.rfb{font-size:24rpx;color:#666;background:var(--bg-secondary);border-radius:14rpx;padding:20rpx;margin-top:14rpx;line-height:1.7;word-break:break-all;display:block;width:100%;box-sizing:border-box}
.rbtn{width:220rpx;height:220rpx;border-radius:50%;background:#FF6B35;color:#fff;font-size:30rpx;font-weight:bold;border:none;display:flex;align-items:center;justify-content:center;margin:20rpx auto;flex-shrink:0}
.rbtn.on{background:#FF4D4F;animation:pulse 1s infinite}
@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.08)}}
</style>
