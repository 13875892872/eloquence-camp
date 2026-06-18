<template>
  <el-card shadow="never" class="chart-card" :class="{ 'no-margin': noMargin }">
    <template v-if="title || $slots.extra" #header>
      <div class="chart-card-hd">
        <span class="chart-card-title">{{ title }}</span>
        <slot name="extra" />
      </div>
    </template>
    <div v-loading="loading" class="chart-card-body" :style="{ height: height + 'px' }">
      <slot />
    </div>
  </el-card>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
  height: { type: Number, default: 260 },
  loading: { type: Boolean, default: false },
  noMargin: { type: Boolean, default: false },
})
</script>

<style scoped lang="scss">
.chart-card {
  border-radius: var(--card-radius);
  background: var(--content-bg);
  &.no-margin { margin-bottom: 0; }
}
.chart-card-hd {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}
.chart-card-title {
  color: var(--text-primary);
}
.chart-card-body {
  width: 100%;
}
</style>
