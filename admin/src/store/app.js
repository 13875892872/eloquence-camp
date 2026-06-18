import { defineStore } from 'pinia'

const COLLAPSE_KEY = 'admin_sidebar_collapsed'
const TABS_KEY = 'admin_visited_tabs'
const BREAKPOINT = 1200

const DEFAULT_TABS = [{ path: '/dashboard', title: '数据看板', affix: true }]

function loadTabs() {
  try {
    const raw = sessionStorage.getItem(TABS_KEY)
    if (raw) {
      const tabs = JSON.parse(raw)
      if (Array.isArray(tabs) && tabs.length) return tabs
    }
  } catch { /* ignore */ }
  return [...DEFAULT_TABS]
}

function saveTabs(tabs) {
  sessionStorage.setItem(TABS_KEY, JSON.stringify(tabs))
}

export function getAdminRole() {
  try {
    const info = JSON.parse(localStorage.getItem('admin_info') || '{}')
    return info.role || 'super_admin'
  } catch {
    return 'super_admin'
  }
}

export const useAppStore = defineStore('app', {
  state: () => ({
    isCollapse: localStorage.getItem(COLLAPSE_KEY) === '1',
    isMobileLayout: window.innerWidth < BREAKPOINT,
    adminRole: getAdminRole(),
    visitedTabs: loadTabs(),
  }),

  getters: {
    sidebarWidth: (s) => (s.isCollapse ? '64px' : '220px'),
  },

  actions: {
    toggleCollapse() {
      this.isCollapse = !this.isCollapse
      localStorage.setItem(COLLAPSE_KEY, this.isCollapse ? '1' : '0')
    },

    setCollapse(val) {
      this.isCollapse = val
      localStorage.setItem(COLLAPSE_KEY, val ? '1' : '0')
    },

    syncAdminRole() {
      this.adminRole = getAdminRole()
    },

    handleResize() {
      const narrow = window.innerWidth < BREAKPOINT
      this.isMobileLayout = narrow
      if (narrow) {
        this.isCollapse = true
      }
    },

    initResponsive() {
      this._onResize = () => this.handleResize()
      this.handleResize()
      window.addEventListener('resize', this._onResize)
    },

    destroyResponsive() {
      if (this._onResize) {
        window.removeEventListener('resize', this._onResize)
      }
    },

    addTab(route) {
      if (!route.meta?.title || route.path === '/login') return
      const exists = this.visitedTabs.find((t) => t.path === route.path)
      if (!exists) {
        this.visitedTabs.push({
          path: route.path,
          title: route.meta.title,
          affix: route.path === '/dashboard',
        })
        saveTabs(this.visitedTabs)
      }
    },

    closeTab(path, currentPath) {
      const idx = this.visitedTabs.findIndex((t) => t.path === path)
      if (idx < 0) return null
      const tab = this.visitedTabs[idx]
      if (tab.affix) return null
      this.visitedTabs.splice(idx, 1)
      saveTabs(this.visitedTabs)
      if (path === currentPath) {
        const next = this.visitedTabs[Math.max(0, idx - 1)]
        return next?.path || '/dashboard'
      }
      return null
    },
  },
})
