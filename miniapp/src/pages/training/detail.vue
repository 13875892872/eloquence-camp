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
      <view v-if="item.locked" class="lock-banner">
        <text>🔒 {{ item.lock_reason || '升级等级后解锁' }}</text>
      </view>
      <view v-if="item.last_practice" class="last-practice">
        <text>上次练习 {{ item.last_practice.ai_score }} 分 · {{ item.last_practice.duration }}秒</text>
      </view>
      <view class="dtx"><text>{{item.sample_text}}</text></view>
      <view class="ab" @tap="playSample">
        <text>{{sampleStatus}}</text>
      </view>
    </view>

    <view class="rc">
      <!-- 初始状态 -->
      <text class="rh" v-if="!recording&&!uploading&&!result">点击按钮开始录音练习</text>

      <!-- 录音中 -->
      <view v-if="recording || paused" class="rs">
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
        <view v-if="lastPracticeScore != null" class="compare-box">
          <text>较上次 {{ scoreDelta >= 0 ? '提升' : '下降' }} {{ Math.abs(scoreDelta) }} 分</text>
          <text class="compare-detail">上次 {{ lastPracticeScore }} 分 → 本次 {{ result.ai_score }} 分</text>
        </view>
        <ScoreRadar :scores="result.dimension_scores" :size="220" />
        <text class="rfb">{{result.ai_feedback}}</text>
        <!-- 回放录音按钮 -->
        <view v-if="userAudioUrl" class="replay-btn" @tap="replayRecording">
          <text>{{replayStatus}}</text>
        </view>
        <view class="share-row">
          <button size="mini" class="share-btn" @tap="openPoster">分享成绩</button>
        </view>
      </view>

      <!-- 录音控制 -->
      <view v-if="recording || paused" class="rec-controls">
        <button class="rbtn sub" @tap="togglePause">{{ paused ? '▶ 继续' : '⏸ 暂停' }}</button>
        <button class="rbtn on" @tap="stopRecord">⏹ 完成</button>
      </view>
      <button v-else class="rbtn" :class="{on:uploading}" @tap="toggleRecord" :disabled="uploading||item.locked">
        {{ item.locked ? '🔒 未解锁' : (uploading ? '上传中...' : '🎤 录音') }}
      </button>
      <text class="rtip" v-if="!recording&&!paused&&!result">最长5分钟 · 支持暂停</text>
    </view>
  </template>
  <Poster :visible="showPoster" type="score" :data="posterData" @close="showPoster=false"/>
</view>
</template>

<script setup>
import {ref,reactive,computed} from 'vue';import {onLoad,onUnload,onShow} from '@dcloudio/uni-app';import api,{BASE_API} from '@/api/request'
import { catLabel, showGoalAchieved } from '@/utils/category'
import Poster from '@/components/poster.vue'
import ScoreRadar from '@/components/ScoreRadar.vue'
import { savePendingUpload, retryPendingUploads } from '@/utils/recordingCache'

const item=ref(null),playing=ref(false),recording=ref(false),paused=ref(false),uploading=ref(false),timer=ref(0),result=ref(null),uploadProgress=ref(0)
const waveHeights=reactive([20,30,40,50,40,30]),isFavorited=ref(false),userAudioUrl=ref(''),replayStatus=ref('🔊 回放我的录音')
const showPoster=ref(false),posterData=ref({})
let ti=null,wi=null,recorderManager=null,audioContext=null,replayContext=null,taskIndex=null,minDuration=30,lastRecordId=null
let recordStartTs=0, pausedTotal=0, pauseStartTs=0

const lastPracticeScore = computed(() => item.value?.last_practice?.ai_score ?? null)
const scoreDelta = computed(() => {
  if (lastPracticeScore.value == null || !result.value) return 0
  return (result.value.ai_score || 0) - lastPracticeScore.value
})

