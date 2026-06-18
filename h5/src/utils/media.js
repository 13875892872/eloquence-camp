import { BASE_API } from '@/api/request'

/** 将后端返回的音频/静态资源路径转为 H5 可播放的完整 URL */
export function resolveMediaUrl(path) {
  if (!path) return ''
  if (/^https?:\/\//i.test(path)) return path

  const normalized = path.startsWith('/') ? path : `/${path}`

  // 已是 /api/... 相对路径：开发环境走当前页面 origin（Vite 代理）
  if (normalized.startsWith('/api/')) {
    if (BASE_API.startsWith('http')) {
      const origin = BASE_API.replace(/\/api\/?$/, '')
      return origin + normalized
    }
    if (typeof window !== 'undefined' && window.location?.origin) {
      return window.location.origin + normalized
    }
    return normalized
  }

  // 其他相对路径（如 /static/demo/...）
  if (BASE_API.startsWith('http')) {
    const origin = BASE_API.replace(/\/api\/?$/, '')
    return origin + normalized
  }
  if (typeof window !== 'undefined' && window.location?.origin) {
    return window.location.origin + normalized
  }
  return normalized
}
