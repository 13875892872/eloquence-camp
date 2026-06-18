<template>
  <image
    class="app-icon"
    :class="[`app-icon--${size}`, { 'app-icon--active': active }]"
    :src="src"
    mode="aspectFit"
  />
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: { type: String, required: true },
  size: { type: String, default: 'md' }, // sm | md | lg
  active: { type: Boolean, default: false }
})

const src = computed(() => `/static/icons/${props.name}.png`)
</script>

<style scoped>
.app-icon { display: block; flex-shrink: 0; }
.app-icon--sm { width: 36rpx; height: 36rpx; }
.app-icon--md { width: 48rpx; height: 48rpx; }
.app-icon--lg { width: 64rpx; height: 64rpx; }
.app-icon--xl { width: 80rpx; height: 80rpx; }
</style>
