/**
 * 全局时间与数值格式化。全系统统一调用本文件，禁止各页面重复实现。
 */

/** yyyy-MM-dd HH:mm:ss */
export function formatTime(v) {
  if (!v) return '—'
  const d = typeof v === 'string' ? new Date(v.replace(/-/g, '/')) : new Date(v)
  if (isNaN(d.getTime())) return String(v)
  const p = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`
}

/** yyyy-MM-dd */
export function formatDate(v) {
  if (!v) return '—'
  const s = String(v)
  if (/^\d{4}-\d{2}-\d{2}/.test(s)) return s.slice(0, 10)
  const d = new Date(s.replace(/-/g, '/'))
  if (isNaN(d.getTime())) return s
  const p = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`
}

/** 日期时间转 datetime-local 输入值 */
export function toInputTime(v) {
  if (!v) return ''
  const s = String(v).replace(' ', 'T')
  return s.length > 16 ? s.slice(0, 16) : s
}

/** 数量：保留两位小数并加千分位 */
export function num(v, digits = 2) {
  if (v === null || v === undefined || v === '') return '0'
  const n = Number(v)
  if (isNaN(n)) return String(v)
  return n.toLocaleString('zh-CN', { minimumFractionDigits: digits, maximumFractionDigits: digits })
}

/** 金额：元 */
export function money(v) {
  return '¥ ' + num(v, 2)
}

/** 百分比 */
export function percent(v, digits = 1) {
  if (v === null || v === undefined || v === '') return '0%'
  return Number(v).toFixed(digits) + '%'
}

export const STATUS_TEXT = {
  // 申请
  PENDING_AUDIT: '待审核', PENDING_SCHEDULE: '待排程', SCHEDULED: '已安排', REJECTED: '已驳回',
  // 计划
  DRAFT: '编制中', AUDITING: '待审核', ISSUED: '已下达', EXECUTING: '执行中',
  CONFIRMING: '待确认', ARCHIVED: '已归档', CONFLICT: '容量冲突',
  // 任务
  PENDING: '待执行', RUNNING: '进行中', FINISHED: '已完成', INTERRUPTED: '已中断',
  // 费用
  UNPAID: '待缴费', PAID: '已缴费', WAIVED: '已减免',
  // 异常
  OPEN: '待处理', HANDLED: '已处理',
  // 台账
  NORMAL: '正常', SHORT: '余量不足', OVER: '已超额', FALLOW: '休耕', STOP: '停用',
  LIMIT: '限流', CLOSED: '关闭', FAULT: '故障', OPEN_GATE: '开启',
  // 建议等级
  RECOMMEND: '推荐', REVIEW: '需复核', DEVIATE: '偏差较大', INSUFFICIENT: '数据不足',
  // 角色
  admin: '灌区管理员', dispatcher: '调度员', operator: '放水员', farmer: '种植户'
}

export const STATUS_TYPE = {
  PENDING_AUDIT: 'blue', PENDING_SCHEDULE: 'blue', SCHEDULED: 'sky', REJECTED: 'bad',
  DRAFT: 'info', AUDITING: 'blue', ISSUED: 'sky', EXECUTING: 'sky',
  CONFIRMING: 'warn', ARCHIVED: 'ok', CONFLICT: 'bad',
  PENDING: 'blue', RUNNING: 'sky', FINISHED: 'ok', INTERRUPTED: 'bad',
  UNPAID: 'blue', PAID: 'ok', WAIVED: 'info',
  OPEN: 'bad', HANDLED: 'ok',
  NORMAL: 'ok', SHORT: 'warn', OVER: 'bad', FALLOW: 'info', STOP: 'info',
  LIMIT: 'warn', CLOSED: 'info', FAULT: 'bad',
  RECOMMEND: 'ok', REVIEW: 'warn', DEVIATE: 'bad', INSUFFICIENT: 'info'
}

export const text = s => STATUS_TEXT[s] || s || '—'

export const URGENCY = { URGENT: '紧急', NORMAL: '普通' }
export const PRIORITY = { HIGH: '高', NORMAL: '中', LOW: '低' }
export const EXC_TYPE = { BLOCK: '渠道堵塞', LEAK: '漏水', FAULT: '设备故障', SHORT: '水量不足' }
export const SOURCE_TYPE = { RESERVOIR: '水库', WELL: '机井', RIVER: '河道', POND: '塘坝' }
export const GRADE = { RECOMMEND: '推荐', REVIEW: '需复核', DEVIATE: '偏差较大', INSUFFICIENT: '数据不足' }
