<template>
  <div>
    <h1 class="page-title">系统管理</h1>
    <p class="page-sub">用户、角色、菜单与数据范围分别控制；只有菜单权限不能直接调用写接口</p>

    <el-tabs v-model="tab">
      <el-tab-pane label="用户管理" name="user">
        <div class="panel">
          <div class="panel-bd">
            <div class="filters">
              <el-input v-model="userQuery.keyword" placeholder="姓名 / 账号" clearable style="width:200px" @keyup.enter="loadUsers" />
              <el-select v-model="userQuery.roleId" placeholder="全部角色" clearable style="width:160px">
                <el-option v-for="r in roles" :key="r.id" :label="r.name" :value="r.id" />
              </el-select>
              <el-button type="primary" @click="loadUsers">查询</el-button>
              <el-button type="primary" style="margin-left:auto" @click="openUser()">新增用户</el-button>
            </div>
            <div class="table-wrap">
              <el-table :data="users" border stripe>
                <el-table-column prop="username" label="账号" min-width="120" />
                <el-table-column prop="realName" label="姓名" min-width="96" />
                <el-table-column prop="roleName" label="角色" min-width="110" />
                <el-table-column prop="orgName" label="所属组织" min-width="120" />
                <el-table-column label="数据范围" min-width="96">
                  <template #default="{ row }">{{ scopeText(row.dataScope) }}</template>
                </el-table-column>
                <el-table-column prop="phone" label="联系电话" min-width="120" />
                <el-table-column label="状态" min-width="84">
                  <template #default="{ row }">
                    <span class="tag" :class="row.status === 1 ? 'ok' : 'info'">{{ row.status === 1 ? '启用' : '停用' }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="操作" min-width="180">
                  <template #default="{ row }">
                    <el-button link type="primary" @click="openUser(row)">编辑</el-button>
                    <el-button link type="primary" @click="resetPwd(row)">重置密码</el-button>
                    <el-button link type="danger" @click="toggle(row)">{{ row.status === 1 ? '停用' : '启用' }}</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <div class="pager">
              <el-pagination background layout="total, prev, pager, next" :total="userTotal"
                             v-model:current-page="userQuery.page" v-model:page-size="userQuery.size" @current-change="loadUsers" />
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="角色与菜单授权" name="role">
        <div class="panel">
          <div class="panel-bd role-box">
            <div class="role-list">
              <div class="rl-title">角色</div>
              <div v-for="r in roles" :key="r.id" class="rl-item" :class="{ on: roleId === r.id }" @click="pickRole(r)">
                <b>{{ r.name }}</b>
                <span>{{ scopeText(r.dataScope) }}</span>
              </div>
            </div>
            <div class="role-menu">
              <div class="rl-title">{{ currentRole?.name }} · 菜单与按钮权限</div>
              <el-tree ref="treeRef" :data="menus" show-checkbox node-key="id" :props="{ label: 'name', children: 'children' }" default-expand-all />
              <div style="margin-top:14px">
                <el-button type="primary" @click="saveMenus">保存授权</el-button>
                <span style="font-size:12.5px;color:var(--text-2);margin-left:10px">「菜单管理」为隐藏项，不在导航中展示</span>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="操作日志" name="log">
        <div class="panel">
          <div class="panel-bd">
            <div class="filters">
              <el-select v-model="logQuery.bizType" placeholder="全部业务" clearable style="width:170px">
                <el-option label="用水申请" value="APPLICATION" />
                <el-option label="灌溉计划" value="PLAN" />
                <el-option label="执行任务" value="TASK" />
                <el-option label="地块" value="FARMLAND" />
                <el-option label="定额" value="QUOTA" />
              </el-select>
              <el-button type="primary" @click="loadLogs">查询</el-button>
            </div>
            <div class="table-wrap">
              <el-table :data="logs" border stripe>
                <el-table-column prop="bizNo" label="业务编号" min-width="150" />
                <el-table-column prop="action" label="动作" min-width="110" />
                <el-table-column label="状态变化" min-width="150">
                  <template #default="{ row }">{{ row.beforeStatus || '—' }} → {{ row.afterStatus || '—' }}</template>
                </el-table-column>
                <el-table-column prop="reason" label="原因" min-width="200" show-overflow-tooltip />
                <el-table-column prop="operatorName" label="操作人" min-width="90" />
                <el-table-column label="操作时间" min-width="152">
                  <template #default="{ row }">{{ formatTime(row.createTime) }}</template>
                </el-table-column>
              </el-table>
            </div>
            <div class="pager">
              <el-pagination background layout="total, prev, pager, next" :total="logTotal"
                             v-model:current-page="logQuery.page" v-model:page-size="logQuery.size" @current-change="loadLogs" />
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="userVisible" :title="userForm.id ? '编辑用户' : '新增用户'" width="500px">
      <el-form :model="userForm" label-width="100px" label-position="left">
        <el-form-item label="账号" required><el-input v-model="userForm.username" :disabled="!!userForm.id" /></el-form-item>
        <el-form-item label="姓名" required><el-input v-model="userForm.realName" /></el-form-item>
        <el-form-item label="角色" required>
          <el-select v-model="userForm.roleId" style="width:100%">
            <el-option v-for="r in roles" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="组织" required>
          <el-select v-model="userForm.orgId" style="width:100%">
            <el-option v-for="o in orgs" :key="o.id" :label="o.name" :value="o.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="电话"><el-input v-model="userForm.phone" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="userForm.email" /></el-form-item>
        <el-form-item v-if="!userForm.id" label="初始密码">
          <el-input v-model="userForm.password" placeholder="默认 123456" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="userVisible = false">取消</el-button>
        <el-button type="primary" @click="saveUser">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { formatTime } from '@/utils/format'

const tab = ref('user')
const users = ref([])
const userTotal = ref(0)
const roles = ref([])
const orgs = ref([])
const menus = ref([])
const logs = ref([])
const logTotal = ref(0)
const roleId = ref(null)
const currentRole = ref(null)
const treeRef = ref()
const userVisible = ref(false)

const userQuery = reactive({ keyword: '', roleId: null, page: 1, size: 10 })
const logQuery = reactive({ bizType: '', page: 1, size: 10 })
const userForm = reactive({ id: null, username: '', realName: '', roleId: 4, orgId: 3, phone: '', email: '', password: '' })

const scopeText = s => ({ ALL: '全部', DEPT: '本部门', SELF: '仅本人' }[s] || s)

async function loadUsers() {
  const data = await request.get('/system/user/page', { params: userQuery })
  users.value = data.records || []
  userTotal.value = data.total || 0
}

async function loadLogs() {
  const data = await request.get('/system/log/page', { params: logQuery })
  logs.value = data.records || []
  logTotal.value = data.total || 0
}

function openUser(row) {
  Object.assign(userForm, { id: null, username: '', realName: '', roleId: 4, orgId: 3, phone: '', email: '', password: '' })
  if (row) Object.assign(userForm, row)
  userVisible.value = true
}

async function saveUser() {
  if (!userForm.username || !userForm.realName) { ElMessage.warning('账号与姓名必填'); return }
  await request.post('/system/user', userForm)
  ElMessage.success('保存成功')
  userVisible.value = false
  loadUsers()
}

async function resetPwd(row) {
  const { value } = await ElMessageBox.prompt('请输入新密码（至少 6 位）', '重置密码 ' + row.realName, { inputValue: '123456' })
  await request.put(`/system/user/${row.id}/password`, { password: value })
  ElMessage.success('密码已重置')
}

async function toggle(row) {
  await request.put(`/system/user/${row.id}/status?status=${row.status === 1 ? 0 : 1}`)
  ElMessage.success('状态已更新')
  loadUsers()
}

async function pickRole(r) {
  currentRole.value = r
  roleId.value = r.id
  const ids = await request.get(`/system/role/${r.id}/menus`)
  treeRef.value?.setCheckedKeys(ids)
}

async function saveMenus() {
  const keys = treeRef.value.getCheckedKeys().concat(treeRef.value.getHalfCheckedKeys())
  await request.post(`/system/role/${roleId.value}/menus`, { menuIds: keys })
  ElMessage.success('授权已保存，相关用户需重新登录生效')
}

onMounted(async () => {
  roles.value = await request.get('/system/roles')
  orgs.value = await request.get('/system/orgs')
  menus.value = await request.get('/system/menus')
  await loadUsers()
  await loadLogs()
  if (roles.value.length) await pickRole(roles.value[0])
})
</script>

<style scoped>
.role-box { display: flex; gap: 24px; }
.role-list { width: 220px; flex: 0 0 220px; border-right: 1px solid var(--line); padding-right: 16px; }
.rl-title { font-size: 13px; color: var(--text-2); margin-bottom: 10px; }
.rl-item { padding: 9px 10px; border-radius: 6px; cursor: pointer; margin-bottom: 4px; }
.rl-item b { display: block; font-size: 13.5px; font-weight: 500; }
.rl-item span { font-size: 12px; color: var(--text-2); }
.rl-item.on { background: #EAF2F8; }
.rl-item.on b { color: var(--primary); }
.role-menu { flex: 1; min-width: 0; }
</style>
