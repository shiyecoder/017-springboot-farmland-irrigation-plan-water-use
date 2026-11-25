<template>
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
