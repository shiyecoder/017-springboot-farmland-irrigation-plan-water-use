<template>
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
            <el-table-column label="现场照片" min-width="96">
              <template #default="{ row }">
                <img v-if="row.photo" :src="row.photo" class="mini-img" alt="水源照片" />
                <span v-else style="color:#B6C4D0">—</span>
              </template>
            </el-table-column>
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
