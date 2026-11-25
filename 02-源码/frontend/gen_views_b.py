# -*- coding: utf-8 -*-
"""批量生成第二批页面：计划、任务、用水建议（创新点）、统计、系统、个人中心、种植户门户。"""
import pathlib

DIR = pathlib.Path("/Users/xiaoxin/showcase/build/NEW-017/frontend/src/views")
F = {}

F["Plan.vue"] = r'''<template>
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
'''

F["Task.vue"] = r'''<template>
  <div>
    <h1 class="page-title">执行任务</h1>
    <p class="page-sub">放水员现场录入开始/结束表数、实际水量与照片；结束表数不得小于开始表数，中断必须填写原因</p>

    <div class="panel">
      <div class="panel-bd">
        <div class="filters">
          <el-select v-model="query.status" placeholder="全部状态" clearable>
            <el-option label="待执行" value="PENDING" />
            <el-option label="进行中" value="RUNNING" />
            <el-option label="已完成" value="FINISHED" />
            <el-option label="已中断" value="INTERRUPTED" />
          </el-select>
          <el-input v-model="query.keyword" placeholder="任务号" clearable @keyup.enter="search" />
          <el-button type="primary" @click="search">查询</el-button>
          <el-button @click="reset">重置</el-button>
        </div>
        <div class="table-wrap">
          <el-table :data="rows" v-loading="loading" border stripe>
            <el-table-column prop="code" label="任务号" min-width="150" />
            <el-table-column prop="farmlandName" label="地块" min-width="130" />
            <el-table-column label="作物/阶段" min-width="116">
              <template #default="{ row }">{{ row.crop }} / {{ row.growthStage }}</template>
            </el-table-column>
            <el-table-column label="计划时段" min-width="180">
              <template #default="{ row }">{{ row.planStart ? formatTime(row.planStart) : '—' }}</template>
            </el-table-column>
            <el-table-column prop="operatorName" label="放水员" min-width="88" />
            <el-table-column label="开始/结束表数" min-width="150" align="right">
              <template #default="{ row }">
                <span class="num">{{ row.startReading ? num(row.startReading, 1) : '—' }} / {{ row.endReading ? num(row.endReading, 1) : '—' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="实际水量(m³)" min-width="116" align="right">
              <template #default="{ row }"><span class="num">{{ row.actualVolume ? num(row.actualVolume, 1) : '—' }}</span></template>
            </el-table-column>
            <el-table-column label="状态" min-width="90">
              <template #default="{ row }"><span class="tag" :class="tagOf(row.status)">{{ text(row.status) }}</span></template>
            </el-table-column>
            <el-table-column label="操作" min-width="112" fixed="right">
              <template #default="{ row }">
                <el-button v-if="row.status === 'PENDING'" link type="primary" @click="openAction(row, 'start')">开始</el-button>
                <el-button v-else-if="row.status === 'RUNNING'" link type="primary" @click="openAction(row, 'finish')">录入完成</el-button>
                <el-button v-else link type="primary" @click="openDetail(row)">详情</el-button>
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

    <!-- 执行抽屉：移动端执行页同款布局，桌面端以抽屉承载 -->
    <el-drawer v-model="actionVisible" :title="action === 'start' ? '开始执行' : '提交完成'" size="520px">
      <template v-if="current">
        <div class="exec-head">
          <b>{{ current.code }}</b>
          <span class="tag sky">{{ text(current.status) }}</span>
        </div>
        <p class="exec-sub">{{ current.farmlandName }} · 计划水量 {{ num(current.planVolume, 1) }} m³ · {{ current.operatorName }}</p>
        <el-form label-width="100px" label-position="left">
          <el-form-item label="开始表数" v-if="action === 'start'" required>
            <el-input-number v-model="exec.startReading" :min="0" :precision="2" style="width:100%" />
          </el-form-item>
          <template v-else>
            <el-form-item label="开始表数"><span class="num">{{ num(current.startReading, 2) }} m³</span></el-form-item>
            <el-form-item label="结束表数" required>
              <el-input-number v-model="exec.endReading" :min="Number(current.startReading || 0)" :precision="2" style="width:100%" />
            </el-form-item>
            <el-form-item label="实际水量">
              <span class="num" style="font-size:16px;font-weight:600">{{ num(actualVolume, 2) }} m³</span>
              <span v-if="deviation" class="tag" :class="Math.abs(deviation) > 15 ? 'warn' : 'ok'" style="margin-left:8px">
                偏差 {{ deviation > 0 ? '+' : '' }}{{ deviation }}%
              </span>
            </el-form-item>
            <el-form-item label="受水人">
              <el-input v-model="exec.receiverName" placeholder="受水人确认姓名" />
            </el-form-item>
            <el-form-item label="现场照片">
              <div class="uploader">
                <img v-if="exec.photo" :src="exec.photo" class="thumb" alt="现场照片" />
                <el-upload :action="uploadUrl" :headers="uploadHeaders" :show-file-list="false" accept="image/*" :on-success="onUploaded">
                  <el-button size="small">{{ exec.photo ? '重新上传' : '上传照片' }}</el-button>
                </el-upload>
              </div>
            </el-form-item>
            <el-form-item label="备注">
              <el-input v-model="exec.remark" type="textarea" :rows="2" placeholder="选填" />
            </el-form-item>
          </template>
        </el-form>
      </template>
      <template #footer>
        <el-button v-if="action === 'finish'" type="danger" plain @click="openInterrupt">中断任务</el-button>
        <el-button @click="actionVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submit">
          {{ action === 'start' ? '确认开始' : '提交完成' }}
        </el-button>
      </template>
    </el-drawer>

    <el-dialog v-model="interruptVisible" title="中断任务" width="480px">
      <el-form label-width="100px" label-position="left">
        <el-form-item label="结束表数" required>
          <el-input-number v-model="interrupt.endReading" :min="Number(current?.startReading || 0)" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="中断原因" required>
          <el-input v-model="interrupt.reason" type="textarea" :rows="3" placeholder="不少于 5 个字，如：渠道堵塞导致末端无水" />
        </el-form-item>
        <el-form-item label="异常类型">
          <el-select v-model="interrupt.excType" style="width:100%">
            <el-option label="渠道堵塞" value="BLOCK" />
            <el-option label="漏水" value="LEAK" />
            <el-option label="设备故障" value="FAULT" />
            <el-option label="水量不足" value="SHORT" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="interruptVisible = false">取消</el-button>
        <el-button type="danger" :loading="saving" @click="doInterrupt">确认中断</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="detailVisible" title="任务详情" size="560px">
      <template v-if="detail.id">
        <div class="exec-head">
          <b>{{ detail.code }}</b>
          <span class="tag" :class="tagOf(detail.status)">{{ text(detail.status) }}</span>
        </div>
        <p class="exec-sub">{{ detail.farmlandName }} · {{ detail.operatorName }}</p>
        <dl>
          <div class="kv"><dt>计划水量</dt><dd>{{ num(detail.planVolume, 2) }} m³</dd></div>
          <div class="kv"><dt>开始/结束表数</dt><dd>{{ num(detail.startReading, 2) }} / {{ num(detail.endReading, 2) }}</dd></div>
          <div class="kv"><dt>实际水量</dt><dd>{{ detail.actualVolume ? num(detail.actualVolume, 2) + ' m³' : '—' }}</dd></div>
          <div class="kv"><dt>起止时间</dt><dd>{{ formatTime(detail.startTime) }} ~ {{ formatTime(detail.endTime) }}</dd></div>
          <div class="kv"><dt>受水人确认</dt><dd>{{ detail.receiverName || '—' }}</dd></div>
          <div class="kv" v-if="detail.interruptReason"><dt>中断原因</dt><dd style="color:#B22B31">{{ detail.interruptReason }}</dd></div>
        </dl>
        <img v-if="detail.photo" :src="detail.photo" class="big-img" alt="现场照片" />
        <h4 class="sub-h">抄表记录</h4>
        <el-table :data="detail.meterRecords || []" size="small" border>
          <el-table-column prop="startReading" label="开始" min-width="90" align="right" />
          <el-table-column prop="endReading" label="结束" min-width="90" align="right" />
          <el-table-column prop="volume" label="水量" min-width="90" align="right" />
          <el-table-column prop="recorderName" label="抄表人" min-width="80" />
        </el-table>
        <h4 class="sub-h">时间轴</h4>
        <el-timeline>
          <el-timeline-item v-for="l in detail.timeline || []" :key="l.id" :timestamp="formatTime(l.createTime)">
            {{ l.action }}<span v-if="l.reason"> · {{ l.reason }}</span>
          </el-timeline-item>
        </el-timeline>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { formatTime, num, text, STATUS_TYPE } from '@/utils/format'

const rows = ref([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const actionVisible = ref(false)
const interruptVisible = ref(false)
const detailVisible = ref(false)
const action = ref('start')
const current = ref(null)
const detail = reactive({})
const query = reactive({ status: '', keyword: '', page: 1, size: 10 })
const exec = reactive({ startReading: 0, endReading: 0, photo: '', receiverName: '', remark: '' })
const interrupt = reactive({ endReading: 0, reason: '', excType: 'BLOCK' })

const uploadUrl = '/api/file/upload'
const uploadHeaders = computed(() => ({ Authorization: 'Bearer ' + localStorage.getItem('token') }))
const tagOf = s => 'tag ' + (STATUS_TYPE[s] || 'info')

const actualVolume = computed(() => Math.max(0, Number(exec.endReading || 0) - Number(current.value?.startReading || 0)))
const deviation = computed(() => {
  const plan = Number(current.value?.planVolume || 0)
  return plan ? Number(((actualVolume.value - plan) / plan * 100).toFixed(1)) : 0
})

async function load() {
  loading.value = true
  try {
    const data = await request.get('/task/page', { params: query })
    rows.value = data.records || []
    total.value = data.total || 0
  } finally { loading.value = false }
}
const search = () => { query.page = 1; load() }
const onSize = () => { query.page = 1; load() }
const reset = () => { Object.assign(query, { status: '', keyword: '', page: 1 }); load() }

function openAction(row, type) {
  current.value = row
  action.value = type
  Object.assign(exec, {
    startReading: row.startReading ? Number(row.startReading) : 12000,
    endReading: row.startReading ? Number(row.startReading) : 12000,
    photo: '', receiverName: '', remark: ''
  })
  actionVisible.value = true
}

const onUploaded = res => {
  if (res.code === 200) exec.photo = res.data
  else ElMessage.error(res.message || '上传失败')
}

async function submit() {
  saving.value = true
  try {
    if (action.value === 'start') {
      await request.post(`/task/${current.value.id}/start`, { startReading: exec.startReading })
      ElMessage.success('任务已开始')
    } else {
      const r = await request.post(`/task/${current.value.id}/finish`, exec)
      ElMessage.success(r.needReview ? `已提交，实际水量偏差 ${r.deviation}%，需复核` : '已完成，费用已生成')
    }
    actionVisible.value = false
    load()
  } finally { saving.value = false }
}

function openInterrupt() {
  interrupt.endReading = exec.endReading
  interrupt.reason = ''
  interruptVisible.value = true
}

async function doInterrupt() {
  if (!interrupt.reason || interrupt.reason.trim().length < 5) {
    ElMessage.warning('中断原因不少于 5 个字')
    return
  }
  saving.value = true
  try {
    await request.post(`/task/${current.value.id}/interrupt`, {
      endReading: interrupt.endReading, reason: interrupt.reason, photo: exec.photo
    })
    await request.post(`/task/${current.value.id}/exception`, {
      excType: interrupt.excType, description: interrupt.reason, lossVolume: 0, photo: exec.photo
    }).catch(() => {})
    ElMessage.success('已中断并记录异常')
    interruptVisible.value = false
    actionVisible.value = false
    load()
  } finally { saving.value = false }
}

async function openDetail(row) {
  Object.assign(detail, await request.get('/task/' + row.id))
  detailVisible.value = true
}

onMounted(load)
</script>

<style scoped>
.exec-head { display: flex; justify-content: space-between; align-items: center; font-size: 15px; }
.exec-sub { font-size: 12.5px; color: var(--text-2); margin: 4px 0 14px; }
.uploader { display: flex; align-items: center; gap: 12px; }
.thumb { width: 72px; height: 54px; object-fit: cover; border-radius: 6px; border: 1px solid var(--line); }
.big-img { width: 100%; max-height: 220px; object-fit: cover; border-radius: 8px; border: 1px solid var(--line); margin-top: 12px; }
.sub-h { font-size: 14px; margin: 18px 0 10px; }
</style>
'''

