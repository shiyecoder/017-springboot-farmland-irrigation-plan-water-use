# -*- coding: utf-8 -*-
"""批量生成业务页面：列表 + 抽屉表单 + 行内操作，统一分页与状态标签。"""
import pathlib

DIR = pathlib.Path("/Users/xiaoxin/showcase/build/NEW-017/frontend/src/views")
F = {}

F["Application.vue"] = r'''<template>
  <div>
    <h1 class="page-title">用水申请</h1>
    <p class="page-sub">种植户提交申请 → 灌区管理员审核 → 调度员排程；超定额需勾选超额审批后通过</p>

    <div class="panel">
      <div class="panel-bd">
        <div class="filters">
          <el-select v-model="query.status" placeholder="全部状态" clearable>
            <el-option label="待审核" value="PENDING_AUDIT" />
            <el-option label="待排程" value="PENDING_SCHEDULE" />
            <el-option label="已安排" value="SCHEDULED" />
            <el-option label="已驳回" value="REJECTED" />
          </el-select>
          <el-input v-model="query.keyword" placeholder="申请编号 / 申请人" clearable @keyup.enter="search" />
          <el-button type="primary" @click="search">查询</el-button>
          <el-button @click="reset">重置</el-button>
          <el-button type="primary" style="margin-left:auto" @click="openCreate">提交申请</el-button>
        </div>
        <div class="table-wrap">
          <el-table :data="rows" v-loading="loading" border stripe>
            <el-table-column prop="code" label="申请编号" min-width="150" />
            <el-table-column prop="farmlandName" label="地块" min-width="130" />
            <el-table-column label="作物 / 阶段" min-width="130">
              <template #default="{ row }">{{ row.crop }} / {{ row.growthStage }}</template>
            </el-table-column>
            <el-table-column prop="expectDate" label="期望日期" min-width="104" />
            <el-table-column label="申请水量(m³)" min-width="112" align="right">
              <template #default="{ row }"><span class="num">{{ num(row.applyVolume, 2) }}</span></template>
            </el-table-column>
            <el-table-column label="紧急程度" min-width="92">
              <template #default="{ row }">
                <span class="tag" :class="row.urgency === 'URGENT' ? 'bad' : 'info'">{{ URGENCY[row.urgency] }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="applicantName" label="申请人" min-width="88" />
            <el-table-column label="状态" min-width="88">
              <template #default="{ row }"><span class="tag" :class="tagOf(row.status)">{{ text(row.status) }}</span></template>
            </el-table-column>
            <el-table-column label="操作" min-width="110" fixed="right">
              <template #default="{ row }">
                <el-button v-if="row.status === 'PENDING_AUDIT'" link type="primary" @click="openAudit(row)">审核</el-button>
                <el-button v-else link type="primary" @click="showDetail(row)">详情</el-button>
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

    <el-drawer v-model="createVisible" title="提交用水申请" size="480px">
      <el-form :model="form" label-width="100px" label-position="left">
        <el-form-item label="地块" required>
          <el-select v-model="form.farmlandId" filterable style="width:100%" placeholder="选择地块">
            <el-option v-for="f in farmlands" :key="f.id" :label="`${f.name}（${f.crop} ${f.growthStage}）`" :value="f.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="期望日期" required>
          <el-date-picker v-model="form.expectDate" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="申请水量" required>
          <el-input-number v-model="form.applyVolume" :min="1" :precision="2" :step="50" style="width:100%" />
        </el-form-item>
        <el-form-item label="紧急程度">
          <el-radio-group v-model="form.urgency">
            <el-radio value="NORMAL">普通</el-radio>
            <el-radio value="URGENT">紧急</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="选填，说明用水缘由" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submit">提交</el-button>
      </template>
    </el-drawer>

    <el-drawer v-model="auditVisible" title="审核用水申请" size="520px">
      <template v-if="current">
        <div class="audit-top">
          <b>{{ current.code }}</b>
          <span class="tag blue">待审核</span>
        </div>
        <dl>
          <div class="kv"><dt>地块</dt><dd>{{ current.farmlandName }} · {{ num(current.area, 2) }} 亩</dd></div>
          <div class="kv"><dt>作物阶段</dt><dd>{{ current.crop }} / {{ current.growthStage }}</dd></div>
          <div class="kv"><dt>申请水量</dt><dd>{{ num(current.applyVolume, 2) }} m³</dd></div>
          <div class="kv"><dt>期望日期</dt><dd>{{ current.expectDate }} · {{ URGENCY[current.urgency] }}</dd></div>
          <div class="kv"><dt>申请人</dt><dd>{{ current.applicantName }}</dd></div>
        </dl>
        <el-form label-width="100px" label-position="left" style="margin-top:14px">
          <el-form-item label="审核意见">
            <el-input v-model="audit.opinion" type="textarea" :rows="3" placeholder="驳回时必填，不少于 5 个字" />
          </el-form-item>
          <el-form-item label="超额审批">
            <el-checkbox v-model="audit.approveOverQuota">申请水量超出定额余量，走超额审批</el-checkbox>
          </el-form-item>
        </el-form>
      </template>
      <template #footer>
        <el-button type="danger" plain @click="doAudit(false)">驳回</el-button>
        <el-button type="primary" :loading="saving" @click="doAudit(true)">通过并转排程</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { num, text, URGENCY, STATUS_TYPE } from '@/utils/format'

const rows = ref([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const createVisible = ref(false)
const auditVisible = ref(false)
const current = ref(null)
const farmlands = ref([])

const query = reactive({ status: '', keyword: '', page: 1, size: 10 })
const form = reactive({ farmlandId: null, expectDate: '', applyVolume: 1000, urgency: 'NORMAL', remark: '' })
const audit = reactive({ opinion: '', approveOverQuota: false })

const tagOf = s => 'tag ' + (STATUS_TYPE[s] || 'info')
const today = new Date().toISOString().slice(0, 10)

async function load() {
  loading.value = true
  try {
    const data = await request.get('/application/page', { params: query })
    rows.value = data.records || []
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}
const search = () => { query.page = 1; load() }
const onSize = () => { query.page = 1; load() }
const reset = () => { Object.assign(query, { status: '', keyword: '', page: 1 }); load() }

async function openCreate() {
  if (!farmlands.value.length) {
    const data = await request.get('/farmland/page', { params: { page: 1, size: 50 } })
    farmlands.value = data.records || []
  }
  Object.assign(form, { farmlandId: farmlands.value[0]?.id || null, expectDate: today, applyVolume: 1000, urgency: 'NORMAL', remark: '' })
  createVisible.value = true
}

async function submit() {
  if (!form.farmlandId) { ElMessage.warning('请选择地块'); return }
  saving.value = true
  try {
    await request.post('/application', form)
    ElMessage.success('申请已提交，等待审核')
    createVisible.value = false
    load()
  } finally { saving.value = false }
}

function openAudit(row) {
  current.value = row
  Object.assign(audit, { opinion: '', approveOverQuota: false })
  auditVisible.value = true
}

async function doAudit(pass) {
  if (!pass && (!audit.opinion || audit.opinion.trim().length < 5)) {
    ElMessage.warning('驳回原因不少于 5 个字')
    return
  }
  saving.value = true
  try {
    await request.post(`/application/${current.value.id}/audit`, { pass, opinion: audit.opinion, approveOverQuota: audit.approveOverQuota })
    ElMessage.success(pass ? '已通过，转调度排程' : '已驳回')
    auditVisible.value = false
    load()
  } finally { saving.value = false }
}

async function showDetail(row) {
  ElMessageBox.alert(
    `申请水量：${num(row.applyVolume, 2)} m³<br/>审核人：${row.auditBy || '—'}<br/>审核意见：${row.auditOpinion || '—'}`,
    row.code + ' ' + text(row.status),
    { dangerouslyUseHTMLString: true, confirmButtonText: '关闭' }
  )
}

onMounted(load)
</script>

<style scoped>
.audit-top { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; font-size:15px; }
</style>
'''

