/** 安全调用订阅消息，避免开发者工具中 invalid tmplId 导致 timeout */
export function safeRequestSubscribe(tmplIds = []) {
  const ids = (tmplIds || []).filter(Boolean)
  if (!ids.length) return Promise.resolve(null)

  return Promise.race([
    uni.requestSubscribeMessage({ tmplIds: ids }),
    new Promise((_, reject) => setTimeout(() => reject(new Error('subscribe timeout')), 5000))
  ]).catch(() => null)
}