F["Advice.vue"] = r'''<template>
  <div>
    <h1 class="page-title">作物阶段用水建议</h1>
    <p class="page-sub">根据作物类型、生育阶段、面积、土壤保水等级与近期降雨计算建议水量，与定额对比并提示偏差</p>

    <el-tabs v-model="tab" class="advice-tabs">
      <el-tab-pane label="计算与结果" name="calc">
        <div class="kpis four" style="margin-bottom:14px">
          <div class="kpi"><div class="lb">累计计算</div><div class="vl">{{ stats.total || 0 }}<small>次</small></div></div>
          <div class="kpi"><div class="lb">推荐采纳率</div><div class="vl">{{ percent(stats.adoptRate) }}</div></div>
          <div class="kpi"><div class="lb">人工调整率</div><div class="vl">{{ percent(stats.adjustRate) }}</div><div class="dt warn">需关注偏差原因</div></div>
          <div class="kpi"><div class="lb">平均偏差</div><div class="vl">{{ percent(stats.avgDeviation) }}</div></div>
        </div>

        <div class="panel">
          <div class="panel-hd"><span>执行计算</span>
            <span style="font-weight:400;font-size:12.5px;color:var(--text-2)">生效规则 {{ stats.activeRule?.version || '—' }} · 权重合计 100%</span>
          </div>
          <div class="panel-bd">
            <div class="filters">
              <el-select v-model="calc.farmlandId" filterable placeholder="选择地块" style="width:240px">
                <el-option v-for="f in farmlands" :key="f.id" :label="`${f.name}（${f.crop} ${f.growthStage}）`" :value="f.id" />
              </el-select>
              <el-input-number v-model="calc.rainMm" :min="0" :precision="1" :step="1" style="width:150px" placeholder="近 7 天降雨 mm" />
              <el-button type="primary" :loading="calculating" @click="evaluate">计算并留痕</el-button>
              <span style="font-size:12.5px;color:var(--text-2)">近期降雨由人工录入；不填则标记为「数据不足」</span>
            </div>

            <div v-if="result" class="result">
              <div class="result-left">
                <div class="res-num">
                  <div class="lb">建议用水量</div>
                  <div class="big">{{ num(result.suggestVolume, 0) }}<small>m³</small></div>
                  <div class="cmp">对比 {{ num(result.quotaVolume, 0) }} m³ · 偏差
                    <b :style="{ color: Math.abs(result.deviation) > 20 ? '#B22B31' : (Math.abs(result.deviation) > 10 ? '#B4761E' : '#1F7653') }">
                      {{ result.deviation > 0 ? '+' : '' }}{{ result.deviation }}%
                    </b>
                  </div>
                  <span class="tag" :class="tagOf(result.grade)" style="margin-top:8px">{{ GRADE[result.grade] }}</span>
                </div>
                <div class="scores">
                  <div class="srow" v-for="s in scoreRows" :key="s.k">
                    <span>{{ s.k }}</span>
                    <div class="bar"><i :style="{ width: Math.min(100, Number(s.v)) + '%' }"></i></div>
                    <b>{{ num(s.v, 1) }}</b>
                  </div>
                  <div class="srow total"><span>加权总分</span><div class="bar"><i :style="{ width: Math.min(100, Number(result.totalScore)) + '%' }"></i></div><b>{{ num(result.totalScore, 1) }}</b></div>
                </div>
              </div>
              <div class="result-right">
                <div class="exp"><dt>主要影响因素</dt><dd>{{ result.explainMain }}</dd></div>
                <div class="exp"><dt>未满足条件</dt><dd>{{ result.explainMissing }}</dd></div>
                <div class="exp"><dt>可改进项</dt><dd>{{ result.explainImprove }}</dd></div>
                <div class="snap">规则版本 {{ result.ruleVersion }} · 输入快照已保存 · {{ formatTime(result.createTime) }}</div>
              </div>
            </div>
            <p v-else class="empty">选择地块并录入近期降雨后点击「计算并留痕」，结果会保存输入快照与各项得分。</p>
          </div>
        </div>

        <div class="panel">
          <div class="panel-hd"><span>计算记录</span>
            <span style="font-weight:400"><el-select v-model="query.grade" size="small" placeholder="全部等级" clearable style="width:140px" @change="load"><el-option v-for="(v, k) in GRADE" :key="k" :label="v" :value="k" /></el-select></span>
          </div>
          <div class="panel-bd flush">
            <div class="table-wrap">
              <el-table :data="rows" v-loading="loading" border stripe>
                <el-table-column prop="id" label="编号" min-width="70" align="center" />
                <el-table-column label="建议水量(m³)" min-width="118" align="right">
                  <template #default="{ row }"><span class="num">{{ num(row.suggestVolume, 0) }}</span></template>
                </el-table-column>
                <el-table-column label="对比定额(m³)" min-width="118" align="right">
                  <template #default="{ row }"><span class="num">{{ num(row.quotaVolume, 0) }}</span></template>
                </el-table-column>
                <el-table-column label="偏差" min-width="86" align="right">
                  <template #default="{ row }"><span class="num">{{ row.deviation }}%</span></template>
                </el-table-column>
                <el-table-column label="结果等级" min-width="100">
                  <template #default="{ row }"><span class="tag" :class="tagOf(row.grade)">{{ GRADE[row.grade] }}</span></template>
                </el-table-column>
                <el-table-column prop="ruleVersion" label="规则版本" min-width="86" align="center" />
                <el-table-column label="人工修正" min-width="150">
                  <template #default="{ row }">
                    <span v-if="row.adjustVolume" class="num">→ {{ num(row.adjustVolume, 0) }} m³（{{ row.adjustBy }}）</span>
                    <el-button v-else link type="primary" @click="openAdjust(row)">修正</el-button>
                  </template>
                </el-table-column>
                <el-table-column label="计算时间" min-width="152">
                  <template #default="{ row }">{{ formatTime(row.createTime) }}</template>
                </el-table-column>
              </el-table>
            </div>
            <div class="pager">
              <el-pagination background layout="total, prev, pager, next" :total="total"
                             v-model:current-page="query.page" v-model:page-size="query.size" @current-change="load" />
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="规则配置" name="rule">
        <div class="panel">
          <div class="panel-hd"><span>权重配置</span><span style="font-weight:400;font-size:12.5px;color:var(--text-2)">合计必须等于 100%，保存后生成新版本</span></div>
          <div class="panel-bd">
            <div class="weights">
              <div class="w" v-for="w in weightFields" :key="w.k">
                <label>{{ w.t }}</label>
                <el-input-number v-model="rule[w.k]" :min="0" :max="100" :step="1" style="width:120px" />
                <span>%</span>
              </div>
              <div class="wsum" :class="{ bad: weightSum !== 100 }">合计 {{ weightSum }}%</div>
            </div>
            <div class="filters" style="margin-top:14px">
              <el-input v-model="rule.name" placeholder="规则名称（可选）" style="width:280px" />
              <el-button type="primary" :loading="savingRule" @click="saveRule">保存为新版本</el-button>
            </div>
            <el-table :data="rules" border size="small" style="margin-top:14px">
              <el-table-column prop="version" label="版本" min-width="70" align="center" />
              <el-table-column prop="name" label="名称" min-width="240" />
              <el-table-column prop="cropWeight" label="作物" min-width="66" align="center" />
              <el-table-column prop="stageWeight" label="阶段" min-width="66" align="center" />
              <el-table-column prop="areaWeight" label="面积" min-width="66" align="center" />
              <el-table-column prop="soilWeight" label="土壤" min-width="66" align="center" />
              <el-table-column prop="rainWeight" label="降雨" min-width="66" align="center" />
              <el-table-column prop="historyWeight" label="历史" min-width="66" align="center" />
              <el-table-column label="状态" min-width="80">
                <template #default="{ row }"><span class="tag" :class="row.status === 'ACTIVE' ? 'ok' : 'info'">{{ row.status === 'ACTIVE' ? '生效' : '停用' }}</span></template>
              </el-table-column>
              <el-table-column label="生效时间" min-width="152">
                <template #default="{ row }">{{ formatTime(row.effectiveTime) }}</template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="adjustVisible" title="人工修正建议水量" width="480px">
      <div class="notice info">原始计算结果不会被覆盖，修正只追加记录并留痕。</div>
      <el-form label-width="100px" label-position="left">
        <el-form-item label="原始建议"><span class="num">{{ num(currentRow?.suggestVolume, 0) }} m³</span></el-form-item>
        <el-form-item label="修正水量" required>
          <el-input-number v-model="adjust.volume" :min="1" :precision="2" :step="50" style="width:100%" />
        </el-form-item>
        <el-form-item label="修正原因" required>
          <el-input v-model="adjust.reason" type="textarea" :rows="3" placeholder="不少于 5 个字" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="adjustVisible = false">取消</el-button>
        <el-button type="primary" @click="doAdjust">提交修正</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { formatTime, num, percent, GRADE, STATUS_TYPE } from '@/utils/format'

const tab = ref('calc')
const rows = ref([])
const total = ref(0)
const loading = ref(false)
const calculating = ref(false)
const savingRule = ref(false)
const adjustVisible = ref(false)
const result = ref(null)
const stats = reactive({ total: 0, adoptRate: 0, adjustRate: 0, avgDeviation: 0, activeRule: null })
const farmlands = ref([])
const rules = ref([])
const currentRow = ref(null)
const query = reactive({ grade: '', page: 1, size: 10 })
const calc = reactive({ farmlandId: null, rainMm: 18.6 })
const adjust = reactive({ volume: 0, reason: '' })

const weightFields = [
  { k: 'cropWeight', t: '作物类型' }, { k: 'stageWeight', t: '生育阶段' }, { k: 'areaWeight', t: '地块面积' },
  { k: 'soilWeight', t: '土壤等级' }, { k: 'rainWeight', t: '近期降雨' }, { k: 'historyWeight', t: '历史单耗' }
]
const rule = reactive({ name: '', cropWeight: 24, stageWeight: 22, areaWeight: 18, soilWeight: 14, rainWeight: 12, historyWeight: 10 })
const weightSum = computed(() => weightFields.reduce((s, w) => s + Number(rule[w.k] || 0), 0))

const tagOf = s => 'tag ' + (STATUS_TYPE[s] || 'info')
const scoreRows = computed(() => result.value ? [
  { k: '作物需水', v: result.value.cropScore }, { k: '阶段系数', v: result.value.stageScore },
  { k: '面积修正', v: result.value.areaScore }, { k: '土壤保水', v: result.value.soilScore },
  { k: '降雨折减', v: result.value.rainScore }, { k: '历史校准', v: result.value.historyScore }
] : [])

async function load() {
  loading.value = true
  try {
    const data = await request.get('/advice/page', { params: query })
    rows.value = data.records || []
    total.value = data.total || 0
    Object.assign(stats, await request.get('/advice/stats'))
  } finally { loading.value = false }
}

async function loadBase() {
  const f = await request.get('/farmland/page', { params: { page: 1, size: 50 } })
  farmlands.value = f.records || []
  calc.farmlandId = farmlands.value[0]?.id || null
  rules.value = await request.get('/rule/list')
}

async function evaluate() {
  if (!calc.farmlandId) { ElMessage.warning('请选择地块'); return }
  calculating.value = true
  try {
    result.value = await request.post('/advice/evaluate', { farmlandId: calc.farmlandId, rainMm: calc.rainMm })
    ElMessage.success('计算完成，已保存输入快照')
    load()
  } finally { calculating.value = false }
}

function openAdjust(row) {
  currentRow.value = row
  adjust.volume = Number(row.suggestVolume)
  adjust.reason = ''
  adjustVisible.value = true
}

async function doAdjust() {
  if (!adjust.reason || adjust.reason.trim().length < 5) { ElMessage.warning('修正原因不少于 5 个字'); return }
  await request.post(`/advice/${currentRow.value.id}/adjust`, adjust)
  ElMessage.success('已提交修正，原始结果保留')
  adjustVisible.value = false
  load()
}

async function saveRule() {
  if (weightSum.value !== 100) { ElMessage.warning('权重合计必须等于 100%，当前 ' + weightSum.value + '%'); return }
  savingRule.value = true
  try {
    await request.post('/rule', rule)
    ElMessage.success('新版本已生效')
    rules.value = await request.get('/rule/list')
    await load()
  } finally { savingRule.value = false }
}

onMounted(async () => {
  await loadBase()
  await load()
})
</script>

<style scoped>
.advice-tabs { margin-top: -6px; }
.result { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; border-top: 1px solid var(--line); padding-top: 16px; }
.res-num .lb { font-size: 12.5px; color: var(--text-2); }
.res-num .big { font-size: 34px; font-weight: 600; color: var(--primary); font-variant-numeric: tabular-nums; line-height: 1.2; }
.res-num .big small { font-size: 13px; font-weight: 400; color: var(--text-2); margin-left: 4px; }
.res-num .cmp { font-size: 12.5px; color: var(--text-2); margin-top: 4px; }
.scores { margin-top: 14px; }
.srow { display: flex; align-items: center; gap: 10px; font-size: 12.5px; margin-bottom: 7px; }
.srow span { width: 64px; color: var(--text-2); flex: 0 0 64px; }
.srow .bar { flex: 1; height: 8px; background: #EDF3F8; border-radius: 4px; overflow: hidden; }
.srow .bar i { display: block; height: 100%; background: var(--secondary); }
.srow b { width: 44px; text-align: right; font-variant-numeric: tabular-nums; font-weight: 500; }
.srow.total b { color: var(--primary); }
.exp { padding: 7px 0; border-bottom: 1px dashed #EDF3F8; font-size: 13px; }
.exp dt { color: var(--text-2); font-size: 12.5px; margin-bottom: 2px; }
.exp dd { margin: 0; }
.snap { font-size: 12px; color: #93A3B0; margin-top: 10px; }
.empty { font-size: 13px; color: var(--text-2); background: #F8FBFD; border: 1px dashed var(--line); border-radius: 6px; padding: 14px; }
.weights { display: flex; flex-wrap: wrap; gap: 16px; align-items: center; }
.w { display: flex; align-items: center; gap: 6px; font-size: 13px; }
.w label { width: 64px; color: var(--text-2); }
.wsum { font-size: 13px; font-weight: 600; color: var(--success); }
.wsum.bad { color: var(--danger); }
</style>
'''