F["Quota.vue"] = r'''<template>
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
'''

F["Fee.vue"] = r'''<template>
  <div>
    <h1 class="page-title">费用台账</h1>
    <p class="page-sub">按实际用水量与分段单价核算；定额内执行基础价，超额部分加价，免费定额按亩折算</p>

    <div class="kpis four" style="margin-bottom:14px">
      <div class="kpi"><div class="lb">本月应收</div><div class="vl">{{ money(sum.totalAmount) }}</div></div>
      <div class="kpi"><div class="lb">已收金额</div><div class="vl">{{ money(sum.paidAmount) }}</div><div class="dt">收缴率 {{ sum.totalAmount ? percent(sum.paidAmount / sum.totalAmount * 100) : '0%' }}</div></div>
      <div class="kpi"><div class="lb">待收金额</div><div class="vl" style="color:#B4761E">{{ money(sum.unpaidAmount) }}</div></div>
      <div class="kpi"><div class="lb">超额加价金额</div><div class="vl" style="color:#B22B31">{{ money(sum.excessAmount) }}</div></div>
    </div>

    <div class="panel">
      <div class="panel-bd">
        <div class="notice info">
          计费规则：基础水价 {{ sum.basePrice }} 元/m³（定额内）· 超额水价 {{ sum.excessPrice }} 元/m³ · 免费定额 30 m³/亩/年
        </div>
        <div class="filters">
          <el-date-picker v-model="query.month" type="month" value-format="YYYY-MM" placeholder="计费月份" style="width:180px" @change="search" />
          <el-select v-model="query.status" placeholder="缴费状态" clearable>
            <el-option label="待缴费" value="UNPAID" />
            <el-option label="已缴费" value="PAID" />
            <el-option label="已减免" value="WAIVED" />
          </el-select>
          <el-input v-model="query.keyword" placeholder="费用单号 / 种植户" clearable @keyup.enter="search" />
          <el-button type="primary" @click="search">查询</el-button>
          <el-button @click="reset">重置</el-button>
        </div>
        <div class="table-wrap">
          <el-table :data="rows" v-loading="loading" border stripe>
            <el-table-column prop="code" label="费用单号" min-width="150" />
            <el-table-column prop="farmlandName" label="地块" min-width="130" />
            <el-table-column prop="taskCode" label="任务号" min-width="140" />
            <el-table-column prop="farmerName" label="种植户" min-width="86" />
            <el-table-column label="实际水量(m³)" min-width="112" align="right">
              <template #default="{ row }"><span class="num">{{ num(row.actualVolume, 2) }}</span></template>
            </el-table-column>
            <el-table-column label="定额内(m³)" min-width="104" align="right">
              <template #default="{ row }"><span class="num">{{ num(row.baseVolume, 2) }}</span></template>
            </el-table-column>
            <el-table-column label="超额(m³)" min-width="96" align="right">
              <template #default="{ row }">
                <span class="num" :style="{ color: Number(row.excessVolume) > 0 ? '#B22B31' : '#1D2A33' }">{{ num(row.excessVolume, 2) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="金额" min-width="104" align="right">
              <template #default="{ row }"><span class="num">{{ money(row.amount) }}</span></template>
            </el-table-column>
            <el-table-column prop="billMonth" label="计费月份" min-width="96" />
            <el-table-column label="状态" min-width="96">
              <template #default="{ row }"><span class="tag" :class="tagOf(row.status)">{{ text(row.status) }}</span></template>
            </el-table-column>
            <el-table-column label="操作" min-width="92" fixed="right">
              <template #default="{ row }">
                <el-button v-if="row.status === 'UNPAID'" link type="primary" @click="pay(row)">确认缴费</el-button>
                <span v-else style="color:#93A3B0;font-size:12.5px">—</span>
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
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { money, num, percent, text, STATUS_TYPE } from '@/utils/format'

const rows = ref([])
const total = ref(0)
const loading = ref(false)
const sum = reactive({ totalAmount: 0, paidAmount: 0, unpaidAmount: 0, excessAmount: 0, basePrice: 0.42, excessPrice: 0.55 })
const query = reactive({ month: '2026-10', status: '', keyword: '', page: 1, size: 10 })
const tagOf = s => 'tag ' + (STATUS_TYPE[s] || 'info')

async function load() {
  loading.value = true
  try {
    const data = await request.get('/fee/page', { params: query })
    rows.value = data.records || []
    total.value = data.total || 0
    Object.assign(sum, await request.get('/fee/summary', { params: { month: query.month } }))
  } finally { loading.value = false }
}
const search = () => { query.page = 1; load() }
const onSize = () => { query.page = 1; load() }
const reset = () => { Object.assign(query, { month: '2026-10', status: '', keyword: '', page: 1 }); load() }

async function pay(row) {
  await ElMessageBox.confirm(`确认费用单 ${row.code} 已缴纳 ${money(row.amount)}？`, '缴费确认', { type: 'warning' })
  await request.post(`/fee/${row.id}/pay`)
  ElMessage.success('已登记缴费')
  load()
}

onMounted(load)
</script>
'''

