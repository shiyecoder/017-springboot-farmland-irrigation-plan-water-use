<template>
  <div>
    <h1 class="page-title">灌溉计划编制</h1>
    <p class="page-sub">按水源可用量、渠道容量与作物阶段编排时段；同一闸口重叠任务由后端容量校验拦截</p>

    <div class="panel">
      <div class="panel-bd">
        <div class="filters">
          <div class="quick">
            <span v-for="q in quicks" :key="q.v" :class="{ on: query.status === q.v }" @click="quick(q.v)">{{ q.t }}</span>
          </div>
          <el-select v-model="query.canalId" placeholder="全部渠道" clearable>
            <el-option v-for="c in canals" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
          <el-date-picker v-model="query.date" type="date" value-format="YYYY-MM-DD" placeholder="计划日期" style="width:170px" />
          <el-input v-model="query.keyword" placeholder="计划编号" clearable @keyup.enter="search" />
          <el-button type="primary" @click="search">查询</el-button>
          <el-button type="primary" style="margin-left:auto" @click="openCreate">新建计划</el-button>
        </div>
        <div class="notice" v-if="conflicts.length">
          ⚠ {{ conflicts.length }} 条计划存在闸口容量冲突（状态标记为「容量冲突」），请调整时段或闸口后重新提交审批。
        </div>
        <div class="table-wrap">
          <el-table :data="rows" v-loading="loading" border stripe>
            <el-table-column prop="code" label="计划编号" min-width="150" />
            <el-table-column prop="farmlandName" label="地块" min-width="130" />
            <el-table-column label="作物/阶段" min-width="118">
              <template #default="{ row }">{{ row.crop }} / {{ row.growthStage }}</template>
            </el-table-column>
            <el-table-column label="渠道·闸口" min-width="170">
              <template #default="{ row }">{{ row.canalName }} · {{ row.gateName }}</template>
            </el-table-column>
            <el-table-column label="计划时段" min-width="196">
              <template #default="{ row }">{{ formatTime(row.planStart) }} ~ {{ formatTime(row.planEnd).slice(11) }}</template>
            </el-table-column>
            <el-table-column label="计划水量(m³)" min-width="116" align="right">
              <template #default="{ row }"><span class="num">{{ num(row.planVolume, 1) }}</span></template>
            </el-table-column>
            <el-table-column label="优先级" min-width="82">
              <template #default="{ row }">
                <span class="tag" :class="row.priority === 'HIGH' ? 'bad' : (row.priority === 'LOW' ? 'info' : 'blue')">{{ PRIORITY[row.priority] }}</span>
              </template>
            </el-table-column>
            <el-table-column label="状态" min-width="96">
              <template #default="{ row }"><span class="tag" :class="tagOf(row.status)">{{ text(row.status) }}</span></template>
            </el-table-column>
            <el-table-column label="操作" min-width="150" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="openDetail(row)">详情</el-button>
                <el-button v-if="nextAction(row.status)" link type="primary" @click="transition(row)">{{ nextAction(row.status).label }}</el-button>
              </template>
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

    <div class="panel">
      <div class="panel-hd"><span>日历排程 · 按渠道</span><span style="font-weight:400;font-size:12.5px;color:var(--text-2)">点击行可查看当日计划</span></div>
      <div class="panel-bd flush">
        <div class="table-wrap">
          <el-table :data="calendar" border size="small">
            <el-table-column prop="slot" label="时段" min-width="110" />
            <el-table-column v-for="c in calendarCanals" :key="c" :label="c" min-width="180">
              <template #default="{ row }">
                <span v-for="p in row[c] || []" :key="p.code" class="tag" :class="tagOf(p.status)" style="margin:1px 2px 1px 0">
                  {{ p.farmlandName }} {{ num(p.planVolume, 0) }}
                </span>
                <span v-if="!(row[c] || []).length" style="color:#B6C4D0">—</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>

    <el-dialog v-model="createVisible" title="新建灌溉计划" width="560px">
      <el-form :model="form" label-width="110px" label-position="left">
        <el-form-item label="地块" required>
          <el-select v-model="form.farmlandId" filterable style="width:100%" @change="onFarmland">
            <el-option v-for="f in farmlands" :key="f.id" :label="`${f.name}（${f.crop} ${f.growthStage}）`" :value="f.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="闸口" required>
          <el-select v-model="form.gateId" filterable style="width:100%">
            <el-option v-for="g in gates" :key="g.id" :label="`${g.name}（设计 ${num(g.designFlow, 2)} m³/s · ${g.status === 'OPEN' ? '开启' : '不可用'}）`" :value="g.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间" required>
          <el-date-picker v-model="form.planStart" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width:100%" />
        </el-form-item>
        <el-form-item label="结束时间" required>
          <el-date-picker v-model="form.planEnd" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width:100%" />
        </el-form-item>
        <el-form-item label="计划水量" required>
          <el-input-number v-model="form.planVolume" :min="1" :precision="1" :step="100" style="width:100%" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-radio-group v-model="form.priority">
            <el-radio value="HIGH">高</el-radio>
            <el-radio value="NORMAL">中</el-radio>
            <el-radio value="LOW">低</el-radio>
          </el-radio-group>
        </el-form-item>
        <div class="notice info" style="margin:0">
          提交时会按「计划水量 ÷ 时段秒数」折算流量，与同一闸口重叠计划累加后比对设计流量，超出即拒绝。
        </div>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存并提交审批</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="detailVisible" title="计划详情" size="560px">
      <template v-if="detail.id">
        <div class="dh">
          <div><b>{{ detail.code }}</b>
            <span class="tag" :class="tagOf(detail.status)" style="margin-left:8px">{{ text(detail.status) }}</span>
            <div class="dh-sub">{{ detail.farmlandName }} · {{ detail.canalName }} · {{ detail.gateName }}</div>
          </div>
        </div>
        <dl>
          <div class="kv"><dt>计划时段</dt><dd>{{ formatTime(detail.planStart) }} ~ {{ formatTime(detail.planEnd) }}</dd></div>
          <div class="kv"><dt>计划水量</dt><dd>{{ num(detail.planVolume, 2) }} m³</dd></div>
          <div class="kv"><dt>调度员</dt><dd>{{ detail.dispatcherName || '—' }}</dd></div>
          <div class="kv"><dt>关联任务</dt><dd>{{ (detail.tasks || []).map(t => t.code).join('、') || '尚未下达' }}</dd></div>
          <div class="kv" v-if="detail.rejectReason"><dt>驳回原因</dt><dd>{{ detail.rejectReason }}</dd></div>
        </dl>
        <h4 class="sub-h">操作时间轴</h4>
        <el-timeline>
          <el-timeline-item v-for="l in detail.timeline || []" :key="l.id" :timestamp="formatTime(l.createTime)">
            {{ l.action }}<span v-if="l.reason"> · {{ l.reason }}</span>
            <div style="font-size:12px;color:#93A3B0">{{ l.operatorName }} {{ l.beforeStatus ? `${l.beforeStatus} → ${l.afterStatus}` : '' }}</div>
          </el-timeline-item>
        </el-timeline>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { formatTime, num, text, PRIORITY, STATUS_TYPE } from '@/utils/format'

