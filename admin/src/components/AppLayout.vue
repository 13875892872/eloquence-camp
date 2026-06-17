<template>
  <el-container class="app-layout">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="aside">
      <!-- 品牌区 -->
      <div class="brand" @click="router.push('/dashboard')">
        <div class="brand-icon">
          <span class="brand-emoji">🎤</span>
        </div>
        <div v-if="!isCollapse" class="brand-text">
          <div class="brand-title">口才训练营</div>
          <div class="brand-sub">管理后台</div>
        </div>
      </div>

      <!-- 导航菜单 -->
      <el-menu
        :default-active="activeMenu"
        router
        :collapse="isCollapse"
        background-color="#1d1e2c"
        text-color="#8b8fa3"
        active-text-color="#fff"
        class="side-menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据看板</span>
        </el-menu-item>

        <el-sub-menu index="content-group">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>内容管理</span>
          </template>
          <el-menu-item index="/training">训练题库</el-menu-item>
          <el-menu-item index="/training/recommend">推荐配置</el-menu-item>
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
          <span>AI 配置</span>
        </el-menu-item>

        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>

        <el-menu-item index="/push">
          <el-icon><ChatDotRound /></el-icon>
          <span>消息推送</span>
        </el-menu-item>

        <el-sub-menu index="settings-group">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统设置</span>
          </template>
          <el-menu-item index="/settings/password">修改密码</el-menu-item>
          <el-menu-item index="/settings/storage">存储管理</el-menu-item>
          <el-menu-item index="/settings/logs">操作日志</el-menu-item>
        </el-sub-menu>
      </el-menu>

      <!-- 底部版本号 -->
      <div v-if="!isCollapse" class="aside-footer">v1.0.0</div>
    </el-aside>

    <!-- 右侧内容区 -->
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="isCollapse = !isCollapse" :size="20">
            <Fold v-if="!isCollapse" /><Expand v-else />
          </el-icon>
          <span class="page-title">{{ pageTitle }}</span>
        </div>
        <div class="header-right">
          <!-- 用户下拉菜单 -->
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-area">
              <el-avatar :size="32" class="user-avatar">{{ adminInitial }}</el-avatar>
              <span class="user-name">{{ adminName }}</span>
              <el-icon class="user-arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="password">
                  <el-icon><Lock /></el-icon>修改密码
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
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

const adminInitial = computed(() => {
  return adminName.value.charAt(0).toUpperCase()
})

const activeMenu = computed(() => {
  // 子菜单激活时高亮父菜单
  if (route.path.startsWith('/training')) return 'content-group'
  if (route.path.startsWith('/checkin')) return 'checkin-group'
  if (route.path.startsWith('/settings')) return 'settings-group'
  return route.path
})

const pageTitle = computed(() => {
  const matched = route.matched.filter(r => r.meta?.title && !r.meta?.hidden)
  return matched.map(r => r.meta.title).join(' / ') || '管理后台'
})

function handleCommand(cmd) {
  if (cmd === 'password') {
    router.push('/settings')
  } else if (cmd === 'logout') {
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_info')
    router.push('/login')
  }
}
</script>

<style scoped lang="scss">
.app-layout { height: 100vh; }

// ── 侧边栏 ──
.aside {
  background: #1d1e2c;
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
  overflow: hidden;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 18px 16px;
  cursor: pointer;
  background: linear-gradient(135deg, #FF6B35, #FF8C5A);
  min-height: 64px;
  box-sizing: border-box;
}
.brand-icon {
  width: 36px;
  height: 36px;
  background: rgba(255,255,255,0.2);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.brand-emoji { font-size: 20px; line-height: 1; }
.brand-text { line-height: 1.3; }
.brand-title {
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  white-space: nowrap;
}
.brand-sub {
  color: rgba(255,255,255,0.7);
  font-size: 11px;
  white-space: nowrap;
}

.side-menu {
  flex: 1;
  border-right: none;
  overflow-y: auto;
  overflow-x: hidden;
}
.side-menu :deep(.el-menu-item) {
  height: 48px;
  line-height: 48px;
  margin: 2px 8px;
  border-radius: 8px;
}
.side-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, #FF6B35, #FF8C5A) !important;
  color: #fff !important;
}
.side-menu :deep(.el-sub-menu .el-menu) {
  background: #151621 !important;
}
.side-menu :deep(.el-sub-menu .el-menu-item) {
  height: 42px;
  line-height: 42px;
  padding-left: 56px !important;
}
.side-menu :deep(.el-sub-menu .el-menu-item.is-active) {
  background: rgba(255,107,53,0.15) !important;
  color: #FF8C5A !important;
}
.side-menu :deep(.el-sub-menu__title) {
  height: 48px;
  line-height: 48px;
  margin: 2px 8px;
  border-radius: 8px;
}

.aside-footer {
  padding: 12px 0;
  text-align: center;
  color: #4a4d5e;
  font-size: 11px;
  border-top: 1px solid #2a2b3a;
}

// ── 头部 ──
.header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  z-index: 10;
  height: 56px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}
.collapse-btn {
  cursor: pointer;
  color: #666;
  &:hover { color: #FF6B35; }
}
.page-title {
  font-size: 15px;
  font-weight: 600;
  color: #1d1e2c;
}

.header-right {
  display: flex;
  align-items: center;
}
.user-area {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 12px 4px 4px;
  border-radius: 20px;
  transition: background 0.2s;
  &:hover { background: #f5f5f5; }
}
.user-avatar {
  background: linear-gradient(135deg, #FF6B35, #FF8C5A);
  color: #fff;
  font-weight: 600;
  font-size: 14px;
}
.user-name {
  font-size: 14px;
  color: #333;
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.user-arrow {
  color: #999;
  font-size: 12px;
}

// ── 内容区 ──
.main {
  background: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}
</style>
