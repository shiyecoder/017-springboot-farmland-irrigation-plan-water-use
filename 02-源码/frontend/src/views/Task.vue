<template>
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
            <el-table-column label="现场照片" min-width="90">
              <template #default="{ row }">
                <img v-if="row.photo" :src="row.photo" class="row-img" alt="现场照片" />
                <span v-else style="color:#B6C4D0">—</span>
              </template>
            </el-table-column>
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
            <el-table-column label="操作" min-width="120" fixed="right">
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
.row-img { width: 56px; height: 42px; object-fit: cover; border-radius: 4px; border: 1px solid var(--line); display: block; }
.exec-head { display: flex; justify-content: space-between; align-items: center; font-size: 15px; }
.exec-sub { font-size: 12.5px; color: var(--text-2); margin: 4px 0 14px; }
.uploader { display: flex; align-items: center; gap: 12px; }
.thumb { width: 72px; height: 54px; object-fit: cover; border-radius: 6px; border: 1px solid var(--line); }
.big-img { width: 100%; max-height: 220px; object-fit: cover; border-radius: 8px; border: 1px solid var(--line); margin-top: 12px; }
.sub-h { font-size: 14px; margin: 18px 0 10px; }
</style>
