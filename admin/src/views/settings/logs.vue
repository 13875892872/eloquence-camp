<template>
<div class="page">
  <el-card shadow="never" class="set-card">
    <template #header>
      <div class="card-top">
        <span class="card-hd">📋 操作日志</span>
        <el-pagination
          v-model:current-page="page" small layout="prev,next"
          :page-size="5" :total="logs.length" background
        />
      </div>
    </template>

    <!-- 时间线 -->
    <div class="timeline">
      <div class="tl-item" v-for="(item,i) in pagedLogs" :key="i">
        <div class="tl-dot" :style="{background:item.color}"></div>
        <div class="tl-line" v-if="i < pagedLogs.length-1"></div>
        <div class="tl-body">
          <div class="tl-head">
            <el-tag :type="item.tagType" size="small" effect="plain">{{item.action}}</el-tag>
            <span class="tl-target">{{item.target}}</span>
          </div>
          <div class="tl-detail">{{item.detail}}</div>
          <div class="tl-time">{{item.time}}</div>
        </div>
      </div>
    </div>
  </el-card>
</div>
</template>

<script setup>
import {ref,computed} from 'vue'

const page=ref(1)
const logs=ref([
  {time:'2026-06-17 17:30',action:'更新配置',target:'AI配置',detail:'调整语音评测权重为30/25/20/15/10',tagType:'warning',color:'#FAAD14'},
  {time:'2026-06-17 15:20',action:'新增素材',target:'训练题库',detail:'调度器自动生成6条训练素材（热搜+名言）',tagType:'success',color:'#52C41A'},
  {time:'2026-06-17 14:32',action:'编辑',target:'训练题#003',detail:'修改了标题和范文文本',tagType:'info',color:'#1890FF'},
  {time:'2026-06-16 10:15',action:'调整权益',target:'用户小明(#1)',detail:'升级为"进阶"等级，额外+5 AI次数',tagType:'info',color:'#1890FF'},
  {time:'2026-06-16 08:00',action:'系统任务',target:'素材获取',detail:'调度器自动获取11条原始素材，入库7条',tagType:'success',color:'#52C41A'},
  {time:'2026-06-15 20:00',action:'自动推送',target:'全量用户',detail:'每日练习提醒推送，触达998人',tagType:'',color:'#999'},
  {time:'2026-06-15 14:00',action:'新增',target:'训练题#086',detail:'新增训练题"即兴辩论技巧"',tagType:'success',color:'#52C41A'},
  {time:'2026-06-15 09:30',action:'登录',target:'系统',detail:'管理员 admin 登录后台',tagType:'info',color:'#1890FF'},
  {time:'2026-06-14 16:00',action:'更新配置',target:'每日任务',detail:'修改任务2副标题和时长要求',tagType:'warning',color:'#FAAD14'},
  {time:'2026-06-14 09:00',action:'更新配置',target:'成长目标',detail:'调整高级目标所需天数从30改为21',tagType:'warning',color:'#FAAD14'},
])

const pagedLogs = computed(() => {
  const start = (page.value - 1) * 5
  return logs.value.slice(start, start + 5)
})
</script>

<style scoped>
.page{padding:0}.set-card{border-radius:10px}
.card-top{display:flex;justify-content:space-between;align-items:center}
.card-hd{font-weight:600}

.timeline{padding:8px 0 0 12px}
.tl-item{display:flex;gap:12px;position:relative;padding-bottom:20px}
.tl-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0;margin-top:6px;z-index:1}
.tl-line{position:absolute;left:4px;top:22px;width:2px;height:calc(100% - 16px);background:#e8e8e8}
.tl-body{flex:1;min-width:0}
.tl-head{display:flex;align-items:center;gap:8px;margin-bottom:4px}
.tl-target{font-size:13px;color:#333;font-weight:500}
.tl-detail{font-size:13px;color:#666;line-height:1.5;margin-bottom:2px}
.tl-time{font-size:11px;color:#bbb}
</style>
