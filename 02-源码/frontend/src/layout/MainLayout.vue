<template>
  <div class="layout">
    <aside class="side" :class="{ fold }">
      <div class="brand">
        <svg width="20" height="20" viewBox="0 0 24 24"><path d="M12 3s6 6.5 6 11a6 6 0 11-12 0c0-4.5 6-11 6-11z" fill="#7FB3D5"/></svg>
        <span v-if="!fold">灌溉用水管理</span>
      </div>
      <nav class="nav">
        <template v-for="(g, gi) in groups" :key="gi">
          <div class="grp" v-if="!fold">{{ g.name }}</div>
          <router-link
            v-for="m in g.items"
            :key="m.path"
            :to="m.path"
            class="item"
            :class="{ on: route.path === m.path }"
            :title="m.name"
          >
            <svg class="ico" viewBox="0 0 24 24" v-html="icons[m.icon] || icons.dashboard"></svg>
            <span v-if="!fold">{{ m.name }}</span>
          </router-link>
        </template>
      </nav>
      <div class="side-foot" @click="fold = !fold">
        <span>{{ fold ? '»' : '« 收起菜单' }}</span>
      </div>
    </aside>

    <div class="main">
      <header class="top">
        <div class="left">
          <span class="crumb">灌区管理 / <b>{{ route.meta.title || '' }}</b></span>
        </div>
        <div class="right">
          <el-popover placement="bottom-end" :width="300" trigger="click">
            <template #reference>
              <span class="badge-wrap">
                <svg width="17" height="17" viewBox="0 0 24 24"><path d="M6 16V10a6 6 0 1112 0v6l2 3H4l2-3z" fill="none" stroke="#5A6B78" stroke-width="1.5"/><path d="M10 21h4" stroke="#5A6B78" stroke-width="1.5"/></svg>
                <i v-if="store.unread" class="dot">{{ store.unread }}</i>
              </span>
            </template>
            <div class="msg-list">
              <div class="msg-hd">站内消息</div>
              <div v-if="!messages.length" class="msg-empty">暂无消息</div>
              <div v-for="m in messages" :key="m.id" class="msg" :class="{ unread: !m.readFlag }" @click="readMsg(m)">
                <b>{{ m.title }}</b>
                <p>{{ m.content }}</p>
                <span>{{ formatTime(m.createTime) }}</span>
              </div>
            </div>
          </el-popover>
          <span class="help">帮助</span>
          <el-dropdown trigger="click">
            <span class="user">
              <img :src="store.user?.avatar || '/uploads/seed/avatar/01.jpg'" class="avatar" alt="头像" />
              <span>{{ store.user?.realName || '—' }}</span>
              <em>{{ store.roleName }}</em>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push('/profile')">个人中心</el-dropdown-item>
                <el-dropdown-item divided @click="doLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>
      <section class="content">
        <router-view />
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '@/utils/request'
import { formatTime } from '@/utils/format'
import { loadMe, store, logout } from '@/store/user'

const route = useRoute()
const router = useRouter()
const fold = ref(false)
const messages = ref([])

// 图标取自 design/icons.svg，按后端返回的 icon 名映射
const icons = {
  dashboard: '<path d="M3 3v18h18" fill="none" stroke="currentColor" stroke-width="1.6"/><rect x="6" y="11" width="3" height="7" fill="currentColor"/><rect x="11" y="8" width="3" height="10" fill="currentColor"/><rect x="16" y="5" width="3" height="13" fill="currentColor"/>',
  map: '<path d="M3 6l5-2 5 2 5-2v14l-5 2-5-2-5 2V6z" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M8 4v14M13 6v14" stroke="currentColor" stroke-width="1.2"/>',
  application: '<rect x="4" y="3" width="16" height="18" rx="2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M8 8h8M8 12h8M8 16h5" stroke="currentColor" stroke-width="1.4"/>',
  plan: '<rect x="3" y="5" width="18" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M3 10h18M8 3v4M16 3v4" stroke="currentColor" stroke-width="1.4"/>',
  task: '<path d="M12 3s6 6.5 6 11a6 6 0 11-12 0c0-4.5 6-11 6-11z" fill="none" stroke="currentColor" stroke-width="1.5"/>',
  fee: '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M12 7v10M9 9.5h4.5a2 2 0 010 4H9" fill="none" stroke="currentColor" stroke-width="1.4"/>',
  quota: '<path d="M12 4v16M6 8h12" stroke="currentColor" stroke-width="1.5"/><path d="M6 8l-3 6h6l-3-6zM18 8l-3 6h6l-3-6z" fill="none" stroke="currentColor" stroke-width="1.4"/>',
  source: '<path d="M3 9c3-3 6 3 9 0s6-3 9 0M3 15c3-3 6 3 9 0s6-3 9 0" fill="none" stroke="currentColor" stroke-width="1.5"/>',
  advice: '<path d="M12 3l2.2 5.8L20 11l-5.8 2.2L12 19l-2.2-5.8L4 11l5.8-2.2L12 3z" fill="none" stroke="currentColor" stroke-width="1.4"/>',
  chart: '<path d="M3 20V4M3 20h18M7 16l4-5 3 3 5-7" fill="none" stroke="currentColor" stroke-width="1.6"/>',
  system: '<circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M12 3v3M12 18v3M4.2 7.5l2.6 1.5M17.2 15l2.6 1.5M4.2 16.5l2.6-1.5M17.2 9l2.6-1.5" stroke="currentColor" stroke-width="1.4"/>'
}

