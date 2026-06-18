/** H5 无微信订阅消息，安全降级为 no-op */
export function safeRequestSubscribe() {
  return Promise.resolve(null)
}
