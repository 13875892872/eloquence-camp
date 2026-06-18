const PENDING_KEY = 'pending_audio_uploads'

export function savePendingUpload(entry) {
  const list = uni.getStorageSync(PENDING_KEY) || []
  list.push({ ...entry, ts: Date.now() })
  uni.setStorageSync(PENDING_KEY, list)
}

export function getPendingUploads() {
  return uni.getStorageSync(PENDING_KEY) || []
}

export function removePendingUpload(index) {
  const list = getPendingUploads()
  list.splice(index, 1)
  uni.setStorageSync(PENDING_KEY, list)
}

export async function retryPendingUploads(uploadFn) {
  const list = getPendingUploads()
  if (!list.length) return 0
  let ok = 0
  for (let i = list.length - 1; i >= 0; i--) {
    const item = list[i]
    try {
      await uploadFn(item)
      removePendingUpload(i)
      ok++
    } catch (e) {
      /* keep for next retry */
    }
  }
  if (ok) uni.showToast({ title: `已恢复上传 ${ok} 条录音`, icon: 'none' })
  return ok
}
