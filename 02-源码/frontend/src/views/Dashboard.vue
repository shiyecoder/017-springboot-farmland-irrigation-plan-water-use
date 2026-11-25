<template>
  <div class="dash">
    <div class="head">
      <div>
        <h1 class="page-title">农业用水分析</h1>
        <p class="page-sub">统计区间 {{ rangeLabel }} · 数据来源：水表抄表与任务执行记录</p>
      </div>
      <div class="ranges">
        <span v-for="r in ranges" :key="r.key" :class="{ on: range === r.key }" @click="switchRange(r)">{{ r.label }}</span>
      </div>
    </div>

    <div class="kpis">
      <div class="kpi">
        <div class="lb">计划用水量</div>
        <div class="vl">{{ num(d.planVolume, 0) }}<small>m³</small></div>
        <div class="dt">完成率 {{ percent(d.finishRate) }}</div>
      </div>
      <div class="kpi">
        <div class="lb">实际用水量</div>
        <div class="vl">{{ num(d.actualVolume, 0) }}<small>m³</small></div>
        <div class="dt" :class="{ warn: overPlan }">{{ overPlan ? '超计划' : '低于计划' }} {{ percent(Math.abs(planDiff)) }}</div>
      </div>
      <div class="kpi">
        <div class="lb">定额偏差</div>
        <div class="vl">{{ percent(d.quotaDeviation) }}</div>
        <div class="dt" :class="{ warn: d.quotaDeviation < -10 }">按年度定额核算</div>
      </div>
      <div class="kpi">
        <div class="lb">计划完成率</div>
        <div class="vl">{{ percent(d.finishRate) }}</div>
        <div class="dt">已确认 {{ d.counts?.task || 0 }} 个任务</div>
      </div>
      <div class="kpi">
        <div class="lb">亩均用水</div>
        <div class="vl">{{ num(d.perMu, 1) }}<small>m³/亩</small></div>
        <div class="dt">涉及 {{ d.counts?.farmland || 0 }} 个地块</div>
      </div>
      <div class="kpi">
        <div class="lb">异常损失</div>
        <div class="vl" :style="{ color: d.lossVolume > 0 ? '#B22B31' : '#0F3B5D' }">{{ num(d.lossVolume, 0) }}<small>m³</small></div>
        <div class="dt" :class="{ bad: d.openException > 0 }">{{ d.openException || 0 }} 起待处理</div>
      </div>
    </div>

    <div class="charts">
      <div class="chart span2">
        <h4>近 30 天用水趋势 <em>实际确认水量 m³</em></h4>
        <div ref="c1" class="cv"></div>
      </div>
      <div class="chart">
        <h4>任务状态分布 <em>共 {{ d.counts?.task || 0 }} 个</em></h4>
        <div ref="c2" class="cv"></div>
      </div>
      <div class="chart">
        <h4>作物用水占比</h4>
        <div ref="c3" class="cv"></div>
      </div>
      <div class="chart">
        <h4>渠道时段负荷 <em>按计划水量</em></h4>
        <div ref="c4" class="cv"></div>
      </div>
      <div class="chart">
        <h4>地块单耗排行 <em>m³/亩</em></h4>
        <div ref="c5" class="cv"></div>
      </div>
    </div>
    <div class="charts second">
      <div class="chart">
        <h4>用水建议结果分布 <em>创新模块</em></h4>
        <div ref="c6" class="cv"></div>
      </div>
      <div class="chart span2">
        <h4>水源可供水量 <em>设计供水 vs 当前可用 m³</em></h4>
        <div ref="c7" class="cv"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, nextTick } from 'vue'
import * as echarts from 'echarts'
import request from '@/utils/request'
import { num, percent, text, STATUS_TEXT } from '@/utils/format'

const d = reactive({})
const range = ref('30d')
const charts = []
const c1 = ref(), c2 = ref(), c3 = ref(), c4 = ref(), c5 = ref(), c6 = ref(), c7 = ref()

const ranges = [
  { key: '30d', label: '近 30 天', days: 30 },
  { key: 'month', label: '本月', days: 30 },
  { key: 'quarter', label: '本季度', days: 92 },
  { key: 'year', label: '本年', days: 300 }
]

const rangeLabel = computed(() => ranges.find(r => r.key === range.value)?.label || '近 30 天')
const planDiff = computed(() => {
  const p = Number(d.planVolume || 0), a = Number(d.actualVolume || 0)
  return p === 0 ? 0 : ((a - p) / p) * 100
})
const overPlan = computed(() => planDiff.value > 0)

const PALETTE = ['#0F3B5D', '#2878B5', '#245A7A', '#5C8FAE', '#8FB3C7', '#1F7653', '#B4761E', '#B22B31']

function mk(el, option) {
  if (!el) return
  const chart = echarts.init(el)
  chart.setOption(option)
  charts.push(chart)
  return chart
}

const baseAxis = {
  axisLine: { lineStyle: { color: '#DCE6EE' } },
  axisLabel: { color: '#5A6B78', fontSize: 10.5 },
  axisTick: { show: false },
  splitLine: { lineStyle: { color: '#EDF3F8' } }
}

