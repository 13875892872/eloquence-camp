import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(uni.getStorageSync('token') || '')
  const userInfo = ref(null)

  function setToken(t) { token.value = t; uni.setStorageSync('token', t) }
  function setUser(u) { userInfo.value = u }
  function logout() { token.value = ''; userInfo.value = null; uni.removeStorageSync('token') }

  return { token, userInfo, setToken, setUser, logout }
})