// 菜单按后端返回的角色权限渲染，并隐藏「菜单管理」入口（文档要求）
const groups = computed(() => {
  const menus = store.menus || []
  if (!menus.length) return []
  return [
    {
      name: '业务导航',
      items: menus
        .filter(m => m.name !== '系统管理')
        .map(m => ({ name: m.name, path: m.path, icon: m.icon }))
        .filter(m => m.path)
    },
    {
      name: '系统',
      items: menus
        .filter(m => m.name === '系统管理')
        .flatMap(m => (m.children && m.children.length ? m.children : [m]))
        .filter(m => m.path && m.name !== '菜单管理')
    }
  ].filter(g => g.items.length)
})

const doLogout = () => logout()

const loadMessages = async () => {
  messages.value = await request.get('/auth/messages').catch(() => [])
}

const readMsg = async m => {
  if (!m.readFlag) {
    await request.put(`/auth/messages/${m.id}/read`)
    m.readFlag = 1
    store.unread = Math.max(0, store.unread - 1)
  }
}

onMounted(async () => {
  await loadMe()
  loadMessages()
})
</script>

<style scoped>
.layout { display: flex; min-height: 100vh; }
.side {
  width: var(--side-w); flex: 0 0 var(--side-w); background: var(--primary);
  color: #fff; display: flex; flex-direction: column; transition: flex-basis .18s, width .18s;
}
.side.fold { width: 64px; flex-basis: 64px; }
.brand {
  height: var(--top-h); display: flex; align-items: center; gap: 8px;
  padding: 0 18px; font-size: 15px; font-weight: 600; letter-spacing: .3px;
  border-bottom: 1px solid rgba(255,255,255,.12); white-space: nowrap;
}
.nav { padding: 10px 8px; flex: 1; overflow-y: auto; }
.grp { font-size: 11px; color: rgba(255,255,255,.45); padding: 12px 12px 6px; letter-spacing: 1px; }
.item {
  display: flex; align-items: center; gap: 9px; padding: 9px 12px; border-radius: 6px;
  color: rgba(255,255,255,.82); font-size: 13.5px; margin-bottom: 2px; white-space: nowrap;
}
.item:hover { background: rgba(255,255,255,.08); color: #fff; }
.item.on { background: rgba(255,255,255,.14); color: #fff; font-weight: 500; }
.ico { width: 16px; height: 16px; flex: 0 0 16px; opacity: .9; }
.side-foot {
  padding: 12px 18px; font-size: 12px; color: rgba(255,255,255,.5);
  border-top: 1px solid rgba(255,255,255,.1); cursor: pointer;
}
.main { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.top {
  height: var(--top-h); background: #fff; border-bottom: 1px solid var(--line);
  display: flex; align-items: center; justify-content: space-between; padding: 0 24px;
}
.crumb { font-size: 13px; color: var(--text-2); }
.crumb b { color: var(--text); font-weight: 500; }
.right { display: flex; align-items: center; gap: 18px; font-size: 13px; color: var(--text-2); }
.badge-wrap { position: relative; display: inline-flex; cursor: pointer; padding-top: 3px; }
.dot {
  position: absolute; top: -4px; right: -9px; background: var(--danger); color: #fff;
  font-style: normal; font-size: 10px; min-width: 15px; height: 15px; border-radius: 8px;
  display: grid; place-items: center; padding: 0 3px;
}
.help { cursor: pointer; }
.user { display: flex; align-items: center; gap: 7px; cursor: pointer; color: var(--text); }
.user em { font-style: normal; font-size: 12px; color: var(--text-2); }
.avatar { width: 30px; height: 30px; border-radius: 50%; object-fit: cover; border: 1px solid var(--line); }
.content { padding: 24px; flex: 1; min-width: 0; }
.msg-list { max-height: 360px; overflow: auto; }
.msg-hd { font-weight: 600; font-size: 13.5px; padding-bottom: 8px; border-bottom: 1px solid var(--line); }
.msg-empty { color: var(--text-2); font-size: 13px; padding: 16px 0; text-align: center; }
.msg { padding: 9px 0; border-bottom: 1px dashed #EDF3F8; cursor: pointer; }
.msg b { font-size: 13px; font-weight: 500; }
.msg p { margin: 2px 0; font-size: 12.5px; color: var(--text-2); line-height: 1.5; }
.msg span { font-size: 11.5px; color: #93A3B0; }
.msg.unread b::before { content: ''; display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: var(--danger); margin-right: 5px; vertical-align: 1px; }
</style>