function render() {
  const trend = d.trend || []
  mk(c1.value, {
    grid: { left: 38, right: 10, top: 14, bottom: 22 },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: trend.map(t => t.date), ...baseAxis, splitLine: { show: false } },
    yAxis: { type: 'value', ...baseAxis },
    series: [{
      type: 'line', smooth: true, symbol: 'none',
      data: trend.map(t => Number(t.volume || 0)),
      lineStyle: { width: 2, color: '#0F3B5D' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(40,120,181,.28)' },
          { offset: 1, color: 'rgba(40,120,181,0)' }
        ])
      }
    }]
  })

  const st = d.statusDist || []
  mk(c2.value, {
    tooltip: { trigger: 'item', formatter: p => `${p.name}：${p.value} 个（${p.percent}%）` },
    legend: { bottom: 0, itemWidth: 8, itemHeight: 8, textStyle: { fontSize: 10.5, color: '#5A6B78' } },
    series: [{
      type: 'pie', radius: ['46%', '68%'], center: ['50%', '44%'],
      itemStyle: { borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      data: st.map((s, i) => ({ name: text(s.status), value: s.count, itemStyle: { color: PALETTE[i % 8] } }))
    }]
  })

  const crop = d.cropDist || []
  mk(c3.value, {
    grid: { left: 52, right: 34, top: 10, bottom: 12 },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'value', ...baseAxis, axisLabel: { show: false }, splitLine: { show: false } },
    yAxis: { type: 'category', data: crop.map(c => c.crop).reverse(), ...baseAxis, splitLine: { show: false } },
    series: [{
      type: 'bar', barWidth: 11,
      data: crop.map(c => Number(c.percent || 0)).reverse(),
      itemStyle: { color: '#2878B5', borderRadius: [0, 3, 3, 0] },
      label: { show: true, position: 'right', fontSize: 10.5, color: '#5A6B78', formatter: '{c}%' }
    }]
  })

  const load = d.gateLoad || []
  mk(c4.value, {
    grid: { left: 42, right: 10, top: 14, bottom: 24 },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: load.map(l => l.slot), ...baseAxis, splitLine: { show: false } },
    yAxis: { type: 'value', ...baseAxis },
    series: [{
      type: 'bar', barWidth: 18,
      data: load.map(l => Number(l.volume || 0)),
      itemStyle: { color: '#245A7A', borderRadius: [3, 3, 0, 0] }
    }]
  })

  const top = d.topLand || []
  mk(c5.value, {
    grid: { left: 66, right: 32, top: 10, bottom: 12 },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'value', ...baseAxis, axisLabel: { show: false }, splitLine: { show: false } },
    yAxis: { type: 'category', data: top.map(t => t.name).reverse(), ...baseAxis, splitLine: { show: false } },
    series: [{
      type: 'bar', barWidth: 11,
      data: top.map(t => Number(t.perMu || 0)).reverse(),
      itemStyle: { color: '#5C8FAE', borderRadius: [0, 3, 3, 0] },
      label: { show: true, position: 'right', fontSize: 10.5, color: '#5A6B78' }
    }]
  })

  const adv = d.adviceDist || []
  mk(c6.value, {
    grid: { left: 34, right: 10, top: 12, bottom: 26 },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: adv.map(a => text(a.grade)), ...baseAxis, splitLine: { show: false } },
    yAxis: { type: 'value', ...baseAxis },
    series: [{
      type: 'bar', barWidth: 22,
      data: adv.map((a, i) => ({
        value: a.count,
        itemStyle: { color: ['#1F7653', '#2878B5', '#B4761E', '#B22B31'][i], borderRadius: [3, 3, 0, 0] }
      }))
    }]
  })

  const src = d.sourceSupply || []
  mk(c7.value, {
    grid: { left: 44, right: 16, top: 14, bottom: 24 },
    tooltip: { trigger: 'axis' },
    legend: { top: 0, right: 0, itemWidth: 9, itemHeight: 9, textStyle: { fontSize: 10.5, color: '#5A6B78' } },
    xAxis: { type: 'category', data: src.map(s => s.name), ...baseAxis, splitLine: { show: false } },
    yAxis: { type: 'value', ...baseAxis },
    series: [
      { name: '设计供水', type: 'bar', barWidth: 14, data: src.map(s => Number(s.design || 0)), itemStyle: { color: '#8FB3C7', borderRadius: [3, 3, 0, 0] } },
      { name: '当前可用', type: 'bar', barWidth: 14, data: src.map(s => Number(s.available || 0)), itemStyle: { color: '#0F3B5D', borderRadius: [3, 3, 0, 0] } }
    ]
  })
}

function resize() {
  charts.forEach(c => c && c.resize())
}

async function load() {
  const r = ranges.find(x => x.key === range.value)
  const data = await request.get('/dashboard', { params: { days: r.days, range: range.value } })
  Object.assign(d, data)
  await nextTick()
  charts.forEach(c => c && c.dispose())
  charts.length = 0
  render()
}

function switchRange(r) {
  range.value = r.key
  load()
}

onMounted(async () => {
  await load()
  window.addEventListener('resize', resize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  charts.forEach(c => c && c.dispose())
})
</script>

<style scoped>
.head { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 12px; }
.head .page-title { margin-bottom: 2px; }
.head .page-sub { margin-bottom: 0; }
.ranges { display: flex; gap: 2px; background: #fff; border: 1px solid var(--line); border-radius: 6px; padding: 2px; }
.ranges span {
  font-size: 12.5px; color: var(--text-2); padding: 4px 11px; border-radius: 4px; cursor: pointer;
}
.ranges span.on { background: var(--primary); color: #fff; }
.chart.span2 { grid-column: span 2; }
.second { margin-top: 12px; }
.second .chart { padding-top: 10px; }
/* 一屏约束：1440×900 下不出现整页滚动，图表整体压缩 */
.dash { display: flex; flex-direction: column; }
.kpis { gap: 10px; margin-bottom: 12px; }
.kpis .kpi { padding: 10px 12px; }
.kpis .vl { font-size: 22px; }
.charts .chart .cv { height: 126px; }
.second .chart .cv { height: 118px; }
</style>