F["Analyze.vue"] = r'''<template>
  <div>
    <h1 class="page-title">用水统计</h1>
    <p class="page-sub">水源供水量、作物用水、亩均用水、定额使用率、时段负荷、异常损失与费用汇总</p>

    <div class="kpis four" style="margin-bottom:14px">
      <div class="kpi"><div class="lb">实际用水量</div><div class="vl">{{ num(d.actualVolume, 0) }}<small>m³</small></div></div>
      <div class="kpi"><div class="lb">亩均用水</div><div class="vl">{{ num(d.perMu, 1) }}<small>m³/亩</small></div></div>
      <div class="kpi"><div class="lb">定额偏差</div><div class="vl">{{ percent(d.quotaDeviation) }}</div></div>
      <div class="kpi"><div class="lb">异常损失</div><div class="vl" style="color:#B22B31">{{ num(d.lossVolume, 0) }}<small>m³</small></div></div>
    </div>

    <div class="charts" style="margin-bottom:14px">
      <div class="chart span2"><h4>作物用水量 <em>m³</em></h4><div ref="c1" class="cv"></div></div>
      <div class="chart"><h4>水源当前可用 <em>m³</em></h4><div ref="c2" class="cv"></div></div>
    </div>

    <div class="panel">
      <div class="panel-hd"><span>作物用水明细</span><span style="font-weight:400;font-size:12.5px;color:var(--text-2)">与看板口径一致</span></div>
      <div class="panel-bd flush">
        <div class="table-wrap">
          <el-table :data="d.cropDist || []" border stripe>
            <el-table-column prop="crop" label="作物" min-width="110" />
            <el-table-column label="实际水量(m³)" min-width="130" align="right">
              <template #default="{ row }"><span class="num">{{ num(row.volume, 2) }}</span></template>
            </el-table-column>
            <el-table-column label="占比" min-width="90" align="right">
              <template #default="{ row }"><span class="num">{{ percent(row.percent) }}</span></template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-hd"><span>地块单耗排行</span></div>
      <div class="panel-bd flush">
        <div class="table-wrap">
          <el-table :data="d.topLand || []" border stripe>
            <el-table-column prop="name" label="地块" min-width="160" />
            <el-table-column label="亩均用水(m³/亩)" min-width="140" align="right">
              <template #default="{ row }"><span class="num">{{ num(row.perMu, 1) }}</span></template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import * as echarts from 'echarts'
import request from '@/utils/request'
import { num, percent } from '@/utils/format'

const d = reactive({})
const c1 = ref()
const c2 = ref()
const charts = []

onMounted(async () => {
  Object.assign(d, await request.get('/dashboard', { params: { days: 30 } }))
  await nextTick()
  const crop = d.cropDist || []
  charts.push(echarts.init(c1.value))
  charts[0].setOption({
    grid: { left: 44, right: 12, top: 16, bottom: 26 },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: crop.map(c => c.crop), axisLabel: { color: '#5A6B78', fontSize: 11 }, axisLine: { lineStyle: { color: '#DCE6EE' } }, axisTick: { show: false } },
    yAxis: { type: 'value', axisLabel: { color: '#5A6B78', fontSize: 10.5 }, splitLine: { lineStyle: { color: '#EDF3F8' } } },
    series: [{ type: 'bar', barWidth: 26, data: crop.map(c => Number(c.volume)), itemStyle: { color: '#0F3B5D', borderRadius: [3, 3, 0, 0] } }]
  })
  const src = d.sourceSupply || []
  charts.push(echarts.init(c2.value))
  charts[1].setOption({
    grid: { left: 40, right: 10, top: 16, bottom: 26 },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: src.map(s => s.name), axisLabel: { color: '#5A6B78', fontSize: 10, rotate: 18 }, axisLine: { lineStyle: { color: '#DCE6EE' } }, axisTick: { show: false } },
    yAxis: { type: 'value', axisLabel: { color: '#5A6B78', fontSize: 10.5 }, splitLine: { lineStyle: { color: '#EDF3F8' } } },
    series: [{ type: 'bar', barWidth: 18, data: src.map(s => Number(s.available)), itemStyle: { color: '#2878B5', borderRadius: [3, 3, 0, 0] } }]
  })
})

onBeforeUnmount(() => charts.forEach(c => c.dispose()))
</script>

<style scoped>
.chart.span2 { grid-column: span 2; }
.chart .cv { height: 150px; }
</style>
'''

