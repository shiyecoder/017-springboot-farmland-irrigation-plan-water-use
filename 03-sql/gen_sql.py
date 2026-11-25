# -*- coding: utf-8 -*-
"""生成 NEW-017 农田灌溉计划与用水统计系统的初始化 SQL。

设计要点：
- 23 张表，字符集 utf8mb4，关键字段带注释与索引
- 测试数据覆盖 4 个角色、6 个组织、26 个地块、48 条申请、34 条计划、40 个任务
- create_time 分散在 2026-05 ~ 2026-10，不堆在同一天
- 图片字段一律 /uploads/seed/<实体>/NN.jpg，按 ((i*7)%N)+1 循环复用且相邻不重复
"""
import pathlib
import random
from datetime import datetime, timedelta

random.seed(20261031)
OUT = pathlib.Path("/Users/xiaoxin/showcase/build/NEW-017/sql/init.sql")
DB = "new_017"
PWD = "$2b$10$ixLF2gjJd.Z7AayJNboJfeN/El.gqamvvdde/pJcbr4KK0xzi8Bte"  # admin123

BASE = datetime(2026, 10, 31, 17, 0, 0)


def ts(days_ago, hour=9, minute=0):
    d = BASE - timedelta(days=days_ago)
    return d.replace(hour=hour, minute=minute, second=random.randint(0, 59)).strftime("%Y-%m-%d %H:%M:%S")


