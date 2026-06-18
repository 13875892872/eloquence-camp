<template>
<div class="ai-page">
  <!-- Qwen 文案生成 -->
  <el-card shadow="never" class="cfg-card">
    <template #header>
      <div class="card-header">
        <span>🤖 Qwen 文案生成配置</span>
        <el-tag size="small" type="success" effect="plain">已配置</el-tag>
      </div>
    </template>
    <el-row :gutter="24">
      <el-col :span="8">
        <el-form-item label="模型版本">
          <el-tooltip content="Max最强/Flash最快/Plus均衡/Turbo轻量" placement="top">
            <el-select v-model="f.text_model" style="width:100%">
              <el-option label="Qwen3-Max（最强大）" value="qwen3-max"/>
              <el-option label="Qwen3-Flash（最快）" value="qwen3-flash"/>
              <el-option label="Qwen-Plus（均衡）" value="qwen-plus"/>
              <el-option label="Qwen-Turbo（轻量）" value="qwen-turbo"/>
            </el-select>
          </el-tooltip>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="创意度 Temperature">
          <el-slider v-model="f.text_temperature" :min="0.1" :max="1.0" :step="0.1"
            :marks="{0.1:'严谨',0.5:'均衡',1.0:'创意'}" show-input :format-tooltip="v=>v.toFixed(1)"/>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="最大输出 Token">
          <el-input-number v-model="f.text_max_tokens" :min="100" :max="4000" :step="100" style="width:100%"/>
        </el-form-item>
      </el-col>
    </el-row>
  </el-card>

  <!-- 免费次数 -->
  <el-card shadow="never" class="cfg-card">
    <template #header>
      <div class="card-header">
        <span>🎫 免费次数策略</span>
        <el-tag size="small" type="warning" effect="plain">可调整</el-tag>
      </div>
    </template>
    <el-row :gutter="24">
      <el-col :span="8">
        <el-form-item label="新用户每日次数">
          <el-input-number v-model="f.new_user_daily" :min="0" :max="100" style="width:100%"/>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="打卡额外奖励次数">
          <el-input-number v-model="f.checkin_bonus" :min="0" :max="10" style="width:100%"/>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="每日重置时间">
          <el-time-picker v-model="resetTime" format="HH:mm" value-format="HH:mm" placeholder="00:00" style="width:100%"/>
        </el-form-item>
      </el-col>
    </el-row>
  </el-card>

  <!-- 语音评测权重 -->
  <el-card shadow="never" class="cfg-card">
    <template #header>
      <div class="card-header">
        <span>🎙️ 语音评测权重配置</span>
        <el-tag size="small" :type="weightTotal===100 ? 'success' : 'danger'" effect="plain">
          {{ weightTotal === 100 ? '权重正常' : '合计≠100%' }}
        </el-tag>
      </div>
    </template>
    <el-row :gutter="24">
      <el-col :span="13">
        <el-form-item label="发音准确度"><el-slider v-model="f.weight_pronunciation" :min="0" :max="100" show-input/></el-form-item>
        <el-form-item label="流利度"><el-slider v-model="f.weight_fluency" :min="0" :max="100" show-input/></el-form-item>
        <el-form-item label="完整度"><el-slider v-model="f.weight_completeness" :min="0" :max="100" show-input/></el-form-item>
        <el-form-item label="内容质量"><el-slider v-model="f.weight_content" :min="0" :max="100" show-input/></el-form-item>
        <el-form-item label="表现力"><el-slider v-model="f.weight_expressiveness" :min="0" :max="100" show-input/></el-form-item>
        <el-form-item label="最低通过分数"><el-input-number v-model="f.min_pass_score" :min="0" :max="100" style="width:100%"/></el-form-item>
      </el-col>
      <!-- 权重分布预览 -->
      <el-col :span="11">
        <div class="weight-preview">
          <div class="weight-title">权重分布预览</div>
          <div class="weight-chart">
            <div class="donut-ring">
              <svg viewBox="0 0 120 120">
                <circle cx="60" cy="60" r="50" fill="none" stroke="#eee" stroke-width="12"/>
                <template v-for="(seg,i) in weightSegments" :key="i">
                  <circle cx="60" cy="60" r="50" fill="none"
                    :stroke="seg.color" stroke-width="12"
                    :stroke-dasharray="`${seg.pct*3.14} ${314-seg.pct*3.14}`"
                    :stroke-dashoffset="seg.offset"
                    transform="rotate(-90 60 60)"
                    style="transition: all 0.5s"/>
                </template>
                <text x="60" y="56" text-anchor="middle" font-size="14" fill="#333" font-weight="bold">{{weightTotal}}%</text>
                <text x="60" y="72" text-anchor="middle" font-size="9" fill="#999">权重合计</text>
              </svg>
            </div>
            <div class="weight-legend">
              <span v-for="(seg,i) in weightSegments" :key="i" class="legend-item">
                <i :style="{background:seg.color}"></i>{{seg.name}}:{{seg.value}}%
              </span>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </el-card>

  <!-- 保存按钮 — sticky 底部 -->
  <div class="save-bar">
    <el-button type="primary" size="large" @click="save" :loading="saving" class="save-btn">
      💾 保存全部配置
    </el-button>
  </div>
