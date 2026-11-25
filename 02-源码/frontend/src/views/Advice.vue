<template>
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