F["Source.vue"] = r'''<template>
  <div>
    <h1 class="page-title">水源与渠道</h1>
    <p class="page-sub">维护水源可用量、干支渠设计流量与闸口启闭状态，供计划编制时做容量校验</p>

    <div class="panel">
      <div class="panel-hd"><span>水源台账</span><el-button size="small" type="primary" @click="openForm()">新增水源</el-button></div>
      <div class="panel-bd flush">
        <div class="table-wrap">
          <el-table :data="sources" v-loading="loading" border stripe>
            <el-table-column prop="code" label="水源编号" min-width="104" />
            <el-table-column prop="name" label="水源名称" min-width="140" />
            <el-table-column label="类型" min-width="86">
              <template #default="{ row }">{{ SOURCE_TYPE[row.sourceType] || row.sourceType }}</template>
            </el-table-column>
            <el-table-column label="设计供水(m³/日)" min-width="132" align="right">
              <template #default="{ row }"><span class="num">{{ num(row.designSupply, 0) }}</span></template>
            </el-table-column>
            <el-table-column label="当前可用(m³)" min-width="120" align="right">
              <template #default="{ row }"><span class="num">{{ num(row.availableVolume, 0) }}</span></template>
            </el-table-column>
            <el-table-column prop="manager" label="负责人" min-width="88" />
            <el-table-column prop="phone" label="联系电话" min-width="120" />
            <el-table-column label="状态" min-width="96">
              <template #default="{ row }"><span class="tag" :class="tagOf(row.status)">{{ text(row.status) }}</span></template>
            </el-table-column>
            <el-table-column label="操作" min-width="80">
              <template #default="{ row }"><el-button link type="primary" @click="openForm(row)">编辑</el-button></template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-hd"><span>干支渠与闸口</span><span style="font-weight:400;font-size:12.5px;color:var(--text-2)">闸口容量用于计划冲突校验</span></div>
      <div class="panel-bd flush">
        <div class="table-wrap">
          <el-table :data="canals" border stripe>
            <el-table-column prop="code" label="渠道编号" min-width="100" />
            <el-table-column prop="name" label="渠道名称" min-width="130" />
            <el-table-column prop="sourceName" label="所属水源" min-width="140" />
            <el-table-column label="级别" min-width="80">
              <template #default="{ row }">{{ row.level === 'MAIN' ? '干渠' : '支渠' }}</template>
            </el-table-column>
            <el-table-column label="设计流量(m³/s)" min-width="126" align="right">
              <template #default="{ row }"><span class="num">{{ num(row.designFlow, 3) }}</span></template>
            </el-table-column>
            <el-table-column label="长度(km)" min-width="94" align="right">
              <template #default="{ row }"><span class="num">{{ num(row.lengthKm, 2) }}</span></template>
            </el-table-column>
            <el-table-column label="闸口" min-width="220">
              <template #default="{ row }">
                <span v-for="g in row.gates" :key="g.id" class="tag" :class="gateTag(g.status)" style="margin-right:4px">
                  {{ g.name }}（{{ num(g.designFlow, 2) }}）
                </span>
              </template>
            </el-table-column>
            <el-table-column label="状态" min-width="88">
              <template #default="{ row }"><span class="tag" :class="tagOf(row.status)">{{ text(row.status) }}</span></template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-hd"><span>水表台账</span><span style="font-weight:400;font-size:12.5px;color:var(--text-2)">共 {{ meterTotal }} 块</span></div>
      <div class="panel-bd flush">
        <div class="table-wrap">
          <el-table :data="meters" border stripe>
            <el-table-column prop="code" label="水表编号" min-width="100" />
            <el-table-column prop="name" label="水表名称" min-width="180" />
            <el-table-column label="初始读数" min-width="104" align="right">
              <template #default="{ row }"><span class="num">{{ num(row.initReading, 2) }}</span></template>
            </el-table-column>
            <el-table-column label="当前读数" min-width="104" align="right">
              <template #default="{ row }"><span class="num">{{ num(row.currentReading, 2) }}</span></template>
            </el-table-column>
            <el-table-column prop="installDate" label="安装日期" min-width="104" />
            <el-table-column label="表具照片" min-width="96">
              <template #default="{ row }"><img :src="row.photo" class="mini-img" alt="水表照片" /></template>
            </el-table-column>
            <el-table-column label="状态" min-width="84">
              <template #default="{ row }"><span class="tag" :class="tagOf(row.status)">{{ text(row.status) }}</span></template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>

    <el-dialog v-model="formVisible" :title="form.id ? '编辑水源' : '新增水源'" width="520px">
      <el-form :model="form" label-width="110px" label-position="left">
        <el-form-item label="水源编号" required><el-input v-model="form.code" :disabled="!!form.id" /></el-form-item>
        <el-form-item label="水源名称" required><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.sourceType" style="width:100%">
            <el-option label="水库" value="RESERVOIR" />
            <el-option label="机井" value="WELL" />
            <el-option label="河道" value="RIVER" />
            <el-option label="塘坝" value="POND" />
          </el-select>
        </el-form-item>
        <el-form-item label="设计供水"><el-input-number v-model="form.designSupply" :min="0" :step="500" style="width:100%" /></el-form-item>
        <el-form-item label="当前可用"><el-input-number v-model="form.availableVolume" :min="0" :step="100" style="width:100%" /></el-form-item>
        <el-form-item label="负责人"><el-input v-model="form.manager" /></el-form-item>
        <el-form-item label="联系电话"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width:100%">
            <el-option label="正常" value="NORMAL" />
            <el-option label="来水偏少" value="SHORT" />
            <el-option label="停用" value="STOP" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { num, text, SOURCE_TYPE, STATUS_TYPE } from '@/utils/format'

const sources = ref([])
const canals = ref([])
const meters = ref([])
const meterTotal = ref(0)
const loading = ref(false)
const formVisible = ref(false)
const form = reactive({ id: null, code: '', name: '', sourceType: 'RESERVOIR', designSupply: 0, availableVolume: 0, manager: '', phone: '', status: 'NORMAL', remark: '' })

const tagOf = s => 'tag ' + (STATUS_TYPE[s] || 'info')
const gateTag = s => (s === 'OPEN' ? 'ok' : (s === 'FAULT' ? 'bad' : 'info'))

async function load() {
  loading.value = true
  try {
    const data = await request.get('/base/source/page', { params: { page: 1, size: 20 } })
    sources.value = data.records || []
    canals.value = await request.get('/base/canals')
    const m = await request.get('/base/meter/page', { params: { page: 1, size: 12 } })
    meters.value = m.records || []
    meterTotal.value = m.total || 0
  } finally { loading.value = false }
}

function openForm(row) {
  Object.assign(form, {
    id: null, code: '', name: '', sourceType: 'RESERVOIR', designSupply: 0, availableVolume: 0,
    manager: '', phone: '', status: 'NORMAL', remark: ''
  })
  if (row) Object.assign(form, row)
  formVisible.value = true
}

async function save() {
  if (!form.code || !form.name) { ElMessage.warning('编号与名称必填'); return }
  await request.post('/base/source', form)
  ElMessage.success('保存成功')
  formVisible.value = false
  load()
}

onMounted(load)
</script>

<style scoped>
.mini-img { width: 54px; height: 38px; object-fit: cover; border-radius: 4px; border: 1px solid var(--line); }
</style>
'''

for name, content in F.items():
    (DIR / name).write_text(content)
print("生成页面", len(F), list(F))
