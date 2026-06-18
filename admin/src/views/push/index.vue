<template>
<div class="ps">
  <el-card shadow="never" header="推送模板管理">
    <el-table :data="tpls" size="small">
      <el-table-column prop="name" label="模板名称" width="140"/>
      <el-table-column prop="type" label="类型" width="120"/>
      <el-table-column prop="push_time" label="推送时间" width="100"><template #default="{row}">{{row.push_time||'-'}}</template></el-table-column>
      <el-table-column label="状态" width="80"><template #default="{row}"><el-switch v-model="row.is_active" active-color="#FF6B35" size="small"/></template></el-table-column>
      <el-table-column label="操作" width="100"><template #default="{row}"><el-button size="small" @click="st(row)">保存</el-button></template></el-table-column>
    </el-table>
  </el-card>

  <el-card shadow="never" header="手动推送消息" class="mt16">
    <el-form :model="pf" label-width="80px">
      <el-row :gutter="16">
        <el-col :span="8"><el-form-item label="推送模板"><el-select v-model="pf.template_type"><el-option label="新素材上线通知" value="new_material"/></el-select></el-form-item></el-col>
        <el-col :span="8"><el-form-item label="推送对象"><el-radio-group v-model="pf.target"><el-radio value="all">全部用户</el-radio></el-radio-group></el-form-item></el-col>
      </el-row>
      <el-form-item label="推送标题"><el-input v-model="pf.title" placeholder="输入推送消息标题"/></el-form-item>
      <el-form-item label="推送内容"><el-input v-model="pf.content" type="textarea" :rows="3" placeholder="输入推送消息正文内容"/></el-form-item>
      <el-form-item><el-button type="primary" @click="sp" :loading="sending">📢 立即推送</el-button></el-form-item>
    </el-form>
  </el-card>

  <el-card shadow="never" header="推送记录" class="mt16">
    <el-table :data="recs" v-loading="rl" size="small" empty-text="暂无推送记录">
      <el-table-column prop="template_type" label="类型" width="120"/>
      <el-table-column prop="title" label="标题" min-width="160" show-overflow-tooltip/>
      <el-table-column prop="target_count" label="目标" width="70"/>
      <el-table-column prop="reach_count" label="触达" width="70"/>
      <el-table-column label="状态" width="80"><template #default="{row}"><el-tag :type="row.status==='success'?'success':'warning'" size="small">{{row.status}}</el-tag></template></el-table-column>
      <el-table-column label="时间" width="150"><template #default="{row}">{{row.created_at?.slice(0,16)||'-'}}</template></el-table-column>
    </el-table>
    <div class="mt16" style="text-align:right"><el-pagination v-model:current-page="rp" :page-size="20" :total="rt" layout="total,prev,pager,next" @current-change="lr"/></div>
  </el-card>
</div>
</template>

<script setup>
import {ref,reactive,onMounted} from 'vue';import {ElMessage} from 'element-plus';import request from '@/api/request'
const tpls=ref([]),pf=reactive({template_type:'new_material',title:'',content:'',target:'all'}),sending=ref(false),recs=ref([]),rl=ref(false),rp=ref(1),rt=ref(0)

async function lt2(){
  try{
    tpls.value=(await request.get('/admin/push-templates')).templates||[]
  }catch(e){
    tpls.value=[]
  }
}
async function st(row){
  try{
    await request.put('/admin/push-templates/'+row.id,{...row})
    ElMessage.success('模板已保存')
  }catch(e){
    ElMessage.error('模板保存失败')
  }
}
async function lr(){
  rl.value=true
  try{
    const d=await request.get('/admin/push-records',{page:rp.value})
    recs.value=d.items||[]
    rt.value=d.pagination?.total||0
  }catch(e){
    recs.value=[]
    rt.value=0
  }
  rl.value=false
}
async function sp(){
  if(!pf.title)return ElMessage.warning('请输入推送标题')
  sending.value=true
  try{
    await request.post('/admin/push/manual',{...pf})
    ElMessage.success('推送成功')
    pf.title=''
    pf.content=''
    lr()
  }catch(e){
    ElMessage.error('推送失败')
  }finally{sending.value=false}
}
onMounted(()=>{lt2();lr()})
</script>

<style scoped>.ps{padding:0}.mt16{margin-top:16px}</style>
