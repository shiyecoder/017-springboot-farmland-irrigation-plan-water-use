<template>
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