</div>
</template>

<script setup>
import {reactive,onMounted,ref,computed} from 'vue';import {ElMessage} from 'element-plus';import request from '@/api/request'
const saving=ref(false)
const resetTime=ref(new Date(0,0,0,0,0))

const def={text_model:'qwen-plus',text_temperature:0.7,text_max_tokens:2000,new_user_daily:3,checkin_bonus:1,reset_hour:'00:00',weight_pronunciation:30,weight_fluency:25,weight_completeness:20,weight_content:15,weight_expressiveness:10,min_pass_score:60}
const f=reactive({...def})

const weightTotal = computed(() =>
  f.weight_pronunciation + f.weight_fluency + f.weight_completeness +
  f.weight_content + f.weight_expressiveness
)

const weightSegments = computed(() => {
  const weights = [
    { name:'发音', value:f.weight_pronunciation, color:'#FF6B35' },
    { name:'流利', value:f.weight_fluency, color:'#1890FF' },
    { name:'完整', value:f.weight_completeness, color:'#52C41A' },
    { name:'内容', value:f.weight_content, color:'#722ED1' },
    { name:'表现', value:f.weight_expressiveness, color:'#FAAD14' },
  ]
  let offset = 0
  return weights.map(w => {
    const pct = w.value / 100
    const seg = { ...w, pct, offset: -(offset * 3.14) }
    offset += pct
    return seg
  })
})

async function load(){
  try{const d=await request.get('/admin/ai-config');Object.assign(f,d)
    if(f.reset_hour){const [h,m]=f.reset_hour.split(':');resetTime.value=new Date(0,0,0,+h,+m)}
  }catch(e){}
}
async function save(){
  saving.value=true
  // 将 time-picker 值同步回字符串
  const h=String(resetTime.value.getHours()).padStart(2,'0')
  const m=String(resetTime.value.getMinutes()).padStart(2,'0')
  f.reset_hour = h+':'+m
  try {
    await request.put('/admin/ai-config', { ...f })
    ElMessage.success('AI配置已保存')
  } catch (e) {
    ElMessage.error('AI配置保存失败')
  }
  finally{saving.value=false}
}
onMounted(load)
</script>

<style scoped>
.ai-page{padding:0;padding-bottom:60px}
.cfg-card{margin-bottom:16px;border-radius:10px}
.card-header{display:flex;justify-content:space-between;align-items:center;font-weight:600}
.weight-preview{background:#fafafa;border-radius:12px;padding:20px;text-align:center}
.weight-title{font-size:14px;font-weight:600;color:#333;margin-bottom:12px}
.weight-chart{display:flex;align-items:center;gap:20px}
.donut-ring{width:120px;height:120px;flex-shrink:0}
.weight-legend{display:flex;flex-direction:column;gap:6px;text-align:left}
.legend-item{font-size:12px;color:#666;display:flex;align-items:center;gap:6px}
.legend-item i{display:inline-block;width:10px;height:10px;border-radius:2px}
.save-bar{position:fixed;bottom:0;left:var(--sidebar-width,220px);right:0;background:#fff;border-top:1px solid #eee;padding:14px 24px;display:flex;justify-content:flex-end;z-index:100;box-shadow:0 -2px 8px rgba(0,0,0,0.06);transition:left .3s}
.save-btn{padding:12px 40px;font-size:16px}
</style>
