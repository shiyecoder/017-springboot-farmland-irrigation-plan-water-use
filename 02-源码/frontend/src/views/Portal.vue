<template>
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