F["System.vue"] = r'''<template>
  <div>
    <h1 class="page-title">系统管理</h1>
    <p class="page-sub">用户、角色、菜单与数据范围分别控制；只有菜单权限不能直接调用写接口</p>

    <el-tabs v-model="tab">
      <el-tab-pane label="用户管理" name="user">
        <div class="panel">
          <div class="panel-bd">
            <div class="filters">
              <el-input v-model="userQuery.keyword" placeholder="姓名 / 账号" clearable style="width:200px" @keyup.enter="loadUsers" />
              <el-select v-model="userQuery.roleId" placeholder="全部角色" clearable style="width:160px">
                <el-option v-for="r in roles" :key="r.id" :label="r.name" :value="r.id" />
              </el-select>
              <el-button type="primary" @click="loadUsers">查询</el-button>
              <el-button type="primary" style="margin-left:auto" @click="openUser()">新增用户</el-button>
            </div>
            <div class="table-wrap">
              <el-table :data="users" border stripe>
                <el-table-column prop="username" label="账号" min-width="120" />
                <el-table-column prop="realName" label="姓名" min-width="96" />
                <el-table-column prop="roleName" label="角色" min-width="110" />
                <el-table-column prop="orgName" label="所属组织" min-width="120" />
                <el-table-column label="数据范围" min-width="96">
                  <template #default="{ row }">{{ scopeText(row.dataScope) }}</template>
                </el-table-column>
                <el-table-column prop="phone" label="联系电话" min-width="120" />
                <el-table-column label="状态" min-width="84">
                  <template #default="{ row }">
                    <span class="tag" :class="row.status === 1 ? 'ok' : 'info'">{{ row.status === 1 ? '启用' : '停用' }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="操作" min-width="180">
                  <template #default="{ row }">
                    <el-button link type="primary" @click="openUser(row)">编辑</el-button>
                    <el-button link type="primary" @click="resetPwd(row)">重置密码</el-button>
                    <el-button link type="danger" @click="toggle(row)">{{ row.status === 1 ? '停用' : '启用' }}</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <div class="pager">
              <el-pagination background layout="total, prev, pager, next" :total="userTotal"
                             v-model:current-page="userQuery.page" v-model:page-size="userQuery.size" @current-change="loadUsers" />
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="角色与菜单授权" name="role">
        <div class="panel">
          <div class="panel-bd role-box">
            <div class="role-list">
              <div class="rl-title">角色</div>
              <div v-for="r in roles" :key="r.id" class="rl-item" :class="{ on: roleId === r.id }" @click="pickRole(r)">
                <b>{{ r.name }}</b>
                <span>{{ scopeText(r.dataScope) }}</span>
              </div>
            </div>
            <div class="role-menu">
              <div class="rl-title">{{ currentRole?.name }} · 菜单与按钮权限</div>
              <el-tree ref="treeRef" :data="menus" show-checkbox node-key="id" :props="{ label: 'name', children: 'children' }" default-expand-all />
              <div style="margin-top:14px">
                <el-button type="primary" @click="saveMenus">保存授权</el-button>
                <span style="font-size:12.5px;color:var(--text-2);margin-left:10px">「菜单管理」为隐藏项，不在导航中展示</span>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="操作日志" name="log">
        <div class="panel">
          <div class="panel-bd">
            <div class="filters">
              <el-select v-model="logQuery.bizType" placeholder="全部业务" clearable style="width:170px">
                <el-option label="用水申请" value="APPLICATION" />
                <el-option label="灌溉计划" value="PLAN" />
                <el-option label="执行任务" value="TASK" />
                <el-option label="地块" value="FARMLAND" />
                <el-option label="定额" value="QUOTA" />
              </el-select>
              <el-button type="primary" @click="loadLogs">查询</el-button>
            </div>
            <div class="table-wrap">
              <el-table :data="logs" border stripe>
                <el-table-column prop="bizNo" label="业务编号" min-width="150" />
                <el-table-column prop="action" label="动作" min-width="110" />
                <el-table-column label="状态变化" min-width="150">
                  <template #default="{ row }">{{ row.beforeStatus || '—' }} → {{ row.afterStatus || '—' }}</template>
                </el-table-column>
                <el-table-column prop="reason" label="原因" min-width="200" show-overflow-tooltip />
                <el-table-column prop="operatorName" label="操作人" min-width="90" />
                <el-table-column label="操作时间" min-width="152">
                  <template #default="{ row }">{{ formatTime(row.createTime) }}</template>
                </el-table-column>
              </el-table>
            </div>
            <div class="pager">
              <el-pagination background layout="total, prev, pager, next" :total="logTotal"
                             v-model:current-page="logQuery.page" v-model:page-size="logQuery.size" @current-change="loadLogs" />
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="userVisible" :title="userForm.id ? '编辑用户' : '新增用户'" width="500px">
      <el-form :model="userForm" label-width="100px" label-position="left">
        <el-form-item label="账号" required><el-input v-model="userForm.username" :disabled="!!userForm.id" /></el-form-item>
        <el-form-item label="姓名" required><el-input v-model="userForm.realName" /></el-form-item>
        <el-form-item label="角色" required>
          <el-select v-model="userForm.roleId" style="width:100%">
            <el-option v-for="r in roles" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="组织" required>
          <el-select v-model="userForm.orgId" style="width:100%">
            <el-option v-for="o in orgs" :key="o.id" :label="o.name" :value="o.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="电话"><el-input v-model="userForm.phone" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="userForm.email" /></el-form-item>
        <el-form-item v-if="!userForm.id" label="初始密码">
          <el-input v-model="userForm.password" placeholder="默认 123456" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="userVisible = false">取消</el-button>
        <el-button type="primary" @click="saveUser">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { formatTime } from '@/utils/format'

const tab = ref('user')
const users = ref([])
const userTotal = ref(0)
const roles = ref([])
const orgs = ref([])
const menus = ref([])
const logs = ref([])
const logTotal = ref(0)
const roleId = ref(null)
const currentRole = ref(null)
const treeRef = ref()
const userVisible = ref(false)

const userQuery = reactive({ keyword: '', roleId: null, page: 1, size: 10 })
const logQuery = reactive({ bizType: '', page: 1, size: 10 })
const userForm = reactive({ id: null, username: '', realName: '', roleId: 4, orgId: 3, phone: '', email: '', password: '' })

const scopeText = s => ({ ALL: '全部', DEPT: '本部门', SELF: '仅本人' }[s] || s)

async function loadUsers() {
  const data = await request.get('/system/user/page', { params: userQuery })
  users.value = data.records || []
  userTotal.value = data.total || 0
}

async function loadLogs() {
  const data = await request.get('/system/log/page', { params: logQuery })
  logs.value = data.records || []
  logTotal.value = data.total || 0
}

function openUser(row) {
  Object.assign(userForm, { id: null, username: '', realName: '', roleId: 4, orgId: 3, phone: '', email: '', password: '' })
  if (row) Object.assign(userForm, row)
  userVisible.value = true
}

async function saveUser() {
  if (!userForm.username || !userForm.realName) { ElMessage.warning('账号与姓名必填'); return }
  await request.post('/system/user', userForm)
  ElMessage.success('保存成功')
  userVisible.value = false
  loadUsers()
}

async function resetPwd(row) {
  const { value } = await ElMessageBox.prompt('请输入新密码（至少 6 位）', '重置密码 ' + row.realName, { inputValue: '123456' })
  await request.put(`/system/user/${row.id}/password`, { password: value })
  ElMessage.success('密码已重置')
}

async function toggle(row) {
  await request.put(`/system/user/${row.id}/status?status=${row.status === 1 ? 0 : 1}`)
  ElMessage.success('状态已更新')
  loadUsers()
}

async function pickRole(r) {
  currentRole.value = r
  roleId.value = r.id
  const ids = await request.get(`/system/role/${r.id}/menus`)
  treeRef.value?.setCheckedKeys(ids)
}

async function saveMenus() {
  const keys = treeRef.value.getCheckedKeys().concat(treeRef.value.getHalfCheckedKeys())
  await request.post(`/system/role/${roleId.value}/menus`, { menuIds: keys })
  ElMessage.success('授权已保存，相关用户需重新登录生效')
}

onMounted(async () => {
  roles.value = await request.get('/system/roles')
  orgs.value = await request.get('/system/orgs')
  menus.value = await request.get('/system/menus')
  await loadUsers()
  await loadLogs()
  if (roles.value.length) await pickRole(roles.value[0])
})
</script>

<style scoped>
.role-box { display: flex; gap: 24px; }
.role-list { width: 220px; flex: 0 0 220px; border-right: 1px solid var(--line); padding-right: 16px; }
.rl-title { font-size: 13px; color: var(--text-2); margin-bottom: 10px; }
.rl-item { padding: 9px 10px; border-radius: 6px; cursor: pointer; margin-bottom: 4px; }
.rl-item b { display: block; font-size: 13.5px; font-weight: 500; }
.rl-item span { font-size: 12px; color: var(--text-2); }
.rl-item.on { background: #EAF2F8; }
.rl-item.on b { color: var(--primary); }
.role-menu { flex: 1; min-width: 0; }
</style>
'''

