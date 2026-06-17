<template>
<view v-if="visible" class="poster-mask" @tap="close">
  <view class="poster-modal" @tap.stop>
    <canvas canvas-id="posterCanvas" :style="{width:canvasW+'px',height:canvasH+'px'}"></canvas>
    <view class="poster-actions">
      <button size="mini" type="primary" @tap="savePoster" class="btn-save">保存到相册</button>
      <button size="mini" @tap="close" class="btn-cancel">关闭</button>
    </view>
  </view>
</view>
</template>

<script setup>
import {ref,watch,nextTick} from 'vue'

const props=defineProps({
  visible:{type:Boolean,default:false},
  type:{type:String,default:'checkin'},
  data:{type:Object,default:()=>({})}
})

const emit=defineEmits(['close'])
const canvasW=ref(375)
const canvasH=ref(600)

const sysInfo=uni.getSystemInfoSync()
const scale=sysInfo.pixelRatio||2
canvasW.value=sysInfo.windowWidth||375
canvasH.value=canvasW.value*1.6

watch(()=>props.visible,async (v)=>{
  if(v){
    await nextTick()
    setTimeout(()=>drawPoster(),300)
  }
})

async function drawPoster(){
  const ctx=uni.createCanvasContext('posterCanvas')
  const W=canvasW.value
  const H=canvasH.value
  const d=props.data||{}

  // 1. 渐变背景
  const bgGrad=ctx.createLinearGradient(0,0,0,H)
  bgGrad.addColorStop(0,'#FF6B35')
  bgGrad.addColorStop(1,'#FF8C5A')
  ctx.setFillStyle(bgGrad)
  ctx.fillRect(0,0,W,H)

  // 2. 白色内容卡片
  const cardTop=H*0.15
  const cardH=H*0.7
  ctx.setFillStyle('#FFFFFF')
  roundRect(ctx,16,cardTop,W-32,cardH,12)

  // 3. 标题
  ctx.setFontSize(18)
  ctx.setFillStyle('#1A1A1A')
  ctx.setTextAlign('center')
  ctx.fillText('口才训练营',W/2,cardTop+40)

  // 4. 描述文字
  const titles={checkin:'今日打卡成功！',achievement:'恭喜达成新成就！',score:'练习评测结果'}
  ctx.setFontSize(14)
  ctx.setFillStyle('#FF6B35')
  ctx.fillText(titles[props.type]||'口才练习记录',W/2,cardTop+68)

  // 5. 统计数据
  if(props.type==='checkin'){
    ctx.setFontSize(36)
    ctx.setFillStyle('#FF6B35')
    ctx.fillText(`${d.days||0}`,W/2-30,cardTop+128)
    ctx.setFontSize(14)
    ctx.setFillStyle('#666')
    ctx.fillText('天',W/2+20,cardTop+128)
    ctx.fillText('持续打卡',W/2,cardTop+152)
  }else if(props.type==='score'){
    ctx.setFontSize(48)
    ctx.setFillStyle('#FF6B35')
    ctx.fillText(`${d.score||0}`,W/2-20,cardTop+128)
    ctx.setFontSize(16)
    ctx.setFillStyle('#666')
    ctx.fillText('分',W/2+30,cardTop+128)
    ctx.fillText('综合评分',W/2,cardTop+152)
  }else{
    ctx.setFontSize(16)
    ctx.setFillStyle('#666')
    ctx.fillText(`🎖 ${d.badge||'新成就'}`,W/2,cardTop+128)
  }

  // 6. 详细数据
  const detailY=cardTop+190
  ctx.setFontSize(13)
  ctx.setFillStyle('#999')
  ctx.setTextAlign('left')
  const detailX=W/2-60
  if(d.totalDays!==undefined){
    ctx.fillText(`累计打卡：${d.totalDays||0}天`,detailX,detailY)
  }
  if(d.totalMinutes!==undefined){
    ctx.fillText(`练习时长：${d.totalMinutes||0}分钟`,detailX,detailY+22)
  }
  if(d.nickname){
    ctx.fillText(`昵称：${d.nickname}`,detailX,detailY+44)
  }

  // 7. 底部文字
  ctx.setFontSize(11)
  ctx.setFillStyle('rgba(255,255,255,0.9)')
  ctx.setTextAlign('center')
  ctx.fillText('扫码加入口才训练营',W/2,H-16)
  ctx.fillText('每天进步一点点',W/2,H-4)

  ctx.draw(false,()=>{
    console.log('poster drawn')
  })
}

function roundRect(ctx,x,y,w,h,r){
  ctx.beginPath()
  ctx.moveTo(x+r,y)
  ctx.lineTo(x+w-r,y)
  ctx.arcTo(x+w,y,x+w,y+r,r)
  ctx.lineTo(x+w,y+h-r)
  ctx.arcTo(x+w,y+h,x+w-r,y+h,r)
  ctx.lineTo(x+r,y+h)
  ctx.arcTo(x,y+h,x,y+h-r,r)
  ctx.lineTo(x,y+r)
  ctx.arcTo(x,y,x+r,y,r)
  ctx.closePath()
  ctx.fill()
}

async function savePoster(){
  try{
    const res=await new Promise((resolve,reject)=>{
      uni.canvasToTempFilePath({
        canvasId:'posterCanvas',
        success:resolve,
        fail:reject
      },this)
    })
    await uni.saveImageToPhotosAlbum({filePath:res.tempFilePath})
    uni.showToast({title:'海报已保存到相册',icon:'success'})
  }catch(e){
    uni.showToast({title:'保存失败，请检查相册权限',icon:'none'})
  }
}

function close(){emit('close')}
</script>

<style scoped>
.poster-mask{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.7);z-index:9999;display:flex;align-items:center;justify-content:center;flex-direction:column}
.poster-modal{background:#fff;border-radius:16rpx;padding:20rpx;display:flex;flex-direction:column;align-items:center;max-width:90vw}
canvas{border-radius:8rpx}
.poster-actions{display:flex;gap:20rpx;margin-top:20rpx}
.btn-save{background:#FF6B35!important;color:#fff!important;border:none!important}
.btn-cancel{background:#f0f0f0!important;color:#666!important;border:none!important}
</style>
