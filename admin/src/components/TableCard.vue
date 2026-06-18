<template>
  <el-card shadow="never" class="table-card">
    <template v-if="title || $slots.extra" #header>
      <div class="table-card-hd">
        <span>{{ title }}</span>
        <slot name="extra" />
      </div>
    </template>
    <div class="table-scroll">
      <slot />
    </div>
    <div v-if="$slots.footer" class="table-card-footer">
      <slot name="footer" />
    </div>
  </el-card>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
})
</script>

<style scoped lang="scss">
.table-card {
  border-radius: var(--card-radius);
  background: var(--content-bg);
  :deep(.el-card__body) {
    padding: 16px;
  }
}
.table-card-hd {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
}
.table-scroll {
  width: 100%;
  overflow-x: auto;
}
.table-card-footer {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
