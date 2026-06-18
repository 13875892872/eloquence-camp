<template>
  <el-container class="app-layout" :style="{ '--sidebar-width': appStore.sidebarWidth }">
    <el-aside :width="appStore.sidebarWidth" class="aside" :class="{ 'is-collapse': appStore.isCollapse }">
      <div class="brand" @click="router.push('/dashboard')">
        <div class="brand-icon">🎤</div>
        <div v-if="!appStore.isCollapse" class="brand-text">
          <div class="brand-title">口才训练营</div>
          <div class="brand-sub">管理后台</div>
        </div>
      </div>

      <el-menu
        :default-active="activeMenu"
        router
        :collapse="appStore.isCollapse"
        background-color="#ffffff"
        text-color="#606266"
        active-text-color="#409eff"
        class="side-menu"
      >
        <template v-for="item in visibleMenus" :key="item.path || item.index">
          <el-menu-item v-if="item.type === 'item'" :index="item.path">
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ item.title }}</span>
          </el-menu-item>
          <el-sub-menu v-else :index="item.index">
            <template #title>
              <el-icon><component :is="item.icon" /></el-icon>
              <span>{{ item.title }}</span>
            </template>
            <el-menu-item
              v-for="child in item.children"
              :key="child.path"
              :index="child.path"
            >
              {{ child.title }}
            </el-menu-item>
          </el-sub-menu>
        </template>
      </el-menu>
    </el-aside>

    <el-container class="main-container">
      <el-header class="header-wrap">
        <div class="header-top">
          <div class="header-left">
            <el-icon class="collapse-btn" @click="appStore.toggleCollapse()" :size="18">
              <Fold v-if="!appStore.isCollapse" /><Expand v-else />
            </el-icon>
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item
                v-for="(bc, i) in breadcrumbs"
                :key="bc.path + bc.title"
                :to="i < breadcrumbs.length - 1 && bc.path ? { path: bc.path } : undefined"
              >
                {{ bc.title }}
              </el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div class="header-right">
            <el-dropdown trigger="click" @command="handleCommand">
              <div class="user-area">
                <el-avatar :size="30" class="user-avatar">{{ adminInitial }}</el-avatar>
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
        </div>

        <div class="tabs-bar">
          <div
            v-for="tab in appStore.visitedTabs"
            :key="tab.path"
            class="tab-item"
            :class="{ active: route.path === tab.path }"
            @click="goTab(tab.path)"
          >
            <span class="tab-title">{{ tab.title }}</span>
            <el-icon
              v-if="!tab.affix"
              class="tab-close"
              @click.stop="closeTab(tab.path)"
            ><Close /></el-icon>
          </div>
        </div>
      </el-header>

      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { sideMenus } from '@/router/menus'
import { filterMenusByRole } from '@/utils/menu'
import { useAppStore } from '@/store/app'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const visibleMenus = computed(() => filterMenusByRole(sideMenus, appStore.adminRole))

const adminName = computed(() => {
  const info = localStorage.getItem('admin_info')
  try { return JSON.parse(info)?.username || '管理员' }
  catch { return '管理员' }
})

const adminInitial = computed(() => adminName.value.charAt(0).toUpperCase())

const activeMenu = computed(() => {
  const p = route.path
  if (/^\/users\/\d+/.test(p)) return '/users'
  if (p.startsWith('/settings')) return '/settings'
  if (p.startsWith('/training/recommend')) return '/training/recommend'
  if (p.startsWith('/training')) return '/training'
  if (p.startsWith('/checkin/tasks')) return '/checkin/tasks'
  if (p.startsWith('/checkin/growth')) return '/checkin/growth'
  return p
})

const breadcrumbs = computed(() => {
  const items = []
  let accPath = ''
  for (const r of route.matched) {
    if (!r.meta?.title || r.meta?.hidden) continue
    if (r.meta.parent) {
      items.push({ title: r.meta.parent, path: '' })
    }
    if (r.path) {
      accPath = r.path.startsWith('/')
        ? r.path
        : `${accPath}/${r.path}`.replace(/\/+/g, '/')
    }
    items.push({ title: r.meta.title, path: accPath || route.path })
  }
  return items
})

function goTab(path) {
  if (route.path !== path) router.push(path)
}

function closeTab(path) {
  const next = appStore.closeTab(path, route.path)
  if (next) router.push(next)
}

