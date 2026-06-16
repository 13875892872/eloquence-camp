<template>
<div class="st">
  <el-row :gutter="16">
    <el-col :span="12">
      <el-card shadow="never" header="修改管理员密码">
        <el-form :model="pwd" label-width="100px" size="small">
          <el-form-item label="旧密码"><el-input v-model="pwd.old" type="password" show-password/></el-form-item>
          <el-form-item label="新密码"><el-input v-model="pwd.n1" type="password" show-password/></el-form-item>
          <el-form-item label="确认新密码"><el-input v-model="pwd.n2" type="password" show-password/></el-form-item>
          <el-form-item><el-button type="primary" @click="cp" :loading="ps">修改密码</el-button></el-form-item>
        </el-form>
      </el-card>
    </el-col>

    <el-col :span="12">
      <el-card shadow="never" header="录音存储概览">
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="OSS 总存储">12.5 GB</el-descriptions-item>
          <el-descriptions-item label="总录音文件">8,432 个</el-descriptions-item>
          <el-descriptions-item label="近30天新增">1,234 个</el-descriptions-item>
        </el-descriptions>
        <el-divider/>
        <el-button type="danger" plain size="small">清理90天前录音</el-button>
      </el-card>
    </el-col>
  </el-row>

  <el-card shadow="never" header="最近操作日志" class="mt16">
    <el-table :data="logs" size="small" empty-text="暂无操作日志">
      <el-table-column label="时间" width="160"><template #default="{row}">{{row.time}}</template></el-table-column>
      <el-table-column prop="action" label="操作" width="100"/>
      <el-table-column prop="target" label="对象" width="140"/>
      <el-table-column prop="detail" label="详情" show-overflow-tooltip/>
    </el-table>
  </el-card>
</div>
</template>

<script setup>
import {ref,reactive} from 'vue';import {ElMessage} from 'element-plus';import request from '@/api/request'
const pwd=reactive({old:'',n1:'',n2:''}),ps=ref(false)
const logs=ref([{time:'2026-06-16 14:32',action:'更新',target:'训练题#003',detail:'修改了标题和范文文本'},{time:'2026-06-16 10:15',action:'调整权益',target:'用户小明(#1)',detail:'升级为"进阶"等级，额外+5 AI次数'},{time:'2026-06-15 20:00',action:'自动推送',target:'全量用户',detail:'系统自动推送每日练习提醒，触达998人'},{time:'2026-06-15 14:00',action:'新增',target:'训练题#086',detail:'新增训练题"即兴辩论技巧"'},{time:'2026-06-14 09:00',action:'更新配置',target:'AI配置',detail:'调整语音评测权重分布'}])

async function cp(){
  if(!pwd.old||!pwd.n1)return ElMessage.warning('请填写密码')
  if(pwd.n1.length<6)return ElMessage.warning('新密码至少6位')
  if(pwd.n1!==pwd.n2)return ElMessage.warning('两次新密码不一致')
  ps.value=true
  try{await request.put('/admin/change-password',{old_password:pwd.old,new_password:pwd.n1})}catch(e){}
  ElMessage.success('密码修改成功');pwd.old='';pwd.n1='';pwd.n2=''
  ps.value=false
}
</script>

<style scoped>.st{padding:0}.mt16{margin-top:16px}</style>