F["Profile.vue"] = r'''<template>
  <div>
    <h1 class="page-title">个人中心</h1>
    <p class="page-sub">修改资料、密码与头像；头像上传成功后左上角与顶栏同步更新</p>

    <div class="profile">
      <div class="panel" style="flex:0 0 320px">
        <div class="panel-bd center">
          <img :src="user.avatar || '/uploads/seed/avatar/01.jpg'" class="avatar-big" alt="头像" />
          <div class="nm">{{ user.realName }}</div>
          <div class="rl">{{ user.roleName }} · {{ user.orgName }}</div>
          <el-upload :action="uploadUrl" :headers="uploadHeaders" :show-file-list="false" accept="image/*" :on-success="onAvatar">
            <el-button size="small" style="margin-top:12px">更换头像</el-button>
          </el-upload>
        </div>
      </div>

      <div class="panel" style="flex:1">
        <div class="panel-hd"><span>基本资料</span></div>
        <div class="panel-bd">
          <el-form :model="form" label-width="100px" label-position="left" style="max-width:520px">
            <el-form-item label="账号"><el-input v-model="user.username" disabled /></el-form-item>
            <el-form-item label="姓名"><el-input v-model="form.realName" /></el-form-item>
            <el-form-item label="联系电话"><el-input v-model="form.phone" /></el-form-item>
            <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
            <el-button type="primary" :loading="saving" @click="saveProfile">保存资料</el-button>
          </el-form>
        </div>
      </div>

      <div class="panel" style="flex:1">
        <div class="panel-hd"><span>修改密码</span></div>
        <div class="panel-bd">
          <el-form :model="pwd" label-width="100px" label-position="left" style="max-width:520px">
            <el-form-item label="原密码"><el-input v-model="pwd.oldPassword" type="password" show-password /></el-form-item>
            <el-form-item label="新密码"><el-input v-model="pwd.newPassword" type="password" show-password placeholder="至少 6 位" /></el-form-item>
            <el-form-item label="确认新密码"><el-input v-model="pwd.confirm" type="password" show-password /></el-form-item>
            <el-button type="primary" @click="changePwd">修改密码</el-button>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { loadMe, store } from '@/store/user'

const user = reactive({})
const form = reactive({ realName: '', phone: '', email: '' })
const pwd = reactive({ oldPassword: '', newPassword: '', confirm: '' })
const saving = ref(false)
const uploadUrl = '/api/file/upload'
const uploadHeaders = computed(() => ({ Authorization: 'Bearer ' + localStorage.getItem('token') }))

const onAvatar = async res => {
  if (res.code !== 200) { ElMessage.error('上传失败'); return }
  await request.put('/auth/avatar', { avatar: res.data })
  user.avatar = res.data
  if (store.user) store.user.avatar = res.data
  ElMessage.success('头像已更新')
}

async function saveProfile() {
  saving.value = true
  try {
    await request.put('/auth/profile', form)
    ElMessage.success('资料已保存')
    await loadMe(true)
    Object.assign(user, store.user)
  } finally { saving.value = false }
}

async function changePwd() {
  if (!pwd.newPassword || pwd.newPassword.length < 6) { ElMessage.warning('新密码至少 6 位'); return }
  if (pwd.newPassword !== pwd.confirm) { ElMessage.warning('两次输入的新密码不一致'); return }
  await request.put('/auth/password', { oldPassword: pwd.oldPassword, newPassword: pwd.newPassword })
  ElMessage.success('密码已修改')
  Object.assign(pwd, { oldPassword: '', newPassword: '', confirm: '' })
}

onMounted(async () => {
  await loadMe()
  Object.assign(user, store.user)
  Object.assign(form, { realName: user.realName, phone: user.phone, email: user.email })
})
</script>

<style scoped>
.profile { display: flex; gap: 16px; align-items: flex-start; flex-wrap: wrap; }
.center { text-align: center; }
.avatar-big { width: 96px; height: 96px; border-radius: 50%; object-fit: cover; border: 2px solid #fff; box-shadow: 0 0 0 1px var(--line); }
.nm { font-size: 16px; font-weight: 600; margin-top: 10px; }
.rl { font-size: 12.5px; color: var(--text-2); }
</style>
'''

