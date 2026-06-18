<template>
  <div class="page-header" v-if="title || $slots.extra">
    <div class="ph-left">
      <el-button v-if="showBack" text class="ph-back" @click="goBack">← 返回</el-button>
      <div>
        <h2 v-if="title" class="ph-title">{{ title }}</h2>
        <p v-if="desc" class="ph-desc">{{ desc }}</p>
      </div>
    </div>
    <div v-if="$slots.extra" class="ph-extra">
      <slot name="extra" />
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  title: { type: String, default: '' },
  desc: { type: String, default: '' },
  showBack: { type: Boolean, default: false },
  backTo: { type: String, default: '' },
})

const router = useRouter()

function goBack() {
  if (props.backTo) router.push(props.backTo)
  else router.back()
}
</script>

<style scoped lang="scss">
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
  gap: 16px;
}
.ph-left {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}
.ph-back {
  margin-top: 2px;
  padding-left: 0;
}
.ph-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.4;
}
.ph-desc {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 4px;
}
.ph-extra {
  flex-shrink: 0;
}
</style>
