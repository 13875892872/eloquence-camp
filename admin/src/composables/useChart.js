import { onMounted, onUnmounted, shallowRef, watch } from 'vue'

const EMPTY_OPTION = {
  title: {
    text: '暂无数据',
    left: 'center',
    top: 'center',
    textStyle: { color: '#999', fontSize: 14, fontWeight: 'normal' },
  },
}

let echartsLib = null

async function getEcharts() {
  if (!echartsLib) {
    echartsLib = await import('echarts')
  }
  return echartsLib
}

export function useChart(containerRef) {
  const chart = shallowRef(null)
  let observer = null

  async function ensureInstance() {
    if (!containerRef.value) return null
    const echarts = await getEcharts()
    if (!chart.value) {
      chart.value = echarts.init(containerRef.value)
    }
    return chart.value
  }

  async function setOption(option, notMerge = false) {
    const inst = await ensureInstance()
    if (!inst) return
    if (!option || (Array.isArray(option.series) && option.series.length === 0)) {
      await showEmpty()
      return
    }
    inst.setOption(option, notMerge)
  }

  async function showEmpty() {
    const inst = await ensureInstance()
    if (!inst) return
    inst.clear()
    inst.setOption(EMPTY_OPTION)
  }

  function resize() {
    chart.value?.resize()
  }

  function dispose() {
    observer?.disconnect()
    observer = null
    chart.value?.dispose()
    chart.value = null
  }

  onMounted(() => {
    if (containerRef.value && typeof ResizeObserver !== 'undefined') {
      observer = new ResizeObserver(() => resize())
      observer.observe(containerRef.value)
    }
    window.addEventListener('resize', resize)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', resize)
    dispose()
  })

  watch(() => containerRef.value, (el, prev) => {
    if (prev && observer) observer.unobserve(prev)
    if (el && observer) observer.observe(el)
    if (!el) dispose()
  })

  return { setOption, showEmpty, resize, dispose }
}
