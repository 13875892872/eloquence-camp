/** 计算页面可用滚动区域高度（px），避免 scroll-view 高度为 0 */
export function getScrollHeight(extraTopPx = 100) {
  try {
    const win = uni.getWindowInfo()
    const safeBottom = win.safeAreaInsets?.bottom || 0
    return Math.max(300, win.windowHeight - extraTopPx - safeBottom)
  } catch (e) {
    return 500
  }
}