def q(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def img(entity, i, n):
    return f"/uploads/seed/{entity}/{((i * 7) % n) + 1:02d}.jpg"


def insert(table, cols, rows):
    out = [f"INSERT INTO `{table}` ({', '.join('`' + c + '`' for c in cols)}) VALUES"]
    vals = []
    for r in rows:
        vals.append("(" + ", ".join(q(x) for x in r) + ")")
    out.append(",\n".join(vals) + ";")
    return "\n".join(out)


S = []
S.append(f"""-- =====================================================================
-- 农田灌溉计划与用水统计系统 · 数据库初始化脚本
-- 库名：{DB}  字符集：utf8mb4  引擎：InnoDB
-- 说明：脚本可重复执行（先删库重建），默认账号 admin / admin123
-- =====================================================================
DROP DATABASE IF EXISTS `{DB}`;
CREATE DATABASE `{DB}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `{DB}`;

SET NAMES utf8mb4;

-- ---------------------------------------------------------------------
-- 1. 组织（灌区管理所 / 调度中心 / 渠道站 / 片区）
-- ---------------------------------------------------------------------
CREATE TABLE `sys_org` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `code` VARCHAR(30) NOT NULL COMMENT '组织编码',
  `name` VARCHAR(80) NOT NULL COMMENT '组织名称',
  `parent_id` BIGINT DEFAULT 0 COMMENT '上级组织',
  `org_type` VARCHAR(20) NOT NULL DEFAULT 'STATION' COMMENT '类型：BUREAU 管理所/STATION 渠道站/VILLAGE 片区',
  `sort_no` INT NOT NULL DEFAULT 0 COMMENT '排序',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT '1 启用 0 停用',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_org_code` (`code`),
  KEY `idx_org_parent` (`parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='组织架构';

-- ---------------------------------------------------------------------
-- 2. 角色
-- ---------------------------------------------------------------------
CREATE TABLE `sys_role` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `code` VARCHAR(30) NOT NULL COMMENT '角色编码',
  `name` VARCHAR(50) NOT NULL COMMENT '角色名称',
  `data_scope` VARCHAR(10) NOT NULL DEFAULT 'SELF' COMMENT '数据范围：ALL 全部/DEPT 本部门/SELF 仅本人',
  `remark` VARCHAR(200) DEFAULT NULL COMMENT '说明',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_role_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色';

-- ---------------------------------------------------------------------
-- 3. 用户（密码 BCrypt，任何接口与日志均不返回 password）
-- ---------------------------------------------------------------------
CREATE TABLE `sys_user` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `username` VARCHAR(50) NOT NULL COMMENT '登录账号',
  `password` VARCHAR(100) NOT NULL COMMENT 'BCrypt 密码',
  `real_name` VARCHAR(50) NOT NULL COMMENT '姓名',
  `phone` VARCHAR(20) DEFAULT NULL COMMENT '联系电话',
  `email` VARCHAR(80) DEFAULT NULL COMMENT '邮箱',
  `avatar` VARCHAR(200) DEFAULT NULL COMMENT '头像相对路径',
  `role_id` BIGINT NOT NULL COMMENT '角色',
  `org_id` BIGINT NOT NULL COMMENT '所属组织',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT '1 启用 0 停用',
  `login_fail_count` INT NOT NULL DEFAULT 0 COMMENT '连续登录失败次数',
  `lock_until` DATETIME DEFAULT NULL COMMENT '锁定截止时间',
  `last_login_time` DATETIME DEFAULT NULL COMMENT '最近登录时间',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_name` (`username`),
  KEY `idx_user_role` (`role_id`),
  KEY `idx_user_org` (`org_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户';

-- ---------------------------------------------------------------------
-- 4. 菜单（type：M 目录 / C 菜单 / F 按钮）
-- ---------------------------------------------------------------------
CREATE TABLE `sys_menu` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `parent_id` BIGINT NOT NULL DEFAULT 0 COMMENT '上级菜单',
  `name` VARCHAR(50) NOT NULL COMMENT '菜单名称',
  `path` VARCHAR(100) DEFAULT NULL COMMENT '前端路由',
  `icon` VARCHAR(40) DEFAULT NULL COMMENT '图标标识',
  `menu_type` CHAR(1) NOT NULL DEFAULT 'C' COMMENT 'M 目录 C 菜单 F 按钮',
  `perm` VARCHAR(80) DEFAULT NULL COMMENT '权限标识',
  `sort_no` INT NOT NULL DEFAULT 0 COMMENT '排序',
  `visible` TINYINT NOT NULL DEFAULT 1 COMMENT '1 显示 0 隐藏',
  PRIMARY KEY (`id`),
  KEY `idx_menu_parent` (`parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='菜单';

CREATE TABLE `sys_role_menu` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `role_id` BIGINT NOT NULL COMMENT '角色',
  `menu_id` BIGINT NOT NULL COMMENT '菜单',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_role_menu` (`role_id`, `menu_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色菜单';

-- ---------------------------------------------------------------------
-- 5. 字典（种植阶段、土壤类型、紧急程度、异常类型等）
-- ---------------------------------------------------------------------
CREATE TABLE `sys_dict_item` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `dict_type` VARCHAR(40) NOT NULL COMMENT '字典类型',
  `label` VARCHAR(50) NOT NULL COMMENT '显示文本',
  `value` VARCHAR(50) NOT NULL COMMENT '存储值',
  `sort_no` INT NOT NULL DEFAULT 0 COMMENT '排序',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT '1 启用',
  PRIMARY KEY (`id`),
  KEY `idx_dict_type` (`dict_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='字典项';

-- ---------------------------------------------------------------------
-- 6. 文件（上传组件元数据，不存外部 URL）
-- ---------------------------------------------------------------------
CREATE TABLE `sys_file` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `biz_type` VARCHAR(30) NOT NULL COMMENT '业务类型',
  `biz_id` BIGINT DEFAULT NULL COMMENT '业务主键',
  `origin_name` VARCHAR(200) NOT NULL COMMENT '原始文件名',
  `file_path` VARCHAR(255) NOT NULL COMMENT '相对路径 /uploads/...',
  `file_size` BIGINT NOT NULL DEFAULT 0 COMMENT '字节数',
  `uploader_id` BIGINT DEFAULT NULL COMMENT '上传人',
  `upload_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
  PRIMARY KEY (`id`),
  KEY `idx_file_biz` (`biz_type`, `biz_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='附件';

-- ---------------------------------------------------------------------
-- 7. 站内消息
-- ---------------------------------------------------------------------
CREATE TABLE `sys_message` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `title` VARCHAR(120) NOT NULL COMMENT '标题',
  `content` VARCHAR(500) NOT NULL COMMENT '内容',
  `biz_no` VARCHAR(40) DEFAULT NULL COMMENT '业务编号',
  `biz_type` VARCHAR(30) DEFAULT NULL COMMENT '业务类型',
  `receiver_id` BIGINT NOT NULL COMMENT '接收人',
  `read_flag` TINYINT NOT NULL DEFAULT 0 COMMENT '0 未读 1 已读',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_msg_receiver` (`receiver_id`, `read_flag`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='站内消息';

-- ---------------------------------------------------------------------
-- 8. 操作日志（状态流转留痕，普通用户不可修改）
-- ---------------------------------------------------------------------
CREATE TABLE `sys_operation_log` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `biz_type` VARCHAR(30) NOT NULL COMMENT '业务类型',
  `biz_id` BIGINT NOT NULL COMMENT '业务主键',
  `biz_no` VARCHAR(40) DEFAULT NULL COMMENT '业务编号',
  `action` VARCHAR(50) NOT NULL COMMENT '动作',
  `before_status` VARCHAR(30) DEFAULT NULL COMMENT '变更前状态',
  `after_status` VARCHAR(30) DEFAULT NULL COMMENT '变更后状态',
  `reason` VARCHAR(300) DEFAULT NULL COMMENT '原因（驳回/退回/中断必填）',
  `operator_id` BIGINT DEFAULT NULL COMMENT '操作人',
  `operator_name` VARCHAR(50) DEFAULT NULL COMMENT '操作人姓名',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
  PRIMARY KEY (`id`),
  KEY `idx_log_biz` (`biz_type`, `biz_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志';

-- ---------------------------------------------------------------------
-- 9. 水源
-- ---------------------------------------------------------------------
CREATE TABLE `water_source` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `code` VARCHAR(30) NOT NULL COMMENT '水源编号',
  `name` VARCHAR(80) NOT NULL COMMENT '水源名称',
  `source_type` VARCHAR(20) NOT NULL COMMENT 'RESERVOIR 水库/WELL 机井/RIVER 河道/POND 塘坝',
  `design_supply` DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '设计日供水 m³',
  `available_volume` DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '当前可用水量 m³',
  `manager` VARCHAR(50) DEFAULT NULL COMMENT '负责人',
  `phone` VARCHAR(20) DEFAULT NULL COMMENT '联系电话',
  `photo` VARCHAR(200) DEFAULT NULL COMMENT '现场照片',
  `status` VARCHAR(20) NOT NULL DEFAULT 'NORMAL' COMMENT 'NORMAL 正常/SHORT 来水偏少/STOP 停用',
  `remark` VARCHAR(300) DEFAULT NULL COMMENT '备注',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_source_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='水源台账';

-- ---------------------------------------------------------------------
-- 10. 干支渠
-- ---------------------------------------------------------------------
CREATE TABLE `canal` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `code` VARCHAR(30) NOT NULL COMMENT '渠道编号',
  `name` VARCHAR(80) NOT NULL COMMENT '渠道名称',
  `source_id` BIGINT NOT NULL COMMENT '所属水源',
  `canal_level` VARCHAR(10) NOT NULL COMMENT 'MAIN 干渠/BRANCH 支渠',
  `design_flow` DECIMAL(8,3) NOT NULL COMMENT '设计流量 m³/s',
  `length_km` DECIMAL(8,2) DEFAULT 0 COMMENT '长度 km',
  `status` VARCHAR(20) NOT NULL DEFAULT 'NORMAL' COMMENT 'NORMAL 正常/LIMIT 限流/CLOSED 关闭',
  `remark` VARCHAR(300) DEFAULT NULL COMMENT '备注',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_canal_code` (`code`),
  KEY `idx_canal_source` (`source_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='渠道';

-- ---------------------------------------------------------------------
-- 11. 闸口（计划冲突校验的最小单元）
-- ---------------------------------------------------------------------
CREATE TABLE `gate` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `code` VARCHAR(30) NOT NULL COMMENT '闸口编号',
  `name` VARCHAR(80) NOT NULL COMMENT '闸口名称',
  `canal_id` BIGINT NOT NULL COMMENT '所属渠道',
  `design_flow` DECIMAL(8,3) NOT NULL COMMENT '闸口设计流量 m³/s',
  `open_degree` INT NOT NULL DEFAULT 100 COMMENT '开度百分比',
  `status` VARCHAR(20) NOT NULL DEFAULT 'OPEN' COMMENT 'OPEN 开启/CLOSED 关闭/FAULT 故障',
  `remark` VARCHAR(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_gate_code` (`code`),
  KEY `idx_gate_canal` (`canal_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='闸口';

-- ---------------------------------------------------------------------
-- 12. 水表
-- ---------------------------------------------------------------------
CREATE TABLE `water_meter` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `code` VARCHAR(30) NOT NULL COMMENT '水表编号',
  `name` VARCHAR(80) NOT NULL COMMENT '水表名称',
  `gate_id` BIGINT DEFAULT NULL COMMENT '安装闸口',
  `farmland_id` BIGINT DEFAULT NULL COMMENT '关联地块',
  `init_reading` DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '初始读数',
  `current_reading` DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '当前读数',
  `install_date` DATE DEFAULT NULL COMMENT '安装日期',
  `photo` VARCHAR(200) DEFAULT NULL COMMENT '表具照片',
  `status` VARCHAR(20) NOT NULL DEFAULT 'NORMAL' COMMENT 'NORMAL 正常/FAULT 故障/REPLACED 已更换',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_meter_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='水表';

-- ---------------------------------------------------------------------
-- 13. 农田地块（核心主数据）
-- ---------------------------------------------------------------------
CREATE TABLE `farmland` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `code` VARCHAR(50) NOT NULL COMMENT '地块编号，业务唯一',
  `name` VARCHAR(80) NOT NULL COMMENT '地块名称',
  `area` DECIMAL(10,2) NOT NULL COMMENT '面积（亩）',
  `crop` VARCHAR(30) NOT NULL COMMENT '作物',
  `growth_stage` VARCHAR(30) NOT NULL COMMENT '种植阶段',
  `soil_type` VARCHAR(30) NOT NULL COMMENT '土壤类型',
  `irrigation_type` VARCHAR(30) DEFAULT NULL COMMENT '灌溉方式',
  `region` VARCHAR(40) NOT NULL COMMENT '所属片区',
  `address` VARCHAR(150) DEFAULT NULL COMMENT '位置描述',
  `owner_id` BIGINT NOT NULL COMMENT '承包种植户',
  `owner_name` VARCHAR(50) NOT NULL COMMENT '种植户姓名',
  `org_id` BIGINT NOT NULL COMMENT '所属组织',
  `photo` VARCHAR(200) DEFAULT NULL COMMENT '地块照片',
  `status` VARCHAR(20) NOT NULL DEFAULT 'NORMAL' COMMENT 'NORMAL 正常/FALLOW 休耕/SHORT 缺水/STOP 停用',
  `deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '逻辑删除',
  `version` INT NOT NULL DEFAULT 0 COMMENT '乐观锁版本号',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_farmland_code` (`code`),
  KEY `idx_farmland_owner` (`owner_id`),
  KEY `idx_farmland_org` (`org_id`),
  KEY `idx_farmland_crop` (`crop`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='农田地块';

-- ---------------------------------------------------------------------
-- 14. 水权定额（已用由任务确认回写，剩余 = 定额 - 已用）
-- ---------------------------------------------------------------------
CREATE TABLE `water_quota` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `quota_year` INT NOT NULL COMMENT '年度',
  `farmland_id` BIGINT NOT NULL COMMENT '地块',
  `farmer_id` BIGINT NOT NULL COMMENT '种植户',
  `farmer_name` VARCHAR(50) NOT NULL COMMENT '种植户姓名',
  `quota_volume` DECIMAL(12,2) NOT NULL COMMENT '定额水量 m³',
  `used_volume` DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '已用水量 m³',
  `remaining_volume` DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '剩余水量 m³',
  `status` VARCHAR(20) NOT NULL DEFAULT 'NORMAL' COMMENT 'NORMAL 正常/SHORT 余量不足/OVER 已超额',
  `version` INT NOT NULL DEFAULT 0 COMMENT '乐观锁版本号',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_quota_year_land` (`quota_year`, `farmland_id`),
  KEY `idx_quota_farmer` (`farmer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='水权定额';

-- ---------------------------------------------------------------------
-- 15. 用水申请（待审核→待排程→已安排/已驳回）
-- ---------------------------------------------------------------------
CREATE TABLE `water_application` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `code` VARCHAR(40) NOT NULL COMMENT '申请编号',
  `farmland_id` BIGINT NOT NULL COMMENT '地块',
  `crop` VARCHAR(30) NOT NULL COMMENT '作物',
  `growth_stage` VARCHAR(30) NOT NULL COMMENT '种植阶段',
  `expect_date` DATE NOT NULL COMMENT '期望用水日期',
  `apply_volume` DECIMAL(12,2) NOT NULL COMMENT '申请水量 m³',
  `urgency` VARCHAR(10) NOT NULL DEFAULT 'NORMAL' COMMENT 'URGENT 紧急/NORMAL 普通',
  `applicant_id` BIGINT NOT NULL COMMENT '申请人',
  `applicant_name` VARCHAR(50) NOT NULL COMMENT '申请人姓名',
  `status` VARCHAR(20) NOT NULL DEFAULT 'PENDING_AUDIT' COMMENT 'PENDING_AUDIT 待审核/PENDING_SCHEDULE 待排程/SCHEDULED 已安排/REJECTED 已驳回',
  `audit_opinion` VARCHAR(300) DEFAULT NULL COMMENT '审核意见',
  `audit_by` VARCHAR(50) DEFAULT NULL COMMENT '审核人',
  `audit_time` DATETIME DEFAULT NULL COMMENT '审核时间',
  `version` INT NOT NULL DEFAULT 0 COMMENT '乐观锁版本号',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_app_code` (`code`),
  KEY `idx_app_land` (`farmland_id`),
  KEY `idx_app_status` (`status`),
  KEY `idx_app_applicant` (`applicant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用水申请';

-- ---------------------------------------------------------------------
-- 16. 灌溉计划（核心过程单据）
-- ---------------------------------------------------------------------
CREATE TABLE `irrigation_plan` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `code` VARCHAR(40) NOT NULL COMMENT '计划编号',
  `application_id` BIGINT DEFAULT NULL COMMENT '来源申请',
  `farmland_id` BIGINT NOT NULL COMMENT '地块',
  `canal_id` BIGINT NOT NULL COMMENT '渠道',
  `gate_id` BIGINT NOT NULL COMMENT '闸口',
  `plan_start` DATETIME NOT NULL COMMENT '计划开始',
  `plan_end` DATETIME NOT NULL COMMENT '计划结束',
  `plan_volume` DECIMAL(12,2) NOT NULL COMMENT '计划水量 m³',
  `priority` VARCHAR(10) NOT NULL DEFAULT 'NORMAL' COMMENT 'HIGH 高/NORMAL 中/LOW 低',
  `status` VARCHAR(20) NOT NULL DEFAULT 'DRAFT' COMMENT 'DRAFT 编制中/AUDITING 待审核/ISSUED 已下达/EXECUTING 执行中/CONFIRMING 待确认/ARCHIVED 已归档/REJECTED 已驳回/CONFLICT 冲突',
  `dispatcher_id` BIGINT DEFAULT NULL COMMENT '调度员',
  `dispatcher_name` VARCHAR(50) DEFAULT NULL COMMENT '调度员姓名',
  `reject_reason` VARCHAR(300) DEFAULT NULL COMMENT '驳回/退回原因',
  `remark` VARCHAR(300) DEFAULT NULL COMMENT '备注',
  `version` INT NOT NULL DEFAULT 0 COMMENT '乐观锁版本号',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_plan_code` (`code`),
  KEY `idx_plan_land` (`farmland_id`),
  KEY `idx_plan_gate_time` (`gate_id`, `plan_start`, `plan_end`),
  KEY `idx_plan_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='灌溉计划';

-- ---------------------------------------------------------------------
-- 17. 执行任务（放水员现场录入）
-- ---------------------------------------------------------------------
CREATE TABLE `irrigation_task` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `code` VARCHAR(40) NOT NULL COMMENT '任务编号',
  `plan_id` BIGINT NOT NULL COMMENT '灌溉计划',
  `farmland_id` BIGINT NOT NULL COMMENT '地块',
  `operator_id` BIGINT DEFAULT NULL COMMENT '放水员',
  `operator_name` VARCHAR(50) DEFAULT NULL COMMENT '放水员姓名',
  `plan_volume` DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '计划水量 m³',
  `start_reading` DECIMAL(12,2) DEFAULT NULL COMMENT '开始表数',
  `end_reading` DECIMAL(12,2) DEFAULT NULL COMMENT '结束表数',
  `actual_volume` DECIMAL(12,2) DEFAULT NULL COMMENT '实际水量 m³',
  `start_time` DATETIME DEFAULT NULL COMMENT '实际开始',
  `end_time` DATETIME DEFAULT NULL COMMENT '实际结束',
  `status` VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT 'PENDING 待执行/RUNNING 进行中/FINISHED 已完成/INTERRUPTED 已中断',
  `photo` VARCHAR(200) DEFAULT NULL COMMENT '现场照片',
  `receiver_name` VARCHAR(50) DEFAULT NULL COMMENT '受水人确认',
  `confirm_time` DATETIME DEFAULT NULL COMMENT '确认时间',
  `interrupt_reason` VARCHAR(300) DEFAULT NULL COMMENT '中断原因',
  `version` INT NOT NULL DEFAULT 0 COMMENT '乐观锁版本号',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_task_code` (`code`),
  KEY `idx_task_plan` (`plan_id`),
  KEY `idx_task_operator` (`operator_id`),
  KEY `idx_task_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='灌溉任务';

-- ---------------------------------------------------------------------
-- 18. 水表记录（任务抄表凭证）
-- ---------------------------------------------------------------------
CREATE TABLE `water_meter_record` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `task_id` BIGINT NOT NULL COMMENT '任务',
  `meter_id` BIGINT DEFAULT NULL COMMENT '水表',
  `start_reading` DECIMAL(12,2) NOT NULL COMMENT '开始表数',
  `end_reading` DECIMAL(12,2) NOT NULL COMMENT '结束表数',
  `volume` DECIMAL(12,2) NOT NULL COMMENT '本段水量 m³',
  `record_time` DATETIME NOT NULL COMMENT '抄表时间',
  `recorder_id` BIGINT DEFAULT NULL COMMENT '抄表人',
  `recorder_name` VARCHAR(50) DEFAULT NULL COMMENT '抄表人姓名',
  `photo` VARCHAR(200) DEFAULT NULL COMMENT '表盘照片',
  `remark` VARCHAR(300) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`id`),
  KEY `idx_record_task` (`task_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='水表抄表记录';

-- ---------------------------------------------------------------------
-- 19. 费用台账（分段计费：定额内基础价，超额加价）
-- ---------------------------------------------------------------------
CREATE TABLE `fee_ledger` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `code` VARCHAR(40) NOT NULL COMMENT '费用单号',
  `task_id` BIGINT NOT NULL COMMENT '任务',
  `farmland_id` BIGINT NOT NULL COMMENT '地块',
  `farmer_name` VARCHAR(50) NOT NULL COMMENT '种植户',
  `actual_volume` DECIMAL(12,2) NOT NULL COMMENT '实际水量 m³',
  `base_volume` DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '定额内水量 m³',
  `excess_volume` DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '超额水量 m³',
  `base_price` DECIMAL(8,2) NOT NULL DEFAULT 0.42 COMMENT '基础单价 元/m³',
  `excess_price` DECIMAL(8,2) NOT NULL DEFAULT 0.55 COMMENT '超额单价 元/m³',
  `amount` DECIMAL(12,2) NOT NULL COMMENT '金额（元）',
  `bill_month` VARCHAR(7) NOT NULL COMMENT '计费月份 yyyy-MM',
  `status` VARCHAR(20) NOT NULL DEFAULT 'UNPAID' COMMENT 'UNPAID 待缴费/PAID 已缴费/WAIVED 已减免',
  `pay_time` DATETIME DEFAULT NULL COMMENT '缴费时间',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_fee_code` (`code`),
  KEY `idx_fee_task` (`task_id`),
  KEY `idx_fee_month` (`bill_month`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='费用台账';

-- ---------------------------------------------------------------------
-- 20. 异常处置（渠道堵塞/漏水/设备故障/水量不足）
-- ---------------------------------------------------------------------
CREATE TABLE `exception_record` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `task_id` BIGINT NOT NULL COMMENT '任务',
  `exc_type` VARCHAR(20) NOT NULL COMMENT 'BLOCK 渠道堵塞/LEAK 漏水/FAULT 设备故障/SHORT 水量不足',
  `description` VARCHAR(300) NOT NULL COMMENT '异常描述',
  `loss_volume` DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '损失水量 m³',
  `handle_result` VARCHAR(300) DEFAULT NULL COMMENT '处理结果',
  `photo` VARCHAR(200) DEFAULT NULL COMMENT '现场照片',
  `reporter_id` BIGINT DEFAULT NULL COMMENT '上报人',
  `reporter_name` VARCHAR(50) DEFAULT NULL COMMENT '上报人姓名',
  `status` VARCHAR(20) NOT NULL DEFAULT 'OPEN' COMMENT 'OPEN 待处理/HANDLED 已处理',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上报时间',
  PRIMARY KEY (`id`),
  KEY `idx_exc_task` (`task_id`),
  KEY `idx_exc_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='异常处置';

-- ---------------------------------------------------------------------
-- 21. 规则配置（创新点：作物阶段用水建议权重，合计必须 100）
-- ---------------------------------------------------------------------
CREATE TABLE `rule_config` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `name` VARCHAR(80) NOT NULL COMMENT '规则名称',
  `version` VARCHAR(20) NOT NULL COMMENT '版本号',
  `crop_weight` INT NOT NULL COMMENT '作物类型权重',
  `stage_weight` INT NOT NULL COMMENT '生育阶段权重',
  `area_weight` INT NOT NULL COMMENT '地块面积权重',
  `soil_weight` INT NOT NULL COMMENT '土壤等级权重',
  `rain_weight` INT NOT NULL COMMENT '近期降雨权重',
  `history_weight` INT NOT NULL COMMENT '历史单耗权重',
  `status` VARCHAR(20) NOT NULL DEFAULT 'DISABLED' COMMENT 'ACTIVE 生效/DISABLED 停用',
  `effective_time` DATETIME DEFAULT NULL COMMENT '生效时间',
  `create_by` VARCHAR(50) DEFAULT NULL COMMENT '创建人',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_rule_version` (`version`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用水建议规则';

-- ---------------------------------------------------------------------
-- 22. 用水建议计算留痕（输入快照 + 明细 + 人工修正）
-- ---------------------------------------------------------------------
CREATE TABLE `water_advice` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `task_id` BIGINT DEFAULT NULL COMMENT '关联任务',
  `farmland_id` BIGINT NOT NULL COMMENT '地块',
  `rule_id` BIGINT NOT NULL COMMENT '规则版本',
  `rule_version` VARCHAR(20) NOT NULL COMMENT '规则版本号快照',
  `snapshot` TEXT NOT NULL COMMENT '输入快照 JSON',
  `crop_score` DECIMAL(6,2) NOT NULL DEFAULT 0 COMMENT '作物得分',
  `stage_score` DECIMAL(6,2) NOT NULL DEFAULT 0 COMMENT '阶段得分',
  `area_score` DECIMAL(6,2) NOT NULL DEFAULT 0 COMMENT '面积得分',
  `soil_score` DECIMAL(6,2) NOT NULL DEFAULT 0 COMMENT '土壤得分',
  `rain_score` DECIMAL(6,2) NOT NULL DEFAULT 0 COMMENT '降雨得分',
  `history_score` DECIMAL(6,2) NOT NULL DEFAULT 0 COMMENT '历史得分',
  `total_score` DECIMAL(6,2) NOT NULL DEFAULT 0 COMMENT '加权总分',
  `suggest_volume` DECIMAL(12,2) NOT NULL COMMENT '建议水量 m³',
  `quota_volume` DECIMAL(12,2) NOT NULL COMMENT '对比定额 m³',
  `deviation` DECIMAL(6,2) NOT NULL DEFAULT 0 COMMENT '偏差百分比',
  `grade` VARCHAR(20) NOT NULL COMMENT 'RECOMMEND 推荐/REVIEW 需复核/DEVIATE 偏差较大/INSUFFICIENT 数据不足',
  `explain_main` VARCHAR(300) DEFAULT NULL COMMENT '主要影响因素',
  `explain_missing` VARCHAR(300) DEFAULT NULL COMMENT '未满足条件',
  `explain_improve` VARCHAR(300) DEFAULT NULL COMMENT '可改进项',
  `adjust_volume` DECIMAL(12,2) DEFAULT NULL COMMENT '人工修正水量',
  `adjust_reason` VARCHAR(300) DEFAULT NULL COMMENT '修正原因',
  `adjust_by` VARCHAR(50) DEFAULT NULL COMMENT '修正人',
  `adjust_time` DATETIME DEFAULT NULL COMMENT '修正时间',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '计算时间',
  PRIMARY KEY (`id`),
  KEY `idx_advice_land` (`farmland_id`),
  KEY `idx_advice_task` (`task_id`),
  KEY `idx_advice_grade` (`grade`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用水建议计算留痕';

-- ---------------------------------------------------------------------
-- 23. 计费参数（分段单价与免费定额，供费用核算读取）
-- ---------------------------------------------------------------------
CREATE TABLE `fee_rule` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `name` VARCHAR(80) NOT NULL COMMENT '规则名称',
  `base_price` DECIMAL(8,2) NOT NULL COMMENT '定额内单价 元/m³',
  `excess_price` DECIMAL(8,2) NOT NULL COMMENT '超额单价 元/m³',
  `free_quota_per_mu` DECIMAL(8,2) NOT NULL DEFAULT 30 COMMENT '每亩免费定额 m³',
  `status` VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' COMMENT 'ACTIVE/DISABLED',
  `effective_time` DATETIME DEFAULT NULL COMMENT '生效时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='计费规则';
""")

# ---------------- 基础数据 ----------------
orgs = [
    (1, "ORG-BUREAU", "灌区管理所", 0, "BUREAU", 1),
    (2, "ORG-DISPATCH", "调度中心", 1, "STATION", 2),
    (3, "ORG-NORTH", "北干渠站", 1, "STATION", 3),
    (4, "ORG-EAST", "东支渠站", 1, "STATION", 4),
    (5, "ORG-SOUTH", "南干渠站", 1, "STATION", 5),
    (6, "ORG-WEST", "西支渠站", 1, "STATION", 6),
]
S.append(insert("sys_org", ["id", "code", "name", "parent_id", "org_type", "sort_no"], orgs))

roles = [
    (1, "admin", "灌区管理员", "ALL", "维护台账、审批计划、计费规则、水权定额与统计"),
    (2, "dispatcher", "调度员", "DEPT", "综合水源可用量、渠道与优先级编制灌溉计划"),
    (3, "operator", "放水员", "SELF", "执行任务，记录开始结束表数、实际水量与异常"),
    (4, "farmer", "种植户", "SELF", "维护承包地块，提交用水申请并查看费用"),
]
S.append(insert("sys_role", ["id", "code", "name", "data_scope", "remark"], roles))

users = []
user_def = [
    (1, "admin", "张建民", 1, 1, "13800001001"),
    (2, "dispatcher01", "王海涛", 2, 2, "13800001002"),
    (3, "dispatcher02", "马晓东", 2, 2, "13800001003"),
    (4, "operator01", "刘卫东", 3, 3, "13800001004"),
    (5, "operator02", "陈立新", 3, 4, "13800001005"),
    (6, "operator03", "杨春生", 3, 5, "13800001006"),
    (7, "operator04", "郭建军", 3, 6, "13800001007"),
    (8, "farmer01", "李国强", 4, 3, "13800001008"),
    (9, "farmer02", "王秀兰", 4, 3, "13800001009"),
    (10, "farmer03", "赵德海", 4, 4, "13800001010"),
    (11, "farmer04", "孙立平", 4, 5, "13800001011"),
    (12, "farmer05", "陈志远", 4, 6, "13800001012"),
]
for idx, (uid, uname, rname, rid, oid, phone) in enumerate(user_def):
    users.append((uid, uname, PWD, rname, phone, f"{uname}@irrig.local",
                  img("avatar", idx, 6), rid, oid, 1, 0, None, ts(200 - idx * 9, 8, 30), ts(200 - idx * 9, 8, 30)))
S.append(insert("sys_user", ["id", "username", "password", "real_name", "phone", "email", "avatar",
                             "role_id", "org_id", "status", "login_fail_count", "lock_until",
                             "last_login_time", "create_time"], users))

# 菜单：目录 + 菜单 + 按钮
menus = [
    (1, 0, "农业用水分析", "/dashboard", "dashboard", "C", "dashboard:view", 1),
    (2, 0, "地块用水地图", "/farmland", "map", "C", "farmland:view", 2),
    (3, 0, "用水申请", "/application", "application", "C", "application:view", 3),
    (4, 0, "灌溉计划", "/plan", "plan", "C", "plan:view", 4),
    (5, 0, "执行任务", "/task", "task", "C", "task:view", 5),
    (6, 0, "费用台账", "/fee", "fee", "C", "fee:view", 6),
    (7, 0, "水权定额", "/quota", "quota", "C", "quota:view", 7),
    (8, 0, "水源与渠道", "/source", "source", "C", "source:view", 8),
    (9, 0, "用水建议", "/advice", "advice", "C", "advice:view", 9),
    (10, 0, "用水统计", "/analysis", "chart", "C", "analysis:view", 10),
    (11, 0, "系统管理", "/system", "system", "C", "system:view", 99),
    (12, 11, "用户管理", "/system/user", "user", "C", "system:user", 1),
    (13, 11, "角色管理", "/system/role", "shield", "C", "system:role", 2),
    (14, 11, "菜单管理", "/system/menu", "menu", "C", "system:menu", 3),
    (15, 11, "字典管理", "/system/dict", "book", "C", "system:dict", 4),
    (16, 11, "操作日志", "/system/log", "log", "C", "system:log", 5),
    (17, 2, "新增地块", None, None, "F", "farmland:add", 1),
    (18, 2, "编辑地块", None, None, "F", "farmland:edit", 2),
    (19, 3, "提交申请", None, None, "F", "application:add", 1),
    (20, 3, "审核申请", None, None, "F", "application:audit", 2),
    (21, 4, "编制计划", None, None, "F", "plan:add", 1),
    (22, 4, "审批计划", None, None, "F", "plan:audit", 2),
    (23, 5, "执行录入", None, None, "F", "task:execute", 1),
    (24, 5, "异常上报", None, None, "F", "task:exception", 2),
    (25, 9, "规则配置", None, None, "F", "advice:rule", 1),
    (26, 9, "人工修正", None, None, "F", "advice:adjust", 2),
    (27, 6, "费用核算", None, None, "F", "fee:calc", 1),
    (28, 7, "分配定额", None, None, "F", "quota:assign", 1),
    (29, 8, "台账维护", None, None, "F", "source:edit", 1),
]
S.append(insert("sys_menu", ["id", "parent_id", "name", "path", "icon", "menu_type", "perm", "sort_no"], menus))

# 角色菜单：管理员全量；调度员 1,2,4,5,8,9,10,21-24；放水员 1,5,10,23,24；种植户 2,3,6,9
rm = []
admin_ids = [m[0] for m in menus]
disp_ids = [1, 2, 4, 5, 8, 9, 10, 21, 22, 23, 24]
oper_ids = [1, 5, 10, 23, 24]
farm_ids = [1, 2, 3, 6, 9, 19]
for mid in admin_ids:
    rm.append((1, mid))
# 隐藏「菜单管理」选项（菜单 14）不给非管理员
for mid in disp_ids:
    rm.append((2, mid))
for mid in oper_ids:
    rm.append((3, mid))
for mid in farm_ids:
    rm.append((4, mid))
S.append(insert("sys_role_menu", ["id", "role_id", "menu_id"], [(i + 1, r, m) for i, (r, m) in enumerate(rm)]))

dicts = []
d = 1
for label, value in [("苗期", "SEEDLING"), ("分蘖期", "TILLERING"), ("拔节期", "JOINTING"),
                     ("孕穗期", "BOOTING"), ("抽穗期", "HEADING"), ("结果期", "FRUITING"),
                     ("果实膨大期", "ENLARGING"), ("成熟期", "MATURE")]:
    dicts.append((d, "growth_stage", label, value, d, 1)); d += 1
for label, value in [("壤土", "LOAM"), ("黏土", "CLAY"), ("砂壤土", "SANDY_LOAM"), ("砂土", "SAND")]:
    dicts.append((d, "soil_type", label, value, d, 1)); d += 1
for label, value in [("滴灌", "DRIP"), ("喷灌", "SPRINKLER"), ("渠道灌溉", "CHANNEL"), ("漫灌", "FLOOD")]:
    dicts.append((d, "irrigation_type", label, value, d, 1)); d += 1
for label, value in [("紧急", "URGENT"), ("普通", "NORMAL")]:
    dicts.append((d, "urgency", label, value, d, 1)); d += 1
for label, value in [("渠道堵塞", "BLOCK"), ("漏水", "LEAK"), ("设备故障", "FAULT"), ("水量不足", "SHORT")]:
    dicts.append((d, "exception_type", label, value, d, 1)); d += 1
for label, value in [("水库", "RESERVOIR"), ("机井", "WELL"), ("河道", "RIVER"), ("塘坝", "POND")]:
    dicts.append((d, "source_type", label, value, d, 1)); d += 1
S.append(insert("sys_dict_item", ["id", "dict_type", "label", "value", "sort_no", "status"], dicts))

sources = [
    (1, "WS-01", "北干渠水库", "RESERVOIR", 12000, 8640, "王海涛", "13800001002", img("source", 0, 4), "NORMAL", "库容充足，可保障北干渠片区", ts(180, 8, 10)),
    (2, "WS-02", "东支渠机井群", "WELL", 3600, 2140, "赵德海", "13800001010", img("source", 1, 4), "NORMAL", "6 眼机井，2 眼轮休", ts(175, 9, 20)),
    (3, "WS-03", "南干渠引水口", "RIVER", 9000, 3200, "孙立平", "13800001011", img("source", 2, 4), "SHORT", "上游来水偏少，按 60% 限供", ts(170, 14, 5)),
    (4, "WS-04", "西支渠塘坝", "POND", 1800, 0, "陈志远", "13800001012", img("source", 3, 4), "STOP", "清淤检修，预计 11 月中旬恢复", ts(165, 10, 40)),
]
S.append(insert("water_source", ["id", "code", "name", "source_type", "design_supply", "available_volume",
                                 "manager", "phone", "photo", "status", "remark", "create_time"], sources))

canals = [
    (1, "CN-01", "北干渠", 1, "MAIN", 1.200, 12.40, "NORMAL", "覆盖北干渠片区 4 个村", ts(178, 9, 0)),
    (2, "CN-02", "东支渠", 2, "BRANCH", 0.450, 6.80, "NORMAL", None, ts(177, 10, 0)),
    (3, "CN-03", "南干渠", 3, "MAIN", 0.350, 9.20, "LIMIT", "受来水影响限流运行", ts(176, 11, 0)),
    (4, "CN-04", "西支渠", 4, "BRANCH", 0.200, 4.60, "CLOSED", "塘坝检修期间停水", ts(175, 15, 0)),
    (5, "CN-05", "北干渠一支", 1, "BRANCH", 0.380, 3.10, "NORMAL", None, ts(174, 9, 30)),
    (6, "CN-06", "北干渠二支", 1, "BRANCH", 0.320, 2.80, "NORMAL", None, ts(173, 9, 30)),
    (7, "CN-07", "东支渠一支", 2, "BRANCH", 0.220, 2.20, "NORMAL", None, ts(172, 14, 0)),
    (8, "CN-08", "南干渠一支", 3, "BRANCH", 0.150, 3.60, "LIMIT", "与 4# 闸共用渠段", ts(171, 16, 0)),
]
S.append(insert("canal", ["id", "code", "name", "source_id", "canal_level", "design_flow", "length_km",
                          "status", "remark", "create_time"], canals))

gates = []
gate_def = [
    (1, "GT-01", "北干渠 1# 闸", 1, 0.400, 100, "OPEN"),
    (2, "GT-02", "北干渠 2# 闸", 1, 0.380, 85, "OPEN"),
    (3, "GT-03", "北干渠 3# 闸", 1, 0.300, 100, "OPEN"),
    (4, "GT-04", "东支渠 1# 闸", 2, 0.240, 90, "OPEN"),
    (5, "GT-05", "东支渠 2# 闸", 2, 0.200, 100, "OPEN"),
    (6, "GT-06", "南干渠 4# 闸", 3, 0.350, 60, "OPEN"),
    (7, "GT-07", "南干渠 5# 闸", 3, 0.300, 55, "OPEN"),
    (8, "GT-08", "西支渠 3# 闸", 4, 0.180, 0, "CLOSED"),
    (9, "GT-09", "北干一支 1# 闸", 5, 0.180, 100, "OPEN"),
    (10, "GT-10", "北干二支 1# 闸", 6, 0.150, 100, "OPEN"),
    (11, "GT-11", "东支一支 1# 闸", 7, 0.120, 100, "FAULT"),
    (12, "GT-12", "南干一支 1# 闸", 8, 0.100, 70, "OPEN"),
]
for gid, code, name, cid, flow, deg, st in gate_def:
    gates.append((gid, code, name, cid, flow, deg, st, None))
S.append(insert("gate", ["id", "code", "name", "canal_id", "design_flow", "open_degree", "status", "remark"], gates))

# 地块 26 条
regions = ["北干渠片区", "东支渠片区", "南干渠片区", "西支渠片区"]
crops = ["水稻", "小麦", "玉米", "蔬菜", "果树", "棉花"]
stages_by_crop = {
    "水稻": ["苗期", "分蘖期", "孕穗期", "抽穗期", "成熟期"],
    "小麦": ["苗期", "分蘖期", "拔节期", "抽穗期", "成熟期"],
    "玉米": ["苗期", "拔节期", "抽穗期", "成熟期"],
    "蔬菜": ["苗期", "结果期", "成熟期"],
    "果树": ["结果期", "果实膨大期", "成熟期"],
    "棉花": ["苗期", "拔节期", "结果期"],
}
soils = ["壤土", "黏土", "砂壤土", "砂土"]
irrig = ["滴灌", "喷灌", "渠道灌溉", "漫灌"]
farmers = [(8, "李国强", 3), (9, "王秀兰", 3), (10, "赵德海", 4), (11, "孙立平", 5), (12, "陈志远", 6)]
land_names = ["一号地", "二号地", "三号地", "五号地", "七号地", "九号地", "十号地"]

farmlands = []
quota_rows = []
FARM_N = 26
for i in range(FARM_N):
    fid = i + 1
    region = regions[i % 4]
    prefix = ["北干渠", "东支渠", "南干渠", "西支渠"][i % 4]
    name = f"{prefix}{land_names[i % len(land_names)]}"
    if i >= 7:
        name = f"{prefix}{land_names[(i // 4) % len(land_names)]}"
    crop = crops[i % 6]
    stage = stages_by_crop[crop][(i * 3 + 1) % len(stages_by_crop[crop])]
    area = round(48 + (i * 17) % 280 + 0.4 * (i % 5), 2)
    owner_id, owner_name, org_id = farmers[i % 5]
    st = "NORMAL"
    if i in (10, 19):
        st = "SHORT"
    elif i in (4, 15):
        st = "FALLOW"
    elif i == 22:
        st = "STOP"
    code = f"FD-2026-{31 + i:04d}"
    farmlands.append((fid, code, name, area, crop, stage, soils[i % 4], irrig[i % 4], region,
                      f"{region}{name}渠段东侧", owner_id, owner_name, org_id, img("farmland", i, 8),
                      st, 0, 0, ts(180 - i * 6, 8 + i % 8, (i * 11) % 60), ts(30 - i % 25, 10, 20)))
S.append(insert("farmland", ["id", "code", "name", "area", "crop", "growth_stage", "soil_type",
                             "irrigation_type", "region", "address", "owner_id", "owner_name", "org_id",
                             "photo", "status", "deleted", "version", "create_time", "update_time"], farmlands))

# 定额：26 条，部分超额 / 余量不足
for i, f in enumerate(farmlands):
    fid, code, name, area = f[0], f[1], f[2], f[3]
    quota = round(area * 23 + 400, 2)
    if i == 10:
        used = round(quota * 1.047, 2)
    elif i == 19:
        used = round(quota * 1.021, 2)
    elif i == 1:
        used = round(quota * 0.963, 2)
    elif i == 20:
        used = round(quota * 0.948, 2)
    elif i == 4 or i == 15:
        used = round(quota * 0.18, 2)
    else:
        used = round(quota * (0.28 + (i % 7) * 0.09), 2)
    remain = round(quota - used, 2)
    st = "NORMAL"
    if remain < 0:
        st = "OVER"
    elif remain < quota * 0.1:
        st = "SHORT"
    quota_rows.append((i + 1, 2026, fid, f[10], f[11], quota, used, remain, st, 0,
                       ts(150 - i * 4, 9, 15), ts(20 - i % 18, 15, 30)))
S.append(insert("water_quota", ["id", "quota_year", "farmland_id", "farmer_id", "farmer_name",
                                "quota_volume", "used_volume", "remaining_volume", "status", "version",
                                "create_time", "update_time"], quota_rows))

# 用水申请 48 条
app_status = ["PENDING_AUDIT"] * 8 + ["PENDING_SCHEDULE"] * 10 + ["SCHEDULED"] * 24 + ["REJECTED"] * 6
random.shuffle(app_status)
apps = []
for i in range(48):
    f = farmlands[i % FARM_N]
    st = app_status[i]
    vol = round(f[3] * (18 + (i % 9) * 1.6), 2)
    urgency = "URGENT" if i % 5 == 0 else "NORMAL"
    expect = (BASE + timedelta(days=(i % 12) - 6)).date().isoformat()
    opinion, audit_by, audit_time = None, None, None
    if st in ("SCHEDULED", "REJECTED"):
        audit_by = "张建民"
        audit_time = ts(28 - i % 20, 10, 30)
        opinion = "定额充足，转调度排程" if st == "SCHEDULED" else "申请水量超出本地块年度定额余量，请核减后重新提交"
    apps.append((i + 1, f"AP-20261031-{i + 1:03d}", f[0], f[4], f[5], expect, vol, urgency,
                 f[10], f[11], st, opinion, audit_by, audit_time, 0,
                 ts(30 - i % 28, 8 + i % 9, (i * 13) % 60), ts(12 - i % 11, 16, 10)))
S.append(insert("water_application", ["id", "code", "farmland_id", "crop", "growth_stage", "expect_date",
                                      "apply_volume", "urgency", "applicant_id", "applicant_name", "status",
                                      "audit_opinion", "audit_by", "audit_time", "version",
                                      "create_time", "update_time"], apps))

# 计划 34 条：覆盖全部阶段
plan_status = (["DRAFT"] * 3 + ["AUDITING"] * 4 + ["ISSUED"] * 9 + ["EXECUTING"] * 6 +
               ["CONFIRMING"] * 5 + ["ARCHIVED"] * 5 + ["CONFLICT"] * 2)
assert len(plan_status) == 34
plans = []
for i in range(34):
    f = farmlands[i % FARM_N]
    gate_id = (i % 12) + 1
    canal_id = gates[gate_id - 1][3]
    st = plan_status[i]
    day_offset = (i % 20) - 12
    start_h = 8 + (i % 4) * 3
    p_start = (BASE + timedelta(days=day_offset)).replace(hour=start_h, minute=0, second=0)
    p_end = p_start + timedelta(hours=3 + (i % 3), minutes=30)
    vol = round(f[3] * (17 + (i % 7) * 1.4), 2)
    pr = "HIGH" if i % 4 == 0 else ("LOW" if i % 4 == 3 else "NORMAL")
    reason = None
    if st == "REJECTED":
        reason = "渠道容量不足，需调整至夜间时段"
    if st == "CONFLICT":
        reason = None
    plans.append((i + 1, f"PL-2026{(p_start.strftime('%m%d'))}-{i + 1:03d}", i + 1 if i < 48 else None,
                  f[0], canal_id, gate_id, p_start.strftime("%Y-%m-%d %H:%M:%S"),
                  p_end.strftime("%Y-%m-%d %H:%M:%S"), vol, pr, st, 2, "王海涛", reason,
                  "同一闸口重叠时段需复核" if st == "CONFLICT" else None, 0,
                  ts(26 - i % 24, 9, 10), ts(10 - i % 9, 15, 40)))
S.append(insert("irrigation_plan", ["id", "code", "application_id", "farmland_id", "canal_id", "gate_id",
                                    "plan_start", "plan_end", "plan_volume", "priority", "status",
                                    "dispatcher_id", "dispatcher_name", "reject_reason", "remark", "version",
                                    "create_time", "update_time"], plans))

# 任务 40 条（由已下达及之后状态的计划派生）
task_status = ["FINISHED"] * 22 + ["RUNNING"] * 5 + ["PENDING"] * 8 + ["INTERRUPTED"] * 5
tasks = []
records = []
meters = []
meter_idx = 1
for i in range(40):
    p = plans[i % 34]
    pid, pstart, pend, pvol, f_id = p[0], p[6], p[7], p[8], p[3]
    st = task_status[i]
    op = [(4, "刘卫东"), (5, "陈立新"), (6, "杨春生"), (7, "郭建军")][i % 4]
    base_reading = round(12000 + i * 137.4, 2)
    start_r = end_r = act = None
    stime = etime = None
    photo = img("task", i, 4) if st in ("FINISHED", "RUNNING", "INTERRUPTED") else None
    recv, ctime, ireason = None, None, None
    if st in ("FINISHED", "INTERRUPTED"):
        start_r = base_reading
        act = round(pvol * (0.86 + (i % 6) * 0.05), 2)
        end_r = round(base_reading + act, 2)
        stime = pstart
        etime = (datetime.strptime(pstart, "%Y-%m-%d %H:%M:%S") +
                 timedelta(hours=2 + i % 3, minutes=40)).strftime("%Y-%m-%d %H:%M:%S")
        recv = farmlands[f_id - 1][11]
        ctime = etime
        if st == "INTERRUPTED":
            ireason = ["渠道堵塞导致末端无水", "渠段发现漏水点紧急停水", "闸门启闭机故障无法调流", "水源可用量不足临时中断"][i % 4]
    elif st == "RUNNING":
        start_r = base_reading
        stime = pstart
    tasks.append((i + 1, f"TK-20261031-{i + 1:03d}", pid, f_id, op[0], op[1], pvol,
                  start_r, end_r, act, stime, etime, st, photo, recv, ctime, ireason, 0,
                  ts(20 - i % 18, 8, 20), ts(6 - i % 5, 17, 25)))
    if act:
        records.append((i + 1, i + 1, meter_idx, start_r, end_r, act, etime, op[0], op[1],
                        img("meter", i, 2), "现场抄表，表盘清晰"))
        meters.append((meter_idx, f"WM-{meter_idx:03d}", f"{farmlands[f_id - 1][2]}计量表", None,
                       f_id, base_reading, end_r, "2025-11-20", img("meter", i, 2), "NORMAL"))
        meter_idx += 1
S.append(insert("irrigation_task", ["id", "code", "plan_id", "farmland_id", "operator_id", "operator_name",
                                    "plan_volume", "start_reading", "end_reading", "actual_volume",
                                    "start_time", "end_time", "status", "photo", "receiver_name",
                                    "confirm_time", "interrupt_reason", "version",
                                    "create_time", "update_time"], tasks))

# 补齐水表台账到 12 条
while meter_idx <= 12:
    fid = (meter_idx * 2) % FARM_N + 1
    meters.append((meter_idx, f"WM-{meter_idx:03d}", f"{farmlands[fid - 1][2]}计量表", None, fid,
                   1000 + meter_idx * 20, 1200 + meter_idx * 22, "2025-12-01", img("meter", meter_idx, 2), "NORMAL"))
    meter_idx += 1
S.append(insert("water_meter", ["id", "code", "name", "gate_id", "farmland_id", "init_reading",
                                "current_reading", "install_date", "photo", "status"], meters))
S.append(insert("water_meter_record", ["id", "task_id", "meter_id", "start_reading", "end_reading",
                                       "volume", "record_time", "recorder_id", "recorder_name",
                                       "photo", "remark"], records))

# 费用 32 条（按已完成任务核算）
fees = []
for i in range(32):
    t = tasks[i]
    tid, fid, act = t[0], t[3], t[9]
    if not act:
        continue
    f = farmlands[fid - 1]
    base_cap = round(f[3] * 12, 2)   # 单次灌溉的定额内额度
    base_vol = min(act, base_cap)
    excess = round(max(0, act - base_cap), 2)
    amount = round(base_vol * 0.42 + excess * 0.55, 2)
    st = "PAID" if i % 5 in (1, 2, 3) else "UNPAID"
    if i == 7:
        st = "WAIVED"
    month = t[10][:7] if t[10] else "2026-10"
    fees.append((len(fees) + 1, f"FE-{month.replace('-', '')}-{len(fees) + 1:03d}", tid, fid, f[11],
                 act, base_vol, excess, 0.42, 0.55, amount, month, st,
                 ts(3 + i % 10, 11, 0) if st == "PAID" else None, ts(12 - i % 10, 18, 0)))
S.append(insert("fee_ledger", ["id", "code", "task_id", "farmland_id", "farmer_name", "actual_volume",
                               "base_volume", "excess_volume", "base_price", "excess_price", "amount",
                               "bill_month", "status", "pay_time", "create_time"], fees))

# 异常 8 条
exc_types = ["BLOCK", "LEAK", "FAULT", "SHORT"]
exc_desc = {
    "BLOCK": "渠段内有秸秆淤积，过流断面缩小约三分之一",
    "LEAK": "支渠衬砌板接缝渗漏，沿渠肩出现明显湿痕",
    "FAULT": "闸门启闭机电机烧毁，无法电动调流",
    "SHORT": "水源可用量低于计划值，末端地块供水中断",
}
excs = []
for i in range(8):
    tid = tasks[(i * 5) % 40][0]
    et = exc_types[i % 4]
    excs.append((i + 1, tid, et, exc_desc[et], round(60 + i * 47.5, 2),
                 "已组织人工清淤并恢复通水" if i % 2 == 0 else None, img("task", i + 2, 4),
                 [(4, "刘卫东"), (5, "陈立新"), (6, "杨春生"), (7, "郭建军")][i % 4][0],
                 [(4, "刘卫东"), (5, "陈立新"), (6, "杨春生"), (7, "郭建军")][i % 4][1],
                 "HANDLED" if i % 2 == 0 else "OPEN", ts(14 - i, 13, 20)))
S.append(insert("exception_record", ["id", "task_id", "exc_type", "description", "loss_volume",
                                     "handle_result", "photo", "reporter_id", "reporter_name",
                                     "status", "create_time"], excs))

# 规则 3 个版本
S.append(insert("rule_config", ["id", "name", "version", "crop_weight", "stage_weight", "area_weight",
                                "soil_weight", "rain_weight", "history_weight", "status",
                                "effective_time", "create_by", "create_time"], [
    (1, "作物阶段用水建议（初版）", "v1", 20, 20, 20, 15, 15, 10, "DISABLED", ts(160, 9, 0), "张建民", ts(160, 9, 0)),
    (2, "作物阶段用水建议（调整面积权重）", "v2", 22, 20, 18, 15, 15, 10, "DISABLED", ts(90, 9, 0), "张建民", ts(90, 9, 0)),
    (3, "作物阶段用水建议（现行）", "v3", 24, 22, 18, 14, 12, 10, "ACTIVE", ts(46, 9, 0), "张建民", ts(46, 9, 0)),
]))

# 用水建议 32 条
grades = ["RECOMMEND"] * 14 + ["REVIEW"] * 9 + ["DEVIATE"] * 7 + ["INSUFFICIENT"] * 2
advices = []
for i in range(32):
    f = farmlands[i % FARM_N]
    tid = tasks[i][0] if i < 40 else None
    quota = quota_rows[i % 26][5]
    grade = grades[i]
    crop_s = round(55 + (i % 5) * 8.5, 2)
    stage_s = round(48 + (i % 6) * 7.2, 2)
    area_s = round(40 + (i % 7) * 6.8, 2)
    soil_s = round(42 + (i % 4) * 9.5, 2)
    rain_s = round(30 + (i % 8) * 7.4, 2)
    hist_s = round(46 + (i % 5) * 8.1, 2)
    total = round(crop_s * .24 + stage_s * .22 + area_s * .18 + soil_s * .14 + rain_s * .12 + hist_s * .10, 2)
    if grade == "INSUFFICIENT":
        suggest = 0
        dev = 0
        main = "缺少近期降雨记录，历史单耗不足 3 年，暂不给出建议水量"
        missing = "近期降雨与历史单耗缺失"
        improve = "补录近 7 天降雨量与最近 3 年灌溉记录后重新计算"
    else:
        suggest = round(quota * (0.9 + (i % 9) * 0.02), 2)
        dev = round((suggest - quota) / quota * 100, 2)
        main = "分蘖期需水系数偏高，作物与阶段合计权重 46%" if i % 2 == 0 else "土壤保水等级偏低，蒸发损失高于一级地块"
        missing = "近 7 天降雨 18.6 mm，已折减 6%" if i % 3 == 0 else "渠道末段水头不足，实际过流低于设计值"
        improve = "建议改为傍晚时段灌溉，可减少约 6% 蒸发损失"
    adj_v, adj_r, adj_by, adj_t = None, None, None, None
    if i % 6 == 3:
        adj_v = round(suggest * 1.01, 2)
        adj_r = "渠道末段水头不足需补量"
        adj_by = "王海涛"
        adj_t = ts(5, 16, 10)
    snapshot = ('{"crop":"%s","stage":"%s","area":%s,"soil":"%s","rain":%s,"history":%s}' %
                (f[4], f[5], f[3], f[6], round(8 + i % 20 + 0.6, 2), round(40 + i % 12 + 0.2, 2)))
    advices.append((i + 1, tid, f[0], 3, "v3", snapshot, crop_s, stage_s, area_s, soil_s, rain_s,
                    hist_s, total, suggest, quota, dev, grade, main, missing, improve,
                    adj_v, adj_r, adj_by, adj_t, ts(18 - i % 16, 9, 5)))
S.append(insert("water_advice", ["id", "task_id", "farmland_id", "rule_id", "rule_version", "snapshot",
                                 "crop_score", "stage_score", "area_score", "soil_score", "rain_score",
                                 "history_score", "total_score", "suggest_volume", "quota_volume",
                                 "deviation", "grade", "explain_main", "explain_missing",
                                 "explain_improve", "adjust_volume", "adjust_reason", "adjust_by",
                                 "adjust_time", "create_time"], advices))

S.append(insert("fee_rule", ["id", "name", "base_price", "excess_price", "free_quota_per_mu",
                             "status", "effective_time"], [
    (1, "2026 年度农业水价", 0.42, 0.55, 30.00, "ACTIVE", ts(200, 0, 0)),
]))

# 消息 12 条
msgs = []
for i in range(12):
    t = tasks[i]
    msgs.append((i + 1, "任务待执行提醒" if i % 3 == 0 else ("用水申请待审核" if i % 3 == 1 else "定额余量不足预警"),
                 f"业务单据 {t[1]} 需要处理，请及时进入详情页确认。", t[1],
                 "TASK" if i % 3 == 0 else ("APPLICATION" if i % 3 == 1 else "QUOTA"),
                 [4, 1, 8][i % 3], 0 if i < 5 else 1, ts(9 - i % 8, 8 + i % 6, 15)))
S.append(insert("sys_message", ["id", "title", "content", "biz_no", "biz_type", "receiver_id",
                                "read_flag", "create_time"], msgs))

# 操作日志 48 条
logs = []
acts = [("提交申请", "DRAFT", "PENDING_AUDIT"), ("审核通过", "PENDING_AUDIT", "PENDING_SCHEDULE"),
        ("编制计划", None, "DRAFT"), ("提交审批", "DRAFT", "AUDITING"),
        ("审批通过", "AUDITING", "ISSUED"), ("下达任务", "ISSUED", "EXECUTING"),
        ("开始执行", "PENDING", "RUNNING"), ("用量确认", "RUNNING", "FINISHED"),
        ("归档", "CONFIRMING", "ARCHIVED")]
for i in range(48):
    a = acts[i % len(acts)]
    subj = apps[i % 48] if i % 2 == 0 else plans[i % 34]
    logs.append((i + 1, "APPLICATION" if i % 2 == 0 else "PLAN", subj[0], subj[1], a[0], a[1], a[2],
                 "渠道容量不足需重新排程" if i % 11 == 0 else None,
                 1 if i % 2 == 0 else 2, "张建民" if i % 2 == 0 else "王海涛",
                 ts(24 - i % 22, 9 + i % 8, (i * 17) % 60)))
S.append(insert("sys_operation_log", ["id", "biz_type", "biz_id", "biz_no", "action", "before_status",
                                      "after_status", "reason", "operator_id", "operator_name",
                                      "create_time"], logs))

S.append("""
-- ---------------------------------------------------------------------
-- 校验：各表数据量
-- ---------------------------------------------------------------------
SELECT 'sys_user' AS t, COUNT(*) AS c FROM sys_user
UNION ALL SELECT 'farmland', COUNT(*) FROM farmland
UNION ALL SELECT 'water_quota', COUNT(*) FROM water_quota
UNION ALL SELECT 'water_application', COUNT(*) FROM water_application
UNION ALL SELECT 'irrigation_plan', COUNT(*) FROM irrigation_plan
UNION ALL SELECT 'irrigation_task', COUNT(*) FROM irrigation_task
UNION ALL SELECT 'water_meter_record', COUNT(*) FROM water_meter_record
UNION ALL SELECT 'fee_ledger', COUNT(*) FROM fee_ledger
UNION ALL SELECT 'exception_record', COUNT(*) FROM exception_record
UNION ALL SELECT 'water_advice', COUNT(*) FROM water_advice;
""")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(S), encoding="utf-8")
print("写入", OUT, "行数", len(OUT.read_text().splitlines()))
