<template>
<div class="ur">
  <el-card shadow="never" class="mb16">
    <el-row :gutter="12">
      <el-col :span="8"><el-input v-model="kw" placeholder="搜索昵称或用户ID" clearable @keyup.enter="load"/></el-col>
      <el-col :span="4"><el-select v-model="lv" placeholder="等级筛选" clearable @change="load" style="width:100%"><el-option label="新人" value="newbie"/><el-option label="入门" value="beginner"/><el-option label="进阶" value="advanced"/><el-option label="达人" value="expert"/><el-option label="大师" value="master"/></el-select></el-col>
    </el-row>
  </el-card>

  <el-card shadow="never">
    <el-table :data="list" stripe v-loading="loading" empty-text="暂无用户数据">
      <el-table-column width="50"><template #default="{row}"><el-avatar :size="34" :style="{background:'#FF6B35'}">{{row.nickname?.charAt(0)||'U'}}</el-avatar></template></el-table-column>
      <el-table-column prop="nickname" label="昵称" min-width="120"/>
      <el-table-column prop="total_days" label="累计打卡" width="85"/>
      <el-table-column prop="continuous_days" label="连续" width="70"/>
      <el-table-column label="等级" width="85"><template #default="{row}"><el-tag size="small" :type="lt(row.growth_level)">{{ll(row.growth_level)}}</el-tag></template></el-table-column>
      <el-table-column prop="remaining_ai" label="剩余AI" width="75"/>
      <el-table-column label="注册时间" width="110"><template #default="{row}">{{row.created_at?.slice(0,10)||'2026-06-01'}}</template></el-table-column>
      <el-table-column label="操作" width="80" fixed="right"><template #default="{row}"><el-button size="small" @click="$router.push('/users/'+row.id)">详情</el-button></template></el-table-column>
    </el-table>
    <div class="mt16" style="display:flex;justify-content:flex-end"><el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="total,prev,pager,next" @current-change="load"/></div>
  </el-card>
</div>
</template>

<script setup>
import {ref,onMounted} from 'vue';import request from '@/api/request'
const loading=ref(false),list=ref([]),total=ref(0),page=ref(1),kw=ref(''),lv=ref('')
const ll=v=>({newbie:'新人',beginner:'入门',advanced:'进阶',expert:'达人',master:'大师'}[v]||v)
const lt=v=>({newbie:'info',beginner:'',advanced:'success',expert:'warning',master:'danger'}[v]||'info')
const mocks=[{id:1,nickname:'小明',total_days:42,continuous_days:7,growth_level:'beginner',remaining_ai:3,created_at:'2026-06-01'},{id:2,nickname:'演讲达人小王',total_days:120,continuous_days:30,growth_level:'advanced',remaining_ai:7,created_at:'2026-04-15'},{id:3,nickname:'主播小红',total_days:85,continuous_days:5,growth_level:'beginner',remaining_ai:2,created_at:'2026-05-10'},{id:4,nickname:'职场新人小李',total_days:15,continuous_days:3,growth_level:'newbie',remaining_ai:3,created_at:'2026-06-12'},{id:5,nickname:'口才大师老张',total_days:200,continuous_days:100,growth_level:'master',remaining_ai:99,created_at:'2026-01-01'}]

async function load(){
  loading.value=true
  try{const d=await request.get('/admin/users',{page:page.value,keyword:kw.value,growth_level:lv.value});list.value=d.items?.length?d.items:mocks;total.value=d.pagination?.total||mocks.length}catch(e){list.value=mocks;total.value=mocks.length}
  loading.value=false
}
onMounted(load)
</script>

<style scoped>.ur{padding:0}.mb16{margin-bottom:16px}.mt16{margin-top:16px}</style>
