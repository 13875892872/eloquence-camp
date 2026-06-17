<template>
<view class="page">
  <!-- 月份切换 -->
  <view class="month-switcher">
    <text class="ms-arrow" @tap="prevMonth">←</text>
    <text class="ms-label">{{currentYear}}年{{currentMonth}}月</text>
    <text class="ms-arrow" @tap="nextMonth">→</text>
  </view>

  <!-- 星期头 -->
  <view class="weekday-row">
    <text class="wd" v-for="d in weekdays" :key="d">{{d}}</text>
  </view>

  <!-- 日历网格 -->
  <view class="calendar-grid">
    <view class="day" v-for="(d,i) in daysList" :key="i"
      :class="{checked:d.checked, today:d.isToday, empty:!d.day}">
      <text v-if="d.day" class="day-num" :class="{'checked-num':d.checked}">{{d.day}}</text>
      <text v-if="d.checked" class="day-dot">✓</text>
    </view>
  </view>

  <!-- 统计 -->
  <view class="card stats-card" v-if="summary">
    <text class="st">本月打卡 <text class="highlight">{{summary.total}}</text> 天</text>
    <text class="sd">坚持就是胜利，每天进步一点点！</text>
  </view>
</view>
</template>

<script setup>
import {ref,computed} from 'vue';import {onLoad} from '@dcloudio/uni-app';import api from '@/api/request'

const currentYear=ref(new Date().getFullYear())
const currentMonth=ref(new Date().getMonth()+1)
const checkedDays=ref([])
const summary=ref(null)
const weekdays=['日','一','二','三','四','五','六']

const daysList=computed(()=>{
  const year=currentYear.value
  const month=currentMonth.value
  const firstDay=new Date(year,month-1,1).getDay() // 当月1号星期几
  const daysInMonth=new Date(year,month,0).getDate() // 当月总天数
  const today=new Date()
  const todayStr=`${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,'0')}-${String(today.getDate()).padStart(2,'0')}`

  const list=[]
  // 填充前面的空白
  for(let i=0;i<firstDay;i++){
    list.push({day:null,checked:false,isToday:false})
  }
  // 填充日期
  for(let d=1;d<=daysInMonth;d++){
    const dateStr=`${year}-${String(month).padStart(2,'0')}-${String(d).padStart(2,'0')}`
    list.push({
      day:d,
      checked:checkedDays.value.includes(dateStr),
      isToday:dateStr===todayStr
    })
  }
  return list
})

async function load(){
  try{
    const d=await api.get('/checkin/calendar',{year:currentYear.value,month:currentMonth.value})
    checkedDays.value=d.days||[]
    summary.value=d.summary||null
  }catch(e){}
}

function prevMonth(){
  if(currentMonth.value===1){currentMonth.value=12;currentYear.value--}
  else currentMonth.value--
  load()
}

function nextMonth(){
  if(currentMonth.value===12){currentMonth.value=1;currentYear.value++}
  else currentMonth.value++
  load()
}

onLoad(()=>{load()})
</script>

<style scoped>
.month-switcher{display:flex;justify-content:space-between;align-items:center;padding:24rpx 0;width:100%}
.ms-arrow{font-size:36rpx;color:#FF6B35;padding:8rpx 24rpx}
.ms-label{font-size:34rpx;font-weight:bold}
.weekday-row{display:flex;background:#FFF8F5;border-radius:16rpx;padding:14rpx 0;margin-bottom:10rpx;width:100%}
.wd{flex:1;text-align:center;font-size:24rpx;color:#666;font-weight:500}
.calendar-grid{display:flex;flex-wrap:wrap;width:100%}
.day{width:calc(100%/7);aspect-ratio:1;display:flex;flex-direction:column;align-items:center;justify-content:center;position:relative}
.day.empty{background:transparent}
.day.checked{background:#FFF0E8;border-radius:16rpx}
.day.today{border:2rpx solid #FF6B35;border-radius:16rpx}
.day-num{font-size:28rpx;color:#1A1A1A}
.checked-num{color:#FF6B35;font-weight:bold}
.day-dot{font-size:18rpx;color:#52C41A;margin-top:2rpx}
.card{background:var(--bg-card);border-radius:24rpx;padding:28rpx;margin-top:24rpx;width:100%;box-sizing:border-box;overflow:hidden}
.st{font-size:32rpx;font-weight:bold;display:block;margin-bottom:8rpx}
.highlight{color:#FF6B35}
.sd{font-size:24rpx;color:#999;display:block}
</style>
