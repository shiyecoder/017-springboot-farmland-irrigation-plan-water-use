<template>
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
