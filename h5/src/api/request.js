/**
 * uni.request 封装 — H5 版
 * 开发：Vite 代理 /api；手机访问局域网 IP 时自动指向同主机 5000 端口
 */
function resolveBaseUrl() {
  const env = import.meta.env.VITE_API_BASE
  if (env && env.startsWith('http')) return env.replace(/\/$/, '')

  if (typeof window !== 'undefined') {
    const { hostname, port, protocol } = window.location
    // 手机通过局域网 IP 访问 dev/preview，直连后端（Vite 代理仅在本机 loopback 有效）
    if (hostname !== 'localhost' && hostname !== '127.0.0.1' && protocol.startsWith('http')) {
      return `${protocol}//${hostname}:5000/api`
    }
    // 本地 dev 走 Vite 代理
    if (import.meta.env.DEV && (port === '5173' || port === '')) {
      return '/api'
    }
  }

  return env || '/api'
}

const BASE_URL = resolveBaseUrl()
const TIMEOUT = 15000

function request(options = {}) {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token') || ''

    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...options.header
      },
      timeout: options.timeout || TIMEOUT,
      success: (res) => {
        const { statusCode, data } = res
        if (statusCode === 200) {
          if (data.code === 200) {
            resolve(data.data)
          } else if (data.code === 401) {
            uni.removeStorageSync('token')
            uni.showToast({ title: '登录已过期，请刷新页面', icon: 'none' })
            reject(data)
          } else {
            uni.showToast({ title: data.message || '请求失败', icon: 'none' })
            reject(data)
          }
        } else {
          uni.showToast({ title: '网络异常', icon: 'none' })
          reject({ code: statusCode, message: '网络异常' })
        }
      },
      fail: (err) => {
        console.error('[api] request fail', options.url, err)
        uni.showToast({ title: '网络连接失败', icon: 'none' })
        reject(err)
      }
    })
  })
}

export const BASE_API = BASE_URL

export default {
  get: (url, params, opts) => {
    if (params) {
      const qs = Object.entries(params)
        .filter(([, v]) => v !== undefined && v !== '')
        .map(([k, v]) => encodeURIComponent(k) + '=' + encodeURIComponent(v))
        .join('&')
      if (qs) url += '?' + qs
    }
    return request({ ...opts, url, method: 'GET' })
  },
  post: (url, data, opts) => request({ ...opts, url, method: 'POST', data }),
  put: (url, data, opts) => request({ ...opts, url, method: 'PUT', data }),
  delete: (url, data, opts) => request({ ...opts, url, method: 'DELETE', data }),
  patch: (url, data, opts) => request({ ...opts, url, method: 'PATCH', data })
}
