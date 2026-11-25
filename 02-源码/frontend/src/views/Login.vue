<template>
  <div class="login">
    <div class="left">
      <div class="bg" :style="{ backgroundImage: `url(${bg})` }"></div>
      <div class="veil"></div>
      <div class="brand">
        <svg width="22" height="22" viewBox="0 0 24 24"><path d="M12 3s6 6.5 6 11a6 6 0 11-12 0c0-4.5 6-11 6-11z" fill="#7FB3D5"/></svg>
        灌区用水管理平台
      </div>
      <div class="copy">
        <h1>把每一方水<br />都算到地块上</h1>
        <p>水源、干支渠、闸口、水表一体化台账；计划排程自动校验闸口容量与时段冲突；抄表数据驱动定额扣减、分段计费与用水建议。</p>
      </div>
      <div class="facts">
        <div><b>1.2 万亩</b><span>覆盖灌溉面积</span></div>
        <div><b>126</b><span>在册地块</span></div>
        <div><b>98.4%</b><span>计划完成率</span></div>
      </div>
    </div>

    <div class="right">
      <div class="card">
        <h2>{{ mode === 'login' ? '登录' : '注册种植户账号' }}</h2>
        <p class="tip">{{ mode === 'login' ? '使用灌区分配的账号登录，连续 5 次失败将锁定 10 分钟' : '注册后默认绑定种植户角色，可提交用水申请与查看费用' }}</p>

        <el-form :model="form" label-position="top" @submit.prevent>
          <el-form-item label="账号">
            <el-input v-model="form.username" size="large" placeholder="请输入账号" />
          </el-form-item>
          <el-form-item v-if="mode === 'register'" label="姓名">
            <el-input v-model="form.realName" size="large" placeholder="请输入真实姓名" />
          </el-form-item>
          <el-form-item v-if="mode === 'register'" label="手机号">
            <el-input v-model="form.phone" size="large" placeholder="选填，用于接收通知" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="form.password" type="password" size="large" show-password
                      placeholder="请输入密码" @keyup.enter="submit" />
          </el-form-item>
          <div class="row">
            <el-checkbox v-model="form.remember">记住账号</el-checkbox>
            <a href="javascript:;">忘记密码</a>
          </div>
          <el-button type="primary" size="large" class="submit" :loading="loading" @click="submit">
            {{ mode === 'login' ? '登 录' : '注 册' }}
          </el-button>
        </el-form>

        <div class="switch">
          <span v-if="mode === 'login'">还没有账号？<a href="javascript:;" @click="toggle">注册种植户</a></span>
          <span v-else>已有账号？<a href="javascript:;" @click="toggle">返回登录</a></span>
        </div>

        <div class="hint">
          <span v-for="h in hints" :key="h.u" @click="fill(h)">{{ h.t }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const mode = ref('login')
const loading = ref(false)
const bg = '/uploads/seed/login/01.jpg'

const form = reactive({
  username: 'admin',
  password: 'admin123',
  realName: '',
  phone: '',
  remember: true
})

const hints = [
  { t: '管理员 admin', u: 'admin', p: 'admin123' },
  { t: '调度员 dispatcher01', u: 'dispatcher01', p: 'admin123' },
  { t: '放水员 operator01', u: 'operator01', p: 'admin123' },
  { t: '种植户 farmer01', u: 'farmer01', p: 'admin123' }
]

const fill = h => {
  mode.value = 'login'
  form.username = h.u
  form.password = h.p
}

const toggle = () => {
  mode.value = mode.value === 'login' ? 'register' : 'login'
}

const submit = async () => {
  if (!form.username || !form.password) {
    ElMessage.warning('请输入账号与密码')
    return
  }
  loading.value = true
  try {
    if (mode.value === 'register') {
      await request.post('/auth/register', {
        username: form.username,
        password: form.password,
        realName: form.realName,
        phone: form.phone
      })
      ElMessage.success('注册成功，请登录')
      mode.value = 'login'
      return
    }
    const data = await request.post('/auth/login', {
      username: form.username,
      password: form.password
    })
    localStorage.setItem('token', data.token)
    if (form.remember) localStorage.setItem('lastUser', form.username)
    ElMessage.success('欢迎回来，' + (data.user.realName || data.user.username))
    const role = data.user.roleId === 4 ? 'farmer' : 'staff'
    router.push(role === 'farmer' ? '/portal' : '/dashboard')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login { min-height: 100vh; display: grid; grid-template-columns: 1.05fr .95fr; background: var(--bg); }
.left { position: relative; overflow: hidden; padding: 54px; display: flex; flex-direction: column; justify-content: space-between; color: #fff; }
.bg { position: absolute; inset: 0; background-size: cover; background-position: center; }
.veil { position: absolute; inset: 0; background: linear-gradient(150deg, rgba(15,59,93,.94) 0%, rgba(27,79,115,.86) 55%, rgba(36,90,122,.78) 100%); }
.brand, .copy, .facts { position: relative; z-index: 1; }
.brand { display: flex; align-items: center; gap: 10px; font-size: 16px; font-weight: 600; letter-spacing: .5px; }
.copy h1 { font-size: 34px; line-height: 1.35; font-weight: 600; margin: 0 0 16px; }
.copy p { font-size: 14px; line-height: 1.9; color: rgba(255,255,255,.76); max-width: 420px; margin: 0; }
.facts { display: flex; gap: 36px; }
.facts b { display: block; font-size: 26px; font-weight: 600; font-variant-numeric: tabular-nums; }
.facts span { font-size: 12.5px; color: rgba(255,255,255,.62); }
.right { display: grid; place-items: center; padding: 40px; }
.card { width: 390px; }
.card h2 { font-size: 22px; font-weight: 600; margin: 0 0 6px; }
.tip { font-size: 13px; color: var(--text-2); margin: 0 0 22px; line-height: 1.7; }
.row { display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: var(--text-2); margin: 2px 0 18px; }
.submit { width: 100%; height: 44px; font-size: 15px; letter-spacing: 2px; }
.switch { font-size: 13px; color: var(--text-2); margin-top: 14px; text-align: center; }
.hint { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 22px; }
.hint span { font-size: 12px; color: var(--text-2); border: 1px solid var(--line); background: #fff; border-radius: 4px; padding: 3px 9px; cursor: pointer; }
.hint span:hover { border-color: var(--secondary); color: var(--secondary); }
@media (max-width: 1080px) {
  .login { grid-template-columns: 1fr; }
  .left { display: none; }
}
</style>
