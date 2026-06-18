<template>
  <div class="settings-layout page-wrap">
    <PageHeader title="系统设置" desc="管理密码、存储与操作审计" />
    <div class="settings-body">
      <el-menu
        :default-active="route.path"
        router
        class="settings-nav"
      >
        <el-menu-item
          v-for="tab in tabs"
          :key="tab.path"
          :index="tab.path"
        >
          <el-icon><component :is="tab.icon" /></el-icon>
          <span>{{ tab.title }}</span>
        </el-menu-item>
      </el-menu>
      <div class="settings-content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import PageHeader from '@/components/PageHeader.vue'
import { getAdminRole } from '@/store/app'

const route = useRoute()
const role = getAdminRole()

const allTabs = [
  { path: '/settings/password', title: '修改密码', icon: 'Lock' },
  { path: '/settings/storage', title: '存储管理', icon: 'FolderOpened', roles: ['super_admin'] },
  { path: '/settings/logs', title: '操作日志', icon: 'Document', roles: ['super_admin'] },
]

const tabs = computed(() =>
  allTabs.filter((t) => !t.roles || t.roles.includes(role))
)
</script>

<style scoped lang="scss">
.settings-body {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}
.settings-nav {
  width: 180px;
  flex-shrink: 0;
  border-radius: var(--card-radius);
  border: 1px solid var(--border-color);
  overflow: hidden;
  background: #fff;
}
.settings-nav :deep(.el-menu-item) {
  height: 44px;
  border-radius: 0;
  margin: 0;
}
.settings-nav :deep(.el-menu-item.is-active) {
  background: var(--menu-active-bg);
  color: var(--el-color-primary);
  position: relative;
}
.settings-nav :deep(.el-menu-item.is-active::before) {
  content: '';
  position: absolute;
  left: 0;
  top: 10px;
  bottom: 10px;
  width: 3px;
  background: var(--el-color-primary);
}
.settings-content {
  flex: 1;
  min-width: 0;
}
@media (max-width: 768px) {
  .settings-body {
    flex-direction: column;
  }
  .settings-nav {
    width: 100%;
    display: flex;
  }
  .settings-nav :deep(.el-menu-item) {
    flex: 1;
    justify-content: center;
    margin: 0;
    border-radius: 0;
  }
}
</style>
