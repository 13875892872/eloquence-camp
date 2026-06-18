<template>
  <el-card shadow="never" class="set-card">
    <el-form :model="pwd" label-width="100px" size="default" class="pwd-form">
      <el-form-item label="旧密码">
        <el-input v-model="pwd.old" type="password" show-password placeholder="请输入旧密码"/>
      </el-form-item>
      <el-form-item label="新密码">
        <el-input v-model="pwd.n1" type="password" show-password placeholder="至少6位"/>
      </el-form-item>
      <el-form-item label="确认密码">
        <el-input v-model="pwd.n2" type="password" show-password placeholder="再次输入新密码"/>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="cp" :loading="ps">确认修改</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

const pwd = reactive({ old: '', n1: '', n2: '' })
const ps = ref(false)

async function cp() {
  if (!pwd.old || !pwd.n1) return ElMessage.warning('请填写密码')
  if (pwd.n1.length < 6) return ElMessage.warning('新密码至少6位')
  if (pwd.n1 !== pwd.n2) return ElMessage.warning('两次新密码不一致')
  ps.value = true
  try {
    await request.put('/admin/change-password', { old_password: pwd.old, new_password: pwd.n1 })
    ElMessage.success('密码修改成功')
    pwd.old = ''
    pwd.n1 = ''
    pwd.n2 = ''
  } catch (e) {
    ElMessage.error('密码修改失败')
  } finally {
    ps.value = false
  }
}
</script>

<style scoped>
.set-card { border-radius: var(--card-radius); }
.pwd-form { max-width: 440px; padding-top: 8px; }
</style>
