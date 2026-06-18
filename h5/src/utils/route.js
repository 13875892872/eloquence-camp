/**
 * 获取页面路由参数（兼容 H5 hash 模式下 onLoad 拿不到 query 的情况）
 */
export function getRouteParam(opt, key) {
  if (opt && opt[key] != null && opt[key] !== '') {
    return String(opt[key])
  }

  if (typeof window !== 'undefined') {
    try {
      const hash = window.location.hash || ''
      const hashQs = hash.includes('?') ? hash.split('?').slice(1).join('?') : ''
      const searchQs = (window.location.search || '').replace(/^\?/, '')
      const qs = hashQs || searchQs
      if (qs) {
        const val = new URLSearchParams(qs).get(key)
        if (val) return val
      }
    } catch (e) {
      console.warn('[route] parse query failed', e)
    }
  }

  try {
    const pages = getCurrentPages()
    const page = pages[pages.length - 1]
    const options = page?.$page?.options || page?.options || {}
    if (options[key] != null && options[key] !== '') {
      return String(options[key])
    }
  } catch (e) {
    console.warn('[route] getCurrentPages failed', e)
  }

  return null
}
