<template>
  <div>
    <h1 class="page-title">水权定额</h1>
    <p class="page-sub">按年度、地块或种植户分配用水定额，系统按已确认用水量计算已用与剩余</p>

    <div class="kpis four" style="margin-bottom:14px">
      <div class="kpi"><div class="lb">2026 年度定额总量</div><div class="vl">{{ num(sum.quota, 0) }}<small>m³</small></div></div>
      <div class="kpi"><div class="lb">已用水量</div><div class="vl">{{ num(sum.used, 0) }}<small>m³</small></div><div class="dt">使用率 {{ percent(sum.rate) }}</div></div>
      <div class="kpi"><div class="lb">剩余可用</div><div class="vl">{{ num(sum.remain, 0) }}<small>m³</small></div></div>
      <div class="kpi"><div class="lb">超额 / 余量不足</div><div class="vl" style="color:#B22B31">{{ sum.over }}<small>块</small></div><div class="dt warn">已触发加价计费</div></div>
    </div>

    <div class="panel">
      <div class="panel-hd">
        <span>定额分配表</span>
        <span style="font-weight:400;display:flex;gap:8px">
          <el-select v-model="query.year" size="small" style="width:110px" @change="search">
            <el-option label="2026 年度" :value="2026" />
            <el-option label="2025 年度" :value="2025" />
          </el-select>
          <el-select v-model="query.status" size="small" placeholder="全部状态" clearable style="width:130px" @change="search">
            <el-option label="正常" value="NORMAL" />
            <el-option label="余量不足" value="SHORT" />
            <el-option label="已超额" value="OVER" />
          </el-select>
          <el-button size="small" type="primary" @click="openAssign">分配定额</el-button>
        </span>
      </div>
      <div class="panel-bd flush">
        <div class="table-wrap">
          <el-table :data="rows" v-loading="loading" border stripe>
            <el-table-column prop="farmlandCode" label="地块编号" min-width="128" />
            <el-table-column prop="farmlandName" label="地块" min-width="130" />
            <el-table-column prop="farmerName" label="种植户" min-width="88" />
            <el-table-column prop="year" label="年度" min-width="70" align="center" />
            <el-table-column label="面积(亩)" min-width="92" align="right">
              <template #default="{ row }"><span class="num">{{ num(row.area, 2) }}</span></template>
            </el-table-column>
            <el-table-column label="定额(m³)" min-width="104" align="right">
              <template #default="{ row }"><span class="num">{{ num(row.quotaVolume, 2) }}</span></template>
            </el-table-column>
            <el-table-column label="已用(m³)" min-width="104" align="right">
              <template #default="{ row }"><span class="num">{{ num(row.usedVolume, 2) }}</span></template>
            </el-table-column>
            <el-table-column label="剩余(m³)" min-width="104" align="right">
              <template #default="{ row }">
                <span class="num" :style="{ color: Number(row.remainingVolume) < 0 ? '#B22B31' : '#1D2A33' }">{{ num(row.remainingVolume, 2) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="使用率" min-width="92" align="right">
              <template #default="{ row }">
                <span class="num" :style="{ color: row.usageRate > 100 ? '#B22B31' : (row.usageRate > 90 ? '#B4761E' : '#1D2A33') }">{{ percent(row.usageRate) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="状态" min-width="92">
              <template #default="{ row }"><span class="tag" :class="tagOf(row.status)">{{ text(row.status) }}</span></template>
            </el-table-column>
          </el-table>
        </div>
        <div class="pager">
          <el-pagination background layout="total, sizes, prev, pager, next" :total="total"
                         v-model:current-page="query.page" v-model:page-size="query.size"
                         :page-sizes="[10, 20, 50]" @current-change="load" @size-change="onSize" />
        </div>
      </div>
    </div>

    <el-dialog v-model="assignVisible" title="分配年度定额" width="480px">
      <el-form label-width="100px" label-position="left">
        <el-form-item label="地块" required>
          <el-select v-model="assign.farmlandId" filterable style="width:100%">
            <el-option v-for="f in farmlands" :key="f.id" :label="`${f.name}（${f.crop}）`" :value="f.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="年度">
          <el-input-number v-model="assign.year" :min="2024" :max="2030" style="width:100%" />
        </el-form-item>
        <el-form-item label="定额水量" required>
          <el-input-number v-model="assign.quotaVolume" :min="0" :precision="2" :step="100" style="width:100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="doAssign">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { num, percent, text, STATUS_TYPE } from '@/utils/format'

const rows = ref([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const assignVisible = ref(false)
const farmlands = ref([])
const query = reactive({ year: 2026, status: '', page: 1, size: 10 })
const assign = reactive({ farmlandId: null, year: 2026, quotaVolume: 4000 })

const sum = computed(() => {
  let quota = 0, used = 0, over = 0
  rows.value.forEach(r => {
    quota += Number(r.quotaVolume || 0)
    used += Number(r.usedVolume || 0)
    if (r.status === 'OVER' || r.status === 'SHORT') over++
  })
  return { quota, used, remain: quota - used, rate: quota ? (used / quota) * 100 : 0, over }
})

const tagOf = s => 'tag ' + (STATUS_TYPE[s] || 'info')

async function load() {
  loading.value = true
  try {
    const data = await request.get('/quota/page', { params: query })
    rows.value = data.records || []
    total.value = data.total || 0
  } finally { loading.value = false }
}
const search = () => { query.page = 1; load() }
const onSize = () => { query.page = 1; load() }

async function openAssign() {
  if (!farmlands.value.length) {
    const data = await request.get('/farmland/page', { params: { page: 1, size: 50 } })
    farmlands.value = data.records || []
  }
  Object.assign(assign, { farmlandId: farmlands.value[0]?.id || null, year: 2026, quotaVolume: 4000 })
  assignVisible.value = true
}

async function doAssign() {
  if (!assign.farmlandId) { ElMessage.warning('请选择地块'); return }
  saving.value = true
  try {
    await request.post('/quota/assign', assign)
    ElMessage.success('定额已保存')
    assignVisible.value = false
    load()
  } finally { saving.value = false }
}

onMounted(load)
</script>