const rows = ref([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const createVisible = ref(false)
const detailVisible = ref(false)
const detail = reactive({})
const farmlands = ref([])
const gates = ref([])
const canals = ref([])

const quicks = [
  { t: '全部', v: '' }, { t: '待我处理', v: 'AUDITING' }, { t: '处理中', v: 'EXECUTING' },
  { t: '已完成', v: 'ARCHIVED' }, { t: '异常', v: 'CONFLICT' }
]
const query = reactive({ status: '', canalId: null, date: '2026-10-31', keyword: '', page: 1, size: 10 })
const form = reactive({ farmlandId: null, gateId: null, canalId: null, planStart: '', planEnd: '', planVolume: 1200, priority: 'NORMAL' })

const conflicts = computed(() => rows.value.filter(r => r.status === 'CONFLICT'))
const tagOf = s => 'tag ' + (STATUS_TYPE[s] || 'info')

// 每个状态只有一个「下一节点」主操作，避免行内按钮泛滥
function nextAction(s) {
  const map = {
    DRAFT: { label: '提交审批', target: 'AUDITING' },
    AUDITING: { label: '审批通过', target: 'ISSUED' },
    EXECUTING: { label: '转用量确认', target: 'CONFIRMING' },
    CONFIRMING: { label: '归档', target: 'ARCHIVED' }
  }
  return map[s]
}

const calendarCanals = computed(() => [...new Set(rows.value.map(r => r.canalName))].slice(0, 4))
const calendar = computed(() => {
  const slots = ['00:00–06:00', '06:00–10:00', '10:00–14:00', '14:00–18:00', '18:00–24:00']
  return slots.map((slot, i) => {
    const row = { slot }
    calendarCanals.value.forEach(c => {
      row[c] = rows.value.filter(r => r.canalName === c && Number(String(r.planStart).slice(11, 13)) >= i * 6 - 2 && Number(String(r.planStart).slice(11, 13)) < i * 6 + 6)
    })
    return row
  })
})

async function load() {
  loading.value = true
  try {
    const data = await request.get('/plan/page', { params: query })
    rows.value = data.records || []
    total.value = data.total || 0
  } finally { loading.value = false }
}
const search = () => { query.page = 1; load() }
const onSize = () => { query.page = 1; load() }
const quick = v => { query.status = v; query.page = 1; load() }

async function loadBase() {
  const f = await request.get('/farmland/page', { params: { page: 1, size: 50 } })
  farmlands.value = f.records || []
  gates.value = await request.get('/base/gates')
  canals.value = await request.get('/base/canals')
}

async function openCreate() {
  if (!farmlands.value.length) await loadBase()
  Object.assign(form, {
    farmlandId: farmlands.value[0]?.id || null, gateId: gates.value[0]?.id || null,
    canalId: null, planStart: '2026-11-01 08:00:00', planEnd: '2026-11-01 12:00:00',
    planVolume: 1200, priority: 'NORMAL'
  })
  createVisible.value = true
}

function onFarmland(id) {
  const f = farmlands.value.find(x => x.id === id)
  if (f) form.planVolume = Math.round(Number(f.area) * 18)
}

async function save() {
  if (!form.farmlandId || !form.gateId || !form.planStart || !form.planEnd) {
    ElMessage.warning('地块、闸口与时段必填')
    return
  }
  saving.value = true
  try {
    const id = await request.post('/plan', form)
    await request.post(`/plan/${id}/transition`, { target: 'AUDITING' }).catch(() => {})
    ElMessage.success('计划已创建并提交审批')
    createVisible.value = false
    load()
  } finally { saving.value = false }
}

async function transition(row) {
  const act = nextAction(row.status)
  if (!act) return
  await ElMessageBox.confirm(`确认将计划 ${row.code} 流转到「${act.label}」？`, '状态流转', { type: 'warning' })
  await request.post(`/plan/${row.id}/transition`, { target: act.target })
  ElMessage.success('已流转：' + act.label)
  load()
}

async function openDetail(row) {
  Object.assign(detail, await request.get('/plan/' + row.id))
  detailVisible.value = true
}

onMounted(async () => {
  await loadBase()
  await load()
})
</script>

<style scoped>
.quick { display: flex; gap: 6px; }
.quick span { font-size: 12.5px; color: var(--text-2); border: 1px solid var(--line); background: #fff; padding: 4px 11px; border-radius: 4px; cursor: pointer; }
.quick span.on { background: var(--primary); color: #fff; border-color: var(--primary); }
.dh { display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 15px; }
.dh-sub { font-size: 12.5px; color: var(--text-2); margin-top: 4px; }
.sub-h { font-size: 14px; margin: 18px 0 10px; }
</style>