const cl=catLabel
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
    stopTimers(true)
    await uploadAudio(res.tempFilePath,res.duration||timer.value*1000)
  })
  recorderManager.onError((err)=>{
    console.error('录音错误',err)
    stopTimers(true)
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
  // 回放录音的独立音频上下文
  replayContext=uni.createInnerAudioContext()
  replayContext.onEnded(()=>{ replayStatus.value='🔊 回放我的录音' })
  replayContext.onError((err)=>{
    console.error('回放错误',err)
    replayStatus.value='🔊 回放我的录音'
    uni.showToast({title:'回放失败',icon:'none'})
  })
}

// ========== 回放自己的录音 ==========
function replayRecording(){
  if(!userAudioUrl.value) return
  if(replayStatus.value==='⏸ 暂停回放'){
    replayContext.pause()
    replayStatus.value='🔊 回放我的录音'
    return
  }
  const fullUrl=userAudioUrl.value.startsWith('http')?userAudioUrl.value:(BASE_API.replace('/api','')+userAudioUrl.value)
  replayContext.src=fullUrl
  replayContext.play()
  replayStatus.value='⏸ 暂停回放'
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
      const payload={text:item.value.sample_text.substring(0,200)}
      if(item.value.id) payload.training_item_id=item.value.id
      const data=await api.post('/ai-speech/tts',payload)
      uni.hideLoading()
      if(data.audio_url){
        // 缓存到本地，下次直接复用
        if(!data.cached) item.value.sample_audio_url=data.audio_url
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
            userAudioUrl.value=audioUrl  // 保存以便回放
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
        uni.showToast({title:'网络异常，录音已本地保存',icon:'none'})
        persistPending(filePath, duration)
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
    lastRecordId=data.record_id
    await completeCheckinTask(Math.round(duration||timer.value), data.record_id)
    uni.showToast({title:`评分 ${data.ai_score} 分`,icon:'success'})
  }catch(e){
    console.error('评测失败',e)
    result.value={
      ai_score:70,
      dimension_scores:{pronunciation:70,fluency:70,completeness:70,content:70,expressiveness:70},
      ai_feedback:'评测服务暂不可用，请稍后重试'
    }
    await completeCheckinTask(Math.round(duration||timer.value), null)
  }
}

async function completeCheckinTask(duration, practiceRecordId){
  if(!taskIndex) return
  try{
    const payload={ task_index: taskIndex }
    if(practiceRecordId) payload.practice_record_id=practiceRecordId
    else payload.duration=duration
    const res=await api.post('/checkin/complete-task', payload)
    showGoalAchieved(res)
  }catch(e){
    const msg=e?.message||e?.data?.message||''
    if(msg) uni.showToast({title:msg,icon:'none'})
  }
}

function openPoster(){
  posterData.value={
    score:result.value?.ai_score||0,
    nickname:'我',
    title:item.value?.title||'口才练习',
  }
  showPoster.value=true
}

// ========== 录音控制 ==========
function persistPending(filePath, duration) {
  uni.saveFile({
    tempFilePath: filePath,
    success: (res) => {
      savePendingUpload({
        savedPath: res.savedFilePath,
        training_item_id: item.value?.id,
        task_index: taskIndex,
        duration: Math.round(duration || timer.value),
        reference_text: item.value?.sample_text || '',
      })
    },
    fail: () => {
      savePendingUpload({
        savedPath: filePath,
        training_item_id: item.value?.id,
        task_index: taskIndex,
        duration: Math.round(duration || timer.value),
        reference_text: item.value?.sample_text || '',
      })
    },
  })
}

async function retryPending() {
  await retryPendingUploads(async (entry) => {
    if (entry.training_item_id && entry.training_item_id !== item.value?.id) return
    await uploadAudio(entry.savedPath, entry.duration)
  })
}

function toggleRecord(){
  if(item.value?.locked) return uni.showToast({title:item.value.lock_reason||'未解锁',icon:'none'})
  if(recording.value || paused.value) return
  uni.authorize({
    scope:'scope.record',
    success:()=>startRecord(),
    fail:()=>uni.showModal({title:'需要录音权限',content:'请在设置中开启麦克风权限',success:r=>{if(r.confirm)uni.openSetting()}})
  })
}

function togglePause(){
  if(!recorderManager) return
  if(paused.value){
    recorderManager.resume()
    paused.value=false
    pausedTotal += Date.now() - pauseStartTs
    startTimers()
  }else{
    recorderManager.pause()
    paused.value=true
    pauseStartTs=Date.now()
    stopTimers(false)
  }
}

function stopRecord(){
  if(recorderManager && (recording.value || paused.value)){
    recorderManager.stop()
    stopTimers(true)
  }
}

function startTimers(){
  ti=setInterval(()=>{
    timer.value=Math.floor((Date.now()-recordStartTs-pausedTotal)/1000)
    if(timer.value>=300) stopRecord()
  },500)
  wi=setInterval(()=>{
    for(let i=0;i<6;i++) waveHeights[i]=Math.max(15,Math.min(80,waveHeights[i]+(Math.random()-0.5)*30))
  },200)
}

function stopTimers(resetPaused){
  if(ti){clearInterval(ti);ti=null}
  if(wi){clearInterval(wi);wi=null}
  if(resetPaused){ paused.value=false; recording.value=false }
}

function startRecord(){
  recording.value=true
  paused.value=false
  result.value=null
  timer.value=0
  recordStartTs=Date.now()
  pausedTotal=0
  startTimers()
  recorderManager.start({duration:300000,sampleRate:16000,numberOfChannels:1,encodeBitRate:48000,format:'mp3',frameSize:1})
}

// ========== 生命周期 ==========
onLoad(async opt=>{
  initRecorder()
  initAudio()
  if(opt?.id){
    try{item.value=await api.get('/training/items/'+opt.id)}catch(e){}
    checkFav()
  }
  if(opt?.tk) taskIndex=parseInt(opt.tk)
  if(opt?.min) minDuration=parseInt(opt.min)||30
  uni.authorize({ scope: 'scope.record', fail: () => {} })
})
onShow(()=>{ retryPending() })

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
  if(replayContext){
    replayContext.destroy()
  }
})
</script>