F["Portal.vue"] = r'''<template>
  <div class="portal">
    <header class="ptop">
      <div class="pleft">
        <b>灌溉用水 · 种植户</b>
        <nav>
          <span :class="{ on: tab === 'land' }" @click="tab = 'land'">我的地块</span>
          <span :class="{ on: tab === 'apply' }" @click="tab = 'apply'">用水申请</span>
          <span :class="{ on: tab === 'fee' }" @click="tab = 'fee'">我的费用</span>
        </nav>
      </div>
      <div class="pright">
        <img :src="user.avatar" class="pa" alt="头像" />
        <span>{{ user.realName }}</span>
        <a href="javascript:;" @click="goBack">进入管理端</a>
        <a href="javascript:;" @click="doLogout">退出</a>
      </div>
    </header>

    <div class="pbody">
      <div class="hero">
        <h2>{{ user.orgName || '灌区' }} · {{ user.realName }}</h2>
        <p>2026 年度定额 {{ num(sum.quota, 0) }} m³，已使用 {{ num(sum.used, 0) }} m³，剩余 {{ num(sum.remain, 0) }} m³（使用率 {{ percent(sum.rate) }}）</p>
        <div class="stat">
          <div><b>{{ lands.length }}</b><span>承包地块</span></div>
          <div><b>{{ num(sum.area, 1) }}</b><span>灌溉面积（亩）</span></div>
          <div><b>{{ apps.length }}</b><span>本年申请</span></div>
          <div><b>{{ money(sum.fee) }}</b><span>本年费用</span></div>
        </div>
      </div>

      <section v-show="tab === 'land'">
        <div class="pcard">
          <div class="pcard-hd">我的地块</div>
          <div class="lands">
            <div class="land" v-for="f in lands" :key="f.id">
              <img :src="f.photo" alt="地块照片" />
              <div class="land-bd">
                <b>{{ f.name }}</b>
                <span class="tag" :class="tagOf(f.status)">{{ text(f.status) }}</span>
                <p>{{ f.crop }} · {{ f.growthStage }} · {{ num(f.area, 2) }} 亩<br/>{{ f.soilType }} · {{ f.irrigationType }}</p>
                <el-button size="small" type="primary" plain @click="quickApply(f)">申请用水</el-button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section v-show="tab === 'apply'">
        <div class="pcard">
          <div class="pcard-hd">我的用水申请 <el-button size="small" type="primary" @click="openApply">提交申请</el-button></div>
          <el-table :data="apps" border stripe>
            <el-table-column prop="code" label="申请编号" min-width="150" />
            <el-table-column prop="farmlandName" label="地块" min-width="130" />
            <el-table-column prop="expectDate" label="期望日期" min-width="104" />
            <el-table-column label="申请水量(m³)" min-width="118" align="right">
              <template #default="{ row }">{{ num(row.applyVolume, 1) }}</template>
            </el-table-column>
            <el-table-column label="状态" min-width="92">
              <template #default="{ row }"><span class="tag" :class="tagOf(row.status)">{{ text(row.status) }}</span></template>
            </el-table-column>
            <el-table-column label="审核意见" min-width="200" show-overflow-tooltip>
              <template #default="{ row }">{{ row.auditOpinion || '—' }}</template>
            </el-table-column>
          </el-table>
        </div>
      </section>

      <section v-show="tab === 'fee'">
        <div class="pcard">
          <div class="pcard-hd">我的费用</div>
          <el-table :data="fees" border stripe>
            <el-table-column prop="code" label="费用单号" min-width="150" />
            <el-table-column prop="farmlandName" label="地块" min-width="130" />
            <el-table-column label="实际水量(m³)" min-width="118" align="right">
              <template #default="{ row }">{{ num(row.actualVolume, 1) }}</template>
            </el-table-column>
            <el-table-column label="超额(m³)" min-width="96" align="right">
              <template #default="{ row }">
                <span :style="{ color: Number(row.excessVolume) > 0 ? '#B22B31' : '#1D2A33' }">{{ num(row.excessVolume, 1) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="金额" min-width="106" align="right">
              <template #default="{ row }">{{ money(row.amount) }}</template>
            </el-table-column>
            <el-table-column prop="billMonth" label="计费月份" min-width="96" />
            <el-table-column label="状态" min-width="90">
              <template #default="{ row }"><span class="tag" :class="tagOf(row.status)">{{ text(row.status) }}</span></template>
            </el-table-column>
          </el-table>
        </div>
      </section>
    </div>

    <el-dialog v-model="applyVisible" title="提交用水申请" width="480px">
      <el-form :model="applyForm" label-width="100px" label-position="left">
        <el-form-item label="地块" required>
          <el-select v-model="applyForm.farmlandId" style="width:100%">
            <el-option v-for="f in lands" :key="f.id" :label="`${f.name}（${f.crop}）`" :value="f.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="期望日期" required>
          <el-date-picker v-model="applyForm.expectDate" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="申请水量" required>
          <el-input-number v-model="applyForm.applyVolume" :min="1" :step="100" style="width:100%" />
        </el-form-item>
        <el-form-item label="紧急程度">
          <el-radio-group v-model="applyForm.urgency">
            <el-radio value="NORMAL">普通</el-radio>
            <el-radio value="URGENT">紧急</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="applyVisible = false">取消</el-button>
        <el-button type="primary" @click="submitApply">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import request from '@/utils/request'
import { money, num, percent, text, STATUS_TYPE } from '@/utils/format'
import { loadMe, store, logout } from '@/store/user'

const router = useRouter()
const tab = ref('land')
const user = reactive({})
const lands = ref([])
const apps = ref([])
const fees = ref([])
const quotas = ref([])
const applyVisible = ref(false)
const today = new Date().toISOString().slice(0, 10)
const applyForm = reactive({ farmlandId: null, expectDate: today, applyVolume: 800, urgency: 'NORMAL' })

const tagOf = s => 'tag ' + (STATUS_TYPE[s] || 'info')
const sum = computed(() => {
  let quota = 0, used = 0, area = 0, fee = 0
  quotas.value.forEach(q => { quota += Number(q.quotaVolume || 0); used += Number(q.usedVolume || 0); area += Number(q.area || 0) })
  fees.value.forEach(f => { fee += Number(f.amount || 0) })
  return { quota, used, remain: quota - used, rate: quota ? (used / quota) * 100 : 0, area, fee }
})

async function loadAll() {
  const f = await request.get('/farmland/page', { params: { page: 1, size: 50 } })
  lands.value = f.records || []
  const a = await request.get('/application/page', { params: { page: 1, size: 20 } })
  apps.value = a.records || []
  const fe = await request.get('/fee/page', { params: { page: 1, size: 20 } })
  fees.value = fe.records || []
  const q = await request.get('/quota/page', { params: { page: 1, size: 50, year: 2026 } })
  quotas.value = q.records || []
}

function quickApply(f) {
  applyForm.farmlandId = f.id
  applyForm.applyVolume = Math.round(Number(f.area) * 15)
  applyVisible.value = true
}

const openApply = () => quickApply(lands.value[0] || {})

async function submitApply() {
  if (!applyForm.farmlandId) { ElMessage.warning('请选择地块'); return }
  await request.post('/application', applyForm)
  ElMessage.success('申请已提交，等待审核')
  applyVisible.value = false
  loadAll()
}

const goBack = () => router.push('/dashboard')
const doLogout = () => logout()

onMounted(async () => {
  await loadMe()
  Object.assign(user, store.user)
  await loadAll()
})
</script>

<style scoped>
.portal { min-height: 100vh; background: var(--bg); }
.ptop { height: 60px; background: #fff; border-bottom: 1px solid var(--line); display: flex; align-items: center; justify-content: space-between; padding: 0 32px; }
.pleft { display: flex; align-items: center; gap: 34px; }
.pleft b { font-size: 17px; color: var(--primary); }
.pleft nav { display: flex; gap: 26px; font-size: 14px; }
.pleft nav span { color: var(--text-2); cursor: pointer; padding: 19px 0; }
.pleft nav span.on { color: var(--primary); font-weight: 500; border-bottom: 2px solid var(--primary); }
.pright { display: flex; align-items: center; gap: 14px; font-size: 13px; color: var(--text-2); }
.pa { width: 30px; height: 30px; border-radius: 50%; object-fit: cover; }
.pbody { max-width: 1180px; margin: 0 auto; padding: 24px 24px 40px; }
.hero { background: linear-gradient(120deg, #0F3B5D, #245A7A); color: #fff; border-radius: 10px; padding: 24px 28px; margin-bottom: 18px; }
.hero h2 { font-size: 21px; font-weight: 600; margin: 0 0 6px; }
.hero p { font-size: 13.5px; color: rgba(255,255,255,.78); margin: 0; }
.stat { display: flex; gap: 44px; margin-top: 18px; }
.stat b { display: block; font-size: 23px; font-weight: 600; font-variant-numeric: tabular-nums; }
.stat span { font-size: 12.5px; color: rgba(255,255,255,.68); }
.pcard { background: #fff; border: 1px solid var(--line); border-radius: 8px; padding: 16px 18px; }
.pcard-hd { display: flex; justify-content: space-between; align-items: center; font-size: 15px; font-weight: 600; margin-bottom: 14px; }
.lands { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.land { border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }
.land img { width: 100%; height: 118px; object-fit: cover; display: block; }
.land-bd { padding: 12px 14px; }
.land-bd b { font-size: 14px; margin-right: 6px; }
.land-bd p { font-size: 12.5px; color: var(--text-2); line-height: 1.8; margin: 6px 0 10px; }
</style>
'''

for name, content in F.items():
    (DIR / name).write_text(content)
print("生成页面", len(F), list(F))
