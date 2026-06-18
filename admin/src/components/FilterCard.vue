<template>
  <el-card shadow="never" class="filter-card">
    <el-row :gutter="12" align="middle">
      <el-col :span="18">
        <slot />
      </el-col>
      <el-col :span="6" class="filter-actions">
        <el-button type="primary" @click="$emit('search')">查询</el-button>
        <el-button @click="$emit('reset')">重置</el-button>
        <slot name="actions" />
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup>
defineEmits(['search', 'reset'])
</script>

<style scoped lang="scss">
.filter-card {
  margin-bottom: 16px;
  border-radius: var(--card-radius);
  background: var(--content-bg);
  :deep(.el-card__body) {
    padding: 16px;
  }
}
.filter-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
