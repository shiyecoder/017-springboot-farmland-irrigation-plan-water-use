<template>
  <div>
    <h1 class="page-title">地块用水地图</h1>
    <p class="page-sub">按区域、作物、种植阶段与执行状态筛选地块，查看定额余量与最近一次灌溉</p>

    <div class="panel">
      <div class="panel-bd">
        <div class="filters">
          <el-select v-model="query.region" placeholder="全部区域" clearable>
            <el-option v-for="r in opts.regions" :key="r" :label="r" :value="r" />
          </el-select>
          <el-select v-model="query.crop" placeholder="全部作物" clearable>
            <el-option v-for="c in opts.crops" :key="c" :label="c" :value="c" />
          </el-select>
          <el-select v-model="query.growthStage" placeholder="全部阶段" clearable>
            <el-option v-for="s in opts.stages" :key="s" :label="s" :value="s" />
          </el-select>
          <el-select v-model="query.irrigationType" placeholder="全部灌溉方式" clearable>
            <el-option v-for="i in opts.irrigations" :key="i" :label="i" :value="i" />
          </el-select>
          <el-select v-model="query.status" placeholder="全部状态" clearable>
            <el-option label="正常" value="NORMAL" />
            <el-option label="休耕" value="FALLOW" />
            <el-option label="缺水" value="SHORT" />
            <el-option label="停用" value="STOP" />
          </el-select>
          <el-input v-model="query.keyword" placeholder="地块编号 / 名称" clearable @keyup.enter="search" />
          <el-button type="primary" @click="search">查询</el-button>
          <el-button @click="reset">重置</el-button>
        </div>

        <div class="kpis four">
          <div class="kpi"><div class="lb">在册地块</div><div class="vl">{{ total }}<small>块</small></div></div>
          <div class="kpi"><div class="lb">当前页灌溉面积</div><div class="vl">{{ num(pageArea, 1) }}<small>亩</small></div></div>
          <div class="kpi"><div class="lb">缺水 / 停用</div><div class="vl" style="color:#B4761E">{{ warnCount }}<small>块</small></div><div class="dt warn">需优先复核</div></div>
          <div class="kpi"><div class="lb">定额余量不足</div><div class="vl" style="color:#B22B31">{{ shortQuota }}<small>块</small></div><div class="dt bad">见水权定额</div></div>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-hd">
        <span>地块清单</span>
        <span style="font-weight:400;display:flex;gap:8px">
          <el-button size="small" @click="exportCsv">导出当前筛选</el-button>
          <el-button size="small" type="primary" @click="openForm()">新建地块</el-button>
        </span>
      </div>
      <div class="panel-bd flush">
        <div class="table-wrap">
          <el-table :data="rows" v-loading="loading" border stripe style="width:100%">
            <el-table-column prop="code" label="地块编号" min-width="128" />
            <el-table-column prop="name" label="地块名称" min-width="130" />
            <el-table-column label="照片" min-width="80">
              <template #default="{ row }">
                <img :src="row.photo || '/uploads/seed/farmland/01.jpg'" class="row-img" alt="地块照片" />
              </template>
            </el-table-column>
            <el-table-column label="面积(亩)" min-width="96" align="right">
              <template #default="{ row }"><span class="num">{{ num(row.area, 2) }}</span></template>
            </el-table-column>
            <el-table-column prop="crop" label="作物" min-width="76" />
            <el-table-column prop="growthStage" label="种植阶段" min-width="92" />
            <el-table-column prop="soilType" label="土壤类型" min-width="90" />
            <el-table-column prop="irrigationType" label="灌溉方式" min-width="96" />
            <el-table-column prop="ownerName" label="责任人" min-width="86" />
            <el-table-column label="状态" min-width="88">
              <template #default="{ row }">
                <span class="tag" :class="tagOf(row.status)">{{ text(row.status) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" min-width="172" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="openDetail(row)">查看</el-button>
                <el-button link type="primary" @click="openForm(row)">编辑</el-button>
                <el-button link type="danger" @click="remove(row)">删除</el-button>
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

    <!-- 新建 / 编辑抽屉 -->
    <el-drawer v-model="formVisible" :title="form.id ? '编辑地块' : '新建地块'" size="520px" :before-close="beforeClose">
      <el-form :model="form" label-width="100px" label-position="left">
        <el-form-item label="地块编号" required>
          <el-input v-model="form.code" :disabled="!!form.id" maxlength="50" placeholder="如 FD-2026-0031" />
        </el-form-item>
        <el-form-item label="地块名称" required>
          <el-input v-model="form.name" placeholder="如 北干渠一号地" />
        </el-form-item>
        <el-form-item label="面积(亩)" required>
          <el-input-number v-model="form.area" :min="0" :precision="2" :step="1" style="width:100%" />
        </el-form-item>
        <el-form-item label="作物" required>
          <el-select v-model="form.crop" style="width:100%">
            <el-option v-for="c in opts.crops" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item label="种植阶段" required>
          <el-select v-model="form.growthStage" style="width:100%">
            <el-option v-for="s in opts.stages" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="土壤类型" required>
          <el-select v-model="form.soilType" style="width:100%">
            <el-option v-for="s in opts.soils" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="灌溉方式">
          <el-select v-model="form.irrigationType" style="width:100%">
            <el-option v-for="i in opts.irrigations" :key="i" :label="i" :value="i" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属片区">
          <el-select v-model="form.region" style="width:100%">
            <el-option v-for="r in opts.regions" :key="r" :label="r" :value="r" />
          </el-select>
        </el-form-item>
        <el-form-item label="位置描述">
          <el-input v-model="form.address" placeholder="渠段、方位等" />
        </el-form-item>
        <el-form-item label="地块状态">
          <el-select v-model="form.status" style="width:100%">
            <el-option label="正常" value="NORMAL" />
            <el-option label="休耕" value="FALLOW" />
            <el-option label="缺水" value="SHORT" />
            <el-option label="停用" value="STOP" />
          </el-select>
        </el-form-item>
        <el-form-item label="地块照片">
          <div class="uploader">
            <img v-if="form.photo" :src="form.photo" class="thumb" alt="地块照片" />
            <el-upload :action="uploadUrl" :headers="uploadHeaders" :show-file-list="false"
                       accept="image/*" :on-success="onUploaded">
              <el-button size="small">{{ form.photo ? '重新上传' : '上传照片' }}</el-button>
            </el-upload>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-drawer>

    <!-- 详情抽屉：基础信息 + 定额 + 最近任务，不重复拼接列表 -->
    <el-drawer v-model="detailVisible" title="地块详情" size="560px">
      <template v-if="detail.farmland">
        <div class="detail-top">
          <div>
            <b>{{ detail.farmland.name }}</b>
            <span class="tag" :class="tagOf(detail.farmland.status)" style="margin-left:8px">{{ text(detail.farmland.status) }}</span>
            <div class="code">{{ detail.farmland.code }} · {{ detail.farmland.region }}</div>
          </div>
          <img :src="detail.farmland.photo" class="detail-img" alt="地块照片" />
        </div>
        <dl>
          <div class="kv"><dt>作物 / 阶段</dt><dd>{{ detail.farmland.crop }} / {{ detail.farmland.growthStage }}</dd></div>
          <div class="kv"><dt>面积</dt><dd>{{ num(detail.farmland.area, 2) }} 亩</dd></div>
          <div class="kv"><dt>土壤 / 方式</dt><dd>{{ detail.farmland.soilType }} · {{ detail.farmland.irrigationType }}</dd></div>
          <div class="kv"><dt>责任人</dt><dd>{{ detail.farmland.ownerName }}</dd></div>
          <div class="kv"><dt>位置</dt><dd>{{ detail.farmland.address || '—' }}</dd></div>
          <div class="kv"><dt>创建 / 更新</dt><dd>{{ formatTime(detail.farmland.createTime) }} / {{ formatTime(detail.farmland.updateTime) }}</dd></div>
        </dl>
        <h4 class="sub-h">年度定额</h4>
        <dl v-if="detail.quota">
          <div class="kv"><dt>定额水量</dt><dd>{{ num(detail.quota.quotaVolume, 2) }} m³</dd></div>
          <div class="kv"><dt>已用 / 剩余</dt><dd>{{ num(detail.quota.usedVolume, 2) }} / {{ num(detail.quota.remainingVolume, 2) }} m³</dd></div>
          <div class="kv"><dt>状态</dt><dd><span class="tag" :class="tagOf(detail.quota.status)">{{ text(detail.quota.status) }}</span></dd></div>
        </dl>
        <p v-else class="empty-tip">该地块尚未分配年度定额，请到「水权定额」页面分配。</p>
        <h4 class="sub-h">最近灌溉任务</h4>
        <el-table :data="detail.recentTasks || []" size="small" border>
          <el-table-column prop="code" label="任务号" min-width="130" />
          <el-table-column label="实际水量" min-width="96" align="right">
            <template #default="{ row }">{{ row.actualVolume ? num(row.actualVolume, 1) : '—' }}</template>
          </el-table-column>
          <el-table-column label="状态" min-width="84">
            <template #default="{ row }"><span class="tag" :class="tagOf(row.status)">{{ text(row.status) }}</span></template>
          </el-table-column>
        </el-table>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { formatTime, num, text, STATUS_TYPE } from '@/utils/format'

const rows = ref([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const formVisible = ref(false)
const detailVisible = ref(false)
const detail = reactive({})
const opts = reactive({ regions: [], crops: [], stages: [], soils: [], irrigations: [] })

const query = reactive({ region: '', crop: '', growthStage: '', irrigationType: '', status: '', keyword: '', page: 1, size: 10 })

const form = reactive({
  id: null, code: '', name: '', area: 0, crop: '', growthStage: '', soilType: '',
  irrigationType: '', region: '', address: '', status: 'NORMAL', photo: '', version: 0
})

const uploadUrl = '/api/file/upload'
const uploadHeaders = computed(() => ({ Authorization: 'Bearer ' + localStorage.getItem('token') }))

const pageArea = computed(() => rows.value.reduce((s, r) => s + Number(r.area || 0), 0))
const warnCount = computed(() => rows.value.filter(r => r.status === 'SHORT' || r.status === 'STOP').length)
const shortQuota = ref(0)

const tagOf = s => 'tag ' + (STATUS_TYPE[s] || 'info')

async function load() {
  loading.value = true
  try {
    const data = await request.get('/farmland/page', { params: query })
    rows.value = data.records || []
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}

const search = () => { query.page = 1; load() }
const onSize = () => { query.page = 1; load() }
const reset = () => {
  Object.assign(query, { region: '', crop: '', growthStage: '', irrigationType: '', status: '', keyword: '', page: 1 })
  load()
}

async function loadOptions() {
  const data = await request.get('/farmland/options')
  Object.assign(opts, data)
}

function openForm(row) {
  Object.assign(form, {
    id: null, code: '', name: '', area: 0, crop: opts.crops[0] || '', growthStage: opts.stages[0] || '',
    soilType: opts.soils[0] || '', irrigationType: opts.irrigations[0] || '', region: opts.regions[0] || '',
    address: '', status: 'NORMAL', photo: '', version: 0
  })
  if (row) Object.assign(form, row)
  formVisible.value = true
}

async function openDetail(row) {
  const data = await request.get('/farmland/' + row.id)
  Object.assign(detail, data)
  detailVisible.value = true
}

const onUploaded = res => {
  if (res.code === 200) {
    form.photo = res.data
    ElMessage.success('上传成功')
  } else {
    ElMessage.error(res.message || '上传失败')
  }
}

async function save() {
  if (!form.code || !form.name) {
    ElMessage.warning('地块编号与名称必填')
    return
  }
  saving.value = true
  try {
    if (form.id) {
      await request.put('/farmland/' + form.id, form)
    } else {
      await request.post('/farmland', form)
    }
    ElMessage.success('保存成功')
    formVisible.value = false
    load()
  } finally {
    saving.value = false
  }
}

async function remove(row) {
  await ElMessageBox.confirm(`确认删除地块「${row.name}」？删除前会检查是否被灌溉计划引用。`, '删除确认', { type: 'warning' })
  await request.delete('/farmland/' + row.id)
  ElMessage.success('已删除')
  load()
}

function beforeClose(done) {
  done()
}

function exportCsv() {
  const head = ['地块编号', '名称', '面积(亩)', '作物', '阶段', '土壤', '方式', '责任人', '状态']
  const lines = rows.value.map(r => [r.code, r.name, r.area, r.crop, r.growthStage, r.soilType, r.irrigationType, r.ownerName, text(r.status)])
  const csv = '\ufeff' + [head, ...lines].map(l => l.join(',')).join('\n')
  const a = document.createElement('a')
  a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }))
  a.download = '地块清单.csv'
  a.click()
  ElMessage.success('已导出当前筛选结果')
}

async function loadQuotaStat() {
  // 定额余量不足与超额地块数，按后端统计口径取，不在前端拼假数据
  const over = await request.get('/quota/page', { params: { page: 1, size: 1, year: 2026, status: 'OVER' } })
  const short = await request.get('/quota/page', { params: { page: 1, size: 1, year: 2026, status: 'SHORT' } })
  shortQuota.value = (over.total || 0) + (short.total || 0)
}

onMounted(async () => {
  await loadOptions()
  await load()
  loadQuotaStat()
})
</script>

<style scoped>
.row-img { width: 56px; height: 42px; object-fit: cover; border-radius: 4px; border: 1px solid var(--line); display: block; }
.uploader { display: flex; align-items: center; gap: 12px; }
.thumb { width: 72px; height: 54px; object-fit: cover; border-radius: 6px; border: 1px solid var(--line); }
.detail-top { display: flex; justify-content: space-between; gap: 16px; margin-bottom: 14px; }
.detail-top b { font-size: 16px; }
.detail-top .code { font-size: 12.5px; color: var(--text-2); margin-top: 4px; }
.detail-img { width: 132px; height: 96px; object-fit: cover; border-radius: 8px; border: 1px solid var(--line); }
.sub-h { font-size: 14px; margin: 20px 0 8px; }
.empty-tip { font-size: 13px; color: var(--text-2); background: #F8FBFD; border: 1px dashed var(--line); border-radius: 6px; padding: 12px; }
</style>
