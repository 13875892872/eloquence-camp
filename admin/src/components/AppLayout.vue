<template>
  <el-container class="app-layout">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '240px'" class="aside">
      <div class="logo" @click="router.push('/dashboard')">
        <span v-if="!isCollapse">🎤 口才训练营后台</span>
        <span v-else>🎤</span>
      </div>
      <el-menu :default-active="activeMenu" router :collapse="isCollapse"
        background-color="#304156" text-color="#bfcbd9" active-text-color="#FF6B35">
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <span>数据看板</span>
        </el-menu-item>
        <el-sub-menu index="training-group">
          <template #title>
            <el-icon><Memo /></el-icon>
            <span>素材管理</span>
          </template>
          <el-menu-item index="/training">训练题库</el-menu-item>
          <el-menu-item index="/training/recommend">热门推荐</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="checkin-group">
          <template #title>
            <el-icon><Calendar /></el-icon>
            <span>打卡配置</span>
          </template>
          <el-menu-item index="/checkin/tasks">每日任务</el-menu-item>
          <el-menu-item index="/checkin/growth">成长目标</el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/ai">
          <el-icon><Cpu /></el-icon>
          <span>AI配置</span>
        </el-menu-item>
        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/push">
          <el-icon><Message /></el-icon>
          <span>消息推送</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 右侧内容区 -->
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="isCollapse = !isCollapse" :size="22">
            <Fold v-if="!isCollapse" /><Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path" :to="item.path">
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <span class="admin-name">{{ adminName }}</span>
          <el-button text @click="handleLogout">退出登录</el-button>
        </div>
      </el-header>

      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const isCollapse = ref(false)

const adminName = computed(() => {
  const info = localStorage.getItem('admin_info')
  try { return JSON.parse(info)?.username || '管理员' }
  catch { return '管理员' }
})

const activeMenu = computed(() => route.path)

const breadcrumbs = computed(() => {
  const matched = route.matched.filter(r => r.meta?.title && !r.meta?.hidden)
  return matched.map(r => ({ path: r.path, title: r.meta.title }))
})

function handleLogout() {
  localStorage.removeItem('admin_token')
  localStorage.removeItem('admin_info')
  router.push('/login')
}
</script>

<style scoped lang="scss">
.app-layout { height: 100vh; }
.aside {
  background: #304156;
  overflow-y: auto;
  transition: width 0.3s;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e8e8e8;
  padding: 0 20px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
.collapse-btn { cursor: pointer; &:hover { color: #FF6B35; } }
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.admin-name { color: #666; font-size: 14px; }
.main {
  background: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}
</style>
