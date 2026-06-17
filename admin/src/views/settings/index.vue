<!-- 系统设置 → 自动跳转到修改密码页 -->
<template><div/></template>
<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
onMounted(() => useRouter().replace('/settings/password'))
</script>
