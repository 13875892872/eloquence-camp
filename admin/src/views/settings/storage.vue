<template>
<div class="page">
  <el-card shadow="never" class="set-card">
    <template #header><div class="card-hd"><span>💾 录音存储概览</span></div></template>
    <el-row :gutter="16">
      <el-col :span="8" v-for="s in stats" :key="s.label">
        <div class="stat-box" :style="{borderColor:s.color}">
          <div class="stat-val" :style="{color:s.color}">{{s.value}}</div>
          <div class="stat-lbl">{{s.label}}</div>
        </div>
      </el-col>
    </el-row>
  </el-card>

  <el-card shadow="never" class="set-card mt16">
    <template #header><div class="card-hd"><span>🧹 存储管理</span></div></template>
    <p class="tip">清理长时间未使用的录音文件以释放存储空间。</p>
    <el-row :gutter="16">
      <el-col :span="8" v-for="a in actions" :key="a.label">
        <div class="action-card">
          <div class="action-icon">{{a.icon}}</div>
          <div class="action-label">{{a.label}}</div>
          <div class="action-desc">{{a.desc}}</div>
          <el-button :type="a.btnType" size="small" disabled>{{a.btnText}}</el-button>
        </div>
      </el-col>
    </el-row>
  </el-card>
</div>
</template>

<script setup>
const stats = [
  {label:'OSS 总存储',value:'12.5 GB',color:'#FF6B35'},
  {label:'总录音文件',value:'8,432 个',color:'#1890FF'},
  {label:'近30天新增',value:'1,234 个',color:'#52C41A'},
]
const actions = [
  {icon:'🗑️',label:'清理旧录音',desc:'删除90天前的录音文件',btnType:'danger',btnText:'清理（开发中）'},
  {icon:'📦',label:'导出备份',desc:'下载全部录音文件备份',btnType:'primary',btnText:'导出（开发中）'},
  {icon:'📊',label:'存储报告',desc:'生成存储使用分析报告',btnType:'success',btnText:'生成（开发中）'},
]
</script>

<style scoped>
.page{padding:0}.set-card{border-radius:10px}.card-hd{font-weight:600}.mt16{margin-top:16px}
.stat-box{text-align:center;padding:24px 16px;border-radius:12px;border:2px solid #eee;background:#fafafa}
.stat-val{font-size:28px;font-weight:bold;margin-bottom:4px}
.stat-lbl{font-size:13px;color:#999}
.tip{color:#999;font-size:13px;margin-bottom:16px}
.action-card{text-align:center;padding:20px 16px;background:#fafafa;border-radius:10px}
.action-icon{font-size:32px;margin-bottom:8px}
.action-label{font-size:15px;font-weight:600;color:#333;margin-bottom:4px}
.action-desc{font-size:12px;color:#999;margin-bottom:12px}
</style>
