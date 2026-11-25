<template>
  <div>
    <h1 class="page-title">个人中心</h1>
    <p class="page-sub">修改资料、密码与头像；头像上传成功后左上角与顶栏同步更新</p>

    <div class="profile">
      <div class="panel" style="flex:0 0 320px">
        <div class="panel-bd center">
          <img :src="user.avatar || '/uploads/seed/avatar/01.jpg'" class="avatar-big" alt="头像" />
          <div class="nm">{{ user.realName }}</div>
          <div class="rl">{{ user.roleName }} · {{ user.orgName }}</div>
          <el-upload :action="uploadUrl" :headers="uploadHeaders" :show-file-list="false" accept="image/*" :on-success="onAvatar">
            <el-button size="small" style="margin-top:12px">更换头像</el-button>
          </el-upload>
        </div>
      </div>

      <div class="panel" style="flex:1">
        <div class="panel-hd"><span>基本资料</span></div>
        <div class="panel-bd">
          <el-form :model="form" label-width="100px" label-position="left" style="max-width:520px">
            <el-form-item label="账号"><el-input v-model="user.username" disabled /></el-form-item>
            <el-form-item label="姓名"><el-input v-model="form.realName" /></el-form-item>
            <el-form-item label="联系电话"><el-input v-model="form.phone" /></el-form-item>
            <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
            <el-button type="primary" :loading="saving" @click="saveProfile">保存资料</el-button>
          </el-form>
        </div>
      </div>

      <div class="panel" style="flex:1">
        <div class="panel-hd"><span>修改密码</span></div>
        <div class="panel-bd">
          <el-form :model="pwd" label-width="100px" label-position="left" style="max-width:520px">
            <el-form-item label="原密码"><el-input v-model="pwd.oldPassword" type="password" show-password /></el-form-item>
            <el-form-item label="新密码"><el-input v-model="pwd.newPassword" type="password" show-password placeholder="至少 6 位" /></el-form-item>
            <el-form-item label="确认新密码"><el-input v-model="pwd.confirm" type="password" show-password /></el-form-item>
            <el-button type="primary" @click="changePwd">修改密码</el-button>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { loadMe, store } from '@/store/user'

const user = reactive({})
const form = reactive({ realName: '', phone: '', email: '' })
const pwd = reactive({ oldPassword: '', newPassword: '', confirm: '' })
const saving = ref(false)
const uploadUrl = '/api/file/upload'
const uploadHeaders = computed(() => ({ Authorization: 'Bearer ' + localStorage.getItem('token') }))

const onAvatar = async res => {
  if (res.code !== 200) { ElMessage.error('上传失败'); return }
  await request.put('/auth/avatar', { avatar: res.data })
  user.avatar = res.data
  if (store.user) store.user.avatar = res.data
  ElMessage.success('头像已更新')
}

async function saveProfile() {
  saving.value = true
  try {
    await request.put('/auth/profile', form)
    ElMessage.success('资料已保存')
    await loadMe(true)
    Object.assign(user, store.user)
  } finally { saving.value = false }
}

async function changePwd() {
  if (!pwd.newPassword || pwd.newPassword.length < 6) { ElMessage.warning('新密码至少 6 位'); return }
  if (pwd.newPassword !== pwd.confirm) { ElMessage.warning('两次输入的新密码不一致'); return }
  await request.put('/auth/password', { oldPassword: pwd.oldPassword, newPassword: pwd.newPassword })
  ElMessage.success('密码已修改')
  Object.assign(pwd, { oldPassword: '', newPassword: '', confirm: '' })
}

onMounted(async () => {
  await loadMe()
  Object.assign(user, store.user)
  Object.assign(form, { realName: user.realName, phone: user.phone, email: user.email })
})
</script>

<style scoped>
.profile { display: flex; gap: 16px; align-items: flex-start; flex-wrap: wrap; }
.center { text-align: center; }
.avatar-big { width: 96px; height: 96px; border-radius: 50%; object-fit: cover; border: 2px solid #fff; box-shadow: 0 0 0 1px var(--line); }
.nm { font-size: 16px; font-weight: 600; margin-top: 10px; }
.rl { font-size: 12.5px; color: var(--text-2); }
</style>