function handleCommand(cmd) {
  if (cmd === 'password') {
    router.push('/settings/password')
  } else if (cmd === 'logout') {
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_info')
    appStore.syncAdminRole()
    router.push('/login')
  }
}

watch(
  () => route.path,
  () => appStore.addTab(route),
  { immediate: true }
)

onMounted(() => {
  appStore.syncAdminRole()
  appStore.initResponsive()
})

onUnmounted(() => {
  appStore.destroyResponsive()
})
</script>

<style scoped lang="scss">
.app-layout {
  height: 100vh;
  --sidebar-width: 210px;
}

.aside {
  background: var(--sidebar-bg);
  border-right: 1px solid var(--sidebar-border);
  display: flex;
  flex-direction: column;
  transition: width 0.28s;
  overflow: hidden;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px;
  cursor: pointer;
  border-bottom: 1px solid var(--border-light);
  min-height: 56px;
  box-sizing: border-box;
  flex-shrink: 0;
}
.brand-icon {
  width: 32px;
  height: 32px;
  background: var(--el-color-primary-light-9);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 18px;
  line-height: 1;
}
.brand-text { line-height: 1.3; min-width: 0; }
.brand-title {
  color: var(--text-primary);
  font-size: 15px;
  font-weight: 600;
  white-space: nowrap;
}
.brand-sub {
  color: var(--text-muted);
  font-size: 11px;
  white-space: nowrap;
}

.side-menu {
  flex: 1;
  border-right: none;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 8px 0;
}
.side-menu :deep(.el-menu-item),
.side-menu :deep(.el-sub-menu__title) {
  height: 44px;
  line-height: 44px;
  margin: 2px 8px;
  border-radius: 4px;
}
.side-menu :deep(.el-menu-item.is-active) {
  background: var(--menu-active-bg) !important;
  color: var(--el-color-primary) !important;
  font-weight: 500;
  position: relative;
}
.side-menu :deep(.el-menu-item.is-active::before) {
  content: '';
  position: absolute;
  left: 0;
  top: 10px;
  bottom: 10px;
  width: 3px;
  background: var(--el-color-primary);
  border-radius: 0 2px 2px 0;
}
.side-menu :deep(.el-sub-menu .el-menu-item) {
  height: 40px;
  line-height: 40px;
  min-width: auto;
}
.side-menu :deep(.el-sub-menu .el-menu-item.is-active) {
  background: var(--menu-active-bg) !important;
  color: var(--el-color-primary) !important;
}
.side-menu :deep(.el-sub-menu .el-menu) {
  background: transparent !important;
}

.main-container {
  min-width: 0;
  background: var(--page-bg);
}

.header-wrap {
  height: auto !important;
  padding: 0;
  background: #fff;
  border-bottom: 1px solid var(--border-color);
  z-index: 10;
}

.header-top {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}
.collapse-btn {
  cursor: pointer;
  color: var(--text-secondary);
  flex-shrink: 0;
  padding: 4px;
  border-radius: 4px;
  &:hover {
    color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
  }
}

.header-right {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}
.user-area {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px 4px 4px;
  border-radius: 4px;
  transition: background 0.2s;
  &:hover { background: var(--el-fill-color-light); }
}
.user-avatar {
  background: var(--el-color-primary);
  color: #fff;
  font-weight: 600;
  font-size: 13px;
}
.user-name {
  font-size: 13px;
  color: var(--text-primary);
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.user-arrow {
  color: var(--text-muted);
  font-size: 12px;
}

.tabs-bar {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 0 12px 6px;
  overflow-x: auto;
  flex-shrink: 0;
}
.tab-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px 12px;
  font-size: 13px;
  color: var(--text-secondary);
  background: #f4f4f5;
  border-radius: 4px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
  user-select: none;
  &:hover:not(.active) {
    color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
  }
  &.active {
    background: var(--el-color-primary);
    color: #fff;
  }
}
.tab-close {
  font-size: 12px;
  opacity: 0.75;
  border-radius: 50%;
  &:hover { opacity: 1; }
}
.tab-item.active .tab-close:hover {
  background: rgba(255, 255, 255, 0.2);
}

.main {
  padding: 16px;
  overflow-y: auto;
}

:deep(.el-breadcrumb) {
  font-size: 13px;
}
:deep(.el-breadcrumb__inner) {
  color: var(--text-muted);
  font-weight: 400;
}
:deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: var(--text-primary);
}

@media (max-width: 1200px) {
  .main { padding: 12px; }
  .user-name { display: none; }
}
</style>
