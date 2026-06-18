<script setup>
import { onLaunch, onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/store/user'
import { BASE_API } from '@/api/request'

const userStore = useUserStore()
const H5_LOGIN_CODE = 'h5_browser_user'

onLaunch(() => {
  const savedToken = uni.getStorageSync('token')
  if (savedToken) {
    userStore.setToken(savedToken)
  }
  doLogin()
})

onShow(() => {
  console.log('App Show')
})

async function doLogin() {
  try {
    const resp = await uni.request({
      url: BASE_API + '/auth/wechat-login',
      method: 'POST',
      data: { code: H5_LOGIN_CODE },
      header: { 'Content-Type': 'application/json' }
    })

    if (resp.statusCode === 200 && resp.data.code === 200) {
      const { token, user, is_new_user } = resp.data.data
      userStore.setToken(token)
      userStore.setUser(user)
      uni.setStorageSync('token', token)
      console.log('H5 登录成功', user.nickname || '用户', is_new_user ? '(首次)' : '')
    } else {
      console.error('登录失败', resp.data)
    }
  } catch (e) {
    console.error('登录异常', e)
  }
}
</script>

<template>
  <view />
</template>

<style lang="scss">
@import '@/styles/global.scss';

/* H5：模拟手机宽度，居中展示 */
@media (min-width: 480px) {
  uni-page-body,
  body {
    background: #e8ecf4 !important;
  }
  uni-tabbar.uni-tabbar-bottom {
    max-width: 430px;
    left: 50% !important;
    transform: translateX(-50%);
  }
}
</style>
