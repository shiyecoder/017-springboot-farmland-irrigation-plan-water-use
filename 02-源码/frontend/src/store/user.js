import { reactive } from 'vue'
import request from '@/utils/request'

/**
 * 轻量全局状态：当前用户、角色、菜单、按钮权限。
 * 菜单与权限均由后端按角色返回，前端不做硬编码角色判断。
 */
export const store = reactive({
  user: null,
  roleCode: '',
  roleName: '',
  menus: [],
  perms: [],
  unread: 0,
  loaded: false
})

export async function loadMe(force = false) {
  if (store.loaded && !force) return store
  const data = await request.get('/auth/me')
  store.user = data
  store.roleCode = data.roleCode || ''
  store.roleName = data.roleName || ''
  store.menus = data.menus || []
  store.perms = await request.get('/auth/perms').catch(() => [])
  store.unread = await request.get('/auth/messages/unread').catch(() => 0)
  store.loaded = true
  return store
}

export function hasPerm(p) {
  return store.perms.includes(p)
}

export function logout() {
  localStorage.removeItem('token')
  store.user = null
  store.loaded = false
  store.menus = []
  location.href = '/login'
}

export function homeOf(role) {
  return role === 'farmer' ? '/portal' : '/dashboard'
}
