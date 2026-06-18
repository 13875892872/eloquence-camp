/**
 * uni.request 封装 — 自动注入Token / 统一错误处理
 */
// #ifdef MP-WEIXIN
const BASE_URL = 'http://192.168.1.234:5000/api'
// #endif

// #ifndef MP-WEIXIN
const BASE_URL = 'https://api.your-domain.com/api'
// #endif
const TIMEOUT = 8000

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
            uni.showToast({ title: '登录已过期，请重新打开', icon: 'none' })
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