<style scoped>
.dc{background:var(--bg-card);border-radius:20rpx;padding:24rpx;margin-bottom:20rpx;width:100%;box-sizing:border-box;overflow:hidden;box-shadow:var(--card-shadow)}
.dc-header{display:flex;justify-content:space-between;align-items:flex-start;width:100%}
.dt{font-size:34rpx;font-weight:bold;display:block;flex:1;min-width:0}
.fav-icon{font-size:40rpx;flex-shrink:0;margin-left:16rpx;color:#ccc}
.fav-icon.faved{color:#FAAD14}
.dm{font-size:22rpx;color:#999;display:block;margin:8rpx 0}
.dtx{background:var(--bg-secondary);border-radius:16rpx;padding:20rpx;margin-top:14rpx;font-size:26rpx;line-height:1.7;word-break:break-all;max-height:400rpx;overflow-y:auto;width:100%;box-sizing:border-box}
.ab{background:var(--bg-brand-light);border-radius:14rpx;padding:16rpx;text-align:center;margin-top:14rpx;color:var(--brand-primary);font-size:26rpx;width:100%;box-sizing:border-box}
.ab:active{background:var(--hero-to)}
.rc{text-align:center;padding:30rpx 0}.rh{font-size:26rpx;color:#999}
.rs{padding:30rpx 0}.wv{display:flex;justify-content:center;align-items:flex-end;gap:6rpx;margin-bottom:14rpx;height:90rpx}
.wvb{width:5rpx;background:var(--brand-primary);border-radius:3rpx;transition:height .15s;min-height:10rpx}
.rt{font-size:44rpx;font-weight:bold;color:var(--brand-primary)}
.rtip{font-size:22rpx;color:#999;display:block;margin-top:10rpx}
.up-bar{width:300rpx;height:8rpx;background:#f0f0f0;border-radius:4rpx;margin:16rpx auto 0;overflow:hidden}
.up-fill{height:100%;background:var(--brand-primary);border-radius:4rpx;transition:width .3s}
.ra{background:var(--bg-card);border-radius:20rpx;padding:24rpx;margin-bottom:20rpx;width:100%;box-sizing:border-box;overflow:hidden;box-shadow:var(--card-shadow)}
.rsc{font-size:36rpx;font-weight:bold;color:#E31837;text-align:center;display:block}
.rd{margin:20rpx 0}.rdl{display:flex;align-items:center;margin:6rpx 0}.rdn{width:100rpx;font-size:22rpx;color:#666;flex-shrink:0}.rdb{flex:1;height:8rpx;background:#f0f0f0;border-radius:4rpx;overflow:hidden;min-width:0;margin:0 8rpx}.rdf{height:100%;background:linear-gradient(90deg,var(--brand-primary),var(--brand-light));border-radius:4rpx;transition:width .5s}.rdv{width:45rpx;text-align:right;font-size:22rpx;font-weight:bold;color:var(--brand-primary);flex-shrink:0}
.rfb{font-size:24rpx;color:#666;background:var(--bg-secondary);border-radius:14rpx;padding:20rpx;margin-top:14rpx;line-height:1.7;word-break:break-all;display:block;width:100%;box-sizing:border-box}
.rbtn{width:220rpx;height:220rpx;border-radius:50%;background:linear-gradient(135deg,var(--brand-primary),var(--brand-light));color:#fff;font-size:30rpx;font-weight:bold;border:none;display:flex;align-items:center;justify-content:center;margin:20rpx auto;flex-shrink:0;box-shadow:0 8rpx 24rpx rgba(160,216,239,0.4)}
.rbtn.on{background:#FF4D4F;animation:pulse 1s infinite}
.replay-btn{background:var(--bg-brand-light);border-radius:14rpx;padding:16rpx;text-align:center;margin-top:14rpx;color:var(--brand-primary);font-size:26rpx;width:100%;box-sizing:border-box}
.compare-box{background:var(--bg-warm);border-radius:14rpx;padding:16rpx;margin:12rpx 0;text-align:center}
.compare-box text{display:block;font-size:24rpx;color:var(--brand-primary);font-weight:600}
.compare-detail{font-size:22rpx!important;color:#666!important;font-weight:400!important;margin-top:6rpx}
.rec-controls{display:flex;gap:16rpx;margin-top:8rpx}
.rbtn.sub{flex:1;background:var(--bg-brand-light);color:var(--brand-primary);font-size:28rpx;border-radius:48rpx;border:none}
.rbtn.on{flex:1}
.share-row{margin-top:16rpx;text-align:center}
.share-btn{background:var(--brand-primary);color:#fff;border-radius:32rpx;font-size:24rpx}
.lock-banner{background:#FFF7E6;border-radius:12rpx;padding:16rpx;margin-top:12rpx;color:#D48806;font-size:24rpx}
.last-practice{font-size:22rpx;color:#999;margin-top:8rpx;display:block}
.replay-btn:active{background:var(--hero-to)}
@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.08)}}
</style>
