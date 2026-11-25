-- =====================================================================
-- 农田灌溉计划与用水统计系统 · 数据库初始化脚本
-- 库名：new_017  字符集：utf8mb4  引擎：InnoDB
-- 说明：脚本可重复执行（先删库重建），默认账号 admin / admin123
-- =====================================================================
DROP DATABASE IF EXISTS `new_017`;
CREATE DATABASE `new_017` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `new_017`;

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

INSERT INTO `sys_org` (`id`, `code`, `name`, `parent_id`, `org_type`, `sort_no`) VALUES
(1, 'ORG-BUREAU', '灌区管理所', 0, 'BUREAU', 1),
(2, 'ORG-DISPATCH', '调度中心', 1, 'STATION', 2),
(3, 'ORG-NORTH', '北干渠站', 1, 'STATION', 3),
(4, 'ORG-EAST', '东支渠站', 1, 'STATION', 4),
(5, 'ORG-SOUTH', '南干渠站', 1, 'STATION', 5),
(6, 'ORG-WEST', '西支渠站', 1, 'STATION', 6);
INSERT INTO `sys_role` (`id`, `code`, `name`, `data_scope`, `remark`) VALUES
(1, 'admin', '灌区管理员', 'ALL', '维护台账、审批计划、计费规则、水权定额与统计'),
(2, 'dispatcher', '调度员', 'DEPT', '综合水源可用量、渠道与优先级编制灌溉计划'),
(3, 'operator', '放水员', 'SELF', '执行任务，记录开始结束表数、实际水量与异常'),
(4, 'farmer', '种植户', 'SELF', '维护承包地块，提交用水申请并查看费用');
INSERT INTO `sys_user` (`id`, `username`, `password`, `real_name`, `phone`, `email`, `avatar`, `role_id`, `org_id`, `status`, `login_fail_count`, `lock_until`, `last_login_time`, `create_time`) VALUES
(1, 'admin', '$2b$10$ixLF2gjJd.Z7AayJNboJfeN/El.gqamvvdde/pJcbr4KK0xzi8Bte', '张建民', '13800001001', 'admin@irrig.local', '/uploads/seed/avatar/01.jpg', 1, 1, 1, 0, NULL, '2026-04-14 08:30:19', '2026-04-14 08:30:15'),
(2, 'dispatcher01', '$2b$10$ixLF2gjJd.Z7AayJNboJfeN/El.gqamvvdde/pJcbr4KK0xzi8Bte', '王海涛', '13800001002', 'dispatcher01@irrig.local', '/uploads/seed/avatar/02.jpg', 2, 2, 1, 0, NULL, '2026-04-23 08:30:48', '2026-04-23 08:30:46'),
(3, 'dispatcher02', '$2b$10$ixLF2gjJd.Z7AayJNboJfeN/El.gqamvvdde/pJcbr4KK0xzi8Bte', '马晓东', '13800001003', 'dispatcher02@irrig.local', '/uploads/seed/avatar/03.jpg', 2, 2, 1, 0, NULL, '2026-05-02 08:30:24', '2026-05-02 08:30:04'),
(4, 'operator01', '$2b$10$ixLF2gjJd.Z7AayJNboJfeN/El.gqamvvdde/pJcbr4KK0xzi8Bte', '刘卫东', '13800001004', 'operator01@irrig.local', '/uploads/seed/avatar/04.jpg', 3, 3, 1, 0, NULL, '2026-05-11 08:30:32', '2026-05-11 08:30:02'),
(5, 'operator02', '$2b$10$ixLF2gjJd.Z7AayJNboJfeN/El.gqamvvdde/pJcbr4KK0xzi8Bte', '陈立新', '13800001005', 'operator02@irrig.local', '/uploads/seed/avatar/05.jpg', 3, 4, 1, 0, NULL, '2026-05-20 08:30:13', '2026-05-20 08:30:15'),
(6, 'operator03', '$2b$10$ixLF2gjJd.Z7AayJNboJfeN/El.gqamvvdde/pJcbr4KK0xzi8Bte', '杨春生', '13800001006', 'operator03@irrig.local', '/uploads/seed/avatar/06.jpg', 3, 5, 1, 0, NULL, '2026-05-29 08:30:30', '2026-05-29 08:30:14'),
(7, 'operator04', '$2b$10$ixLF2gjJd.Z7AayJNboJfeN/El.gqamvvdde/pJcbr4KK0xzi8Bte', '郭建军', '13800001007', 'operator04@irrig.local', '/uploads/seed/avatar/01.jpg', 3, 6, 1, 0, NULL, '2026-06-07 08:30:40', '2026-06-07 08:30:10'),
(8, 'farmer01', '$2b$10$ixLF2gjJd.Z7AayJNboJfeN/El.gqamvvdde/pJcbr4KK0xzi8Bte', '李国强', '13800001008', 'farmer01@irrig.local', '/uploads/seed/avatar/02.jpg', 4, 3, 1, 0, NULL, '2026-06-16 08:30:06', '2026-06-16 08:30:58'),
(9, 'farmer02', '$2b$10$ixLF2gjJd.Z7AayJNboJfeN/El.gqamvvdde/pJcbr4KK0xzi8Bte', '王秀兰', '13800001009', 'farmer02@irrig.local', '/uploads/seed/avatar/03.jpg', 4, 3, 1, 0, NULL, '2026-06-25 08:30:49', '2026-06-25 08:30:36'),
(10, 'farmer03', '$2b$10$ixLF2gjJd.Z7AayJNboJfeN/El.gqamvvdde/pJcbr4KK0xzi8Bte', '赵德海', '13800001010', 'farmer03@irrig.local', '/uploads/seed/avatar/04.jpg', 4, 4, 1, 0, NULL, '2026-07-04 08:30:55', '2026-07-04 08:30:48'),
(11, 'farmer04', '$2b$10$ixLF2gjJd.Z7AayJNboJfeN/El.gqamvvdde/pJcbr4KK0xzi8Bte', '孙立平', '13800001011', 'farmer04@irrig.local', '/uploads/seed/avatar/05.jpg', 4, 5, 1, 0, NULL, '2026-07-13 08:30:48', '2026-07-13 08:30:37'),
(12, 'farmer05', '$2b$10$ixLF2gjJd.Z7AayJNboJfeN/El.gqamvvdde/pJcbr4KK0xzi8Bte', '陈志远', '13800001012', 'farmer05@irrig.local', '/uploads/seed/avatar/06.jpg', 4, 6, 1, 0, NULL, '2026-07-22 08:30:02', '2026-07-22 08:30:17');
INSERT INTO `sys_menu` (`id`, `parent_id`, `name`, `path`, `icon`, `menu_type`, `perm`, `sort_no`) VALUES
(1, 0, '农业用水分析', '/dashboard', 'dashboard', 'C', 'dashboard:view', 1),
(2, 0, '地块用水地图', '/farmland', 'map', 'C', 'farmland:view', 2),
(3, 0, '用水申请', '/application', 'application', 'C', 'application:view', 3),
(4, 0, '灌溉计划', '/plan', 'plan', 'C', 'plan:view', 4),
(5, 0, '执行任务', '/task', 'task', 'C', 'task:view', 5),
(6, 0, '费用台账', '/fee', 'fee', 'C', 'fee:view', 6),
(7, 0, '水权定额', '/quota', 'quota', 'C', 'quota:view', 7),
(8, 0, '水源与渠道', '/source', 'source', 'C', 'source:view', 8),
(9, 0, '用水建议', '/advice', 'advice', 'C', 'advice:view', 9),
(10, 0, '用水统计', '/analysis', 'chart', 'C', 'analysis:view', 10),
(11, 0, '系统管理', '/system', 'system', 'C', 'system:view', 99),
(12, 11, '用户管理', '/system/user', 'user', 'C', 'system:user', 1),
(13, 11, '角色管理', '/system/role', 'shield', 'C', 'system:role', 2),
(14, 11, '菜单管理', '/system/menu', 'menu', 'C', 'system:menu', 3),
(15, 11, '字典管理', '/system/dict', 'book', 'C', 'system:dict', 4),
(16, 11, '操作日志', '/system/log', 'log', 'C', 'system:log', 5),
(17, 2, '新增地块', NULL, NULL, 'F', 'farmland:add', 1),
(18, 2, '编辑地块', NULL, NULL, 'F', 'farmland:edit', 2),
(19, 3, '提交申请', NULL, NULL, 'F', 'application:add', 1),
(20, 3, '审核申请', NULL, NULL, 'F', 'application:audit', 2),
(21, 4, '编制计划', NULL, NULL, 'F', 'plan:add', 1),
(22, 4, '审批计划', NULL, NULL, 'F', 'plan:audit', 2),
(23, 5, '执行录入', NULL, NULL, 'F', 'task:execute', 1),
(24, 5, '异常上报', NULL, NULL, 'F', 'task:exception', 2),
(25, 9, '规则配置', NULL, NULL, 'F', 'advice:rule', 1),
(26, 9, '人工修正', NULL, NULL, 'F', 'advice:adjust', 2),
(27, 6, '费用核算', NULL, NULL, 'F', 'fee:calc', 1),
(28, 7, '分配定额', NULL, NULL, 'F', 'quota:assign', 1),
(29, 8, '台账维护', NULL, NULL, 'F', 'source:edit', 1);
INSERT INTO `sys_role_menu` (`id`, `role_id`, `menu_id`) VALUES
(1, 1, 1),
(2, 1, 2),
(3, 1, 3),
(4, 1, 4),
(5, 1, 5),
(6, 1, 6),
(7, 1, 7),
(8, 1, 8),
(9, 1, 9),
(10, 1, 10),
(11, 1, 11),
(12, 1, 12),
(13, 1, 13),
(14, 1, 14),
(15, 1, 15),
(16, 1, 16),
(17, 1, 17),
(18, 1, 18),
(19, 1, 19),
(20, 1, 20),
(21, 1, 21),
(22, 1, 22),
(23, 1, 23),
(24, 1, 24),
(25, 1, 25),
(26, 1, 26),
(27, 1, 27),
(28, 1, 28),
(29, 1, 29),
(30, 2, 1),
(31, 2, 2),
(32, 2, 4),
(33, 2, 5),
(34, 2, 8),
(35, 2, 9),
(36, 2, 10),
(37, 2, 21),
(38, 2, 22),
(39, 2, 23),
(40, 2, 24),
(41, 3, 1),
(42, 3, 5),
(43, 3, 10),
(44, 3, 23),
(45, 3, 24),
(46, 4, 1),
(47, 4, 2),
(48, 4, 3),
(49, 4, 6),
(50, 4, 9),
(51, 4, 19);
INSERT INTO `sys_dict_item` (`id`, `dict_type`, `label`, `value`, `sort_no`, `status`) VALUES
(1, 'growth_stage', '苗期', 'SEEDLING', 1, 1),
(2, 'growth_stage', '分蘖期', 'TILLERING', 2, 1),
(3, 'growth_stage', '拔节期', 'JOINTING', 3, 1),
(4, 'growth_stage', '孕穗期', 'BOOTING', 4, 1),
(5, 'growth_stage', '抽穗期', 'HEADING', 5, 1),
(6, 'growth_stage', '结果期', 'FRUITING', 6, 1),
(7, 'growth_stage', '果实膨大期', 'ENLARGING', 7, 1),
(8, 'growth_stage', '成熟期', 'MATURE', 8, 1),
(9, 'soil_type', '壤土', 'LOAM', 9, 1),
(10, 'soil_type', '黏土', 'CLAY', 10, 1),
(11, 'soil_type', '砂壤土', 'SANDY_LOAM', 11, 1),
(12, 'soil_type', '砂土', 'SAND', 12, 1),
(13, 'irrigation_type', '滴灌', 'DRIP', 13, 1),
(14, 'irrigation_type', '喷灌', 'SPRINKLER', 14, 1),
(15, 'irrigation_type', '渠道灌溉', 'CHANNEL', 15, 1),
(16, 'irrigation_type', '漫灌', 'FLOOD', 16, 1),
(17, 'urgency', '紧急', 'URGENT', 17, 1),
(18, 'urgency', '普通', 'NORMAL', 18, 1),
(19, 'exception_type', '渠道堵塞', 'BLOCK', 19, 1),
(20, 'exception_type', '漏水', 'LEAK', 20, 1),
(21, 'exception_type', '设备故障', 'FAULT', 21, 1),
(22, 'exception_type', '水量不足', 'SHORT', 22, 1),
(23, 'source_type', '水库', 'RESERVOIR', 23, 1),
(24, 'source_type', '机井', 'WELL', 24, 1),
(25, 'source_type', '河道', 'RIVER', 25, 1),
(26, 'source_type', '塘坝', 'POND', 26, 1);
INSERT INTO `water_source` (`id`, `code`, `name`, `source_type`, `design_supply`, `available_volume`, `manager`, `phone`, `photo`, `status`, `remark`, `create_time`) VALUES
(1, 'WS-01', '北干渠水库', 'RESERVOIR', 12000, 8640, '王海涛', '13800001002', '/uploads/seed/source/01.jpg', 'NORMAL', '库容充足，可保障北干渠片区', '2026-05-04 08:10:14'),
(2, 'WS-02', '东支渠机井群', 'WELL', 3600, 2140, '赵德海', '13800001010', '/uploads/seed/source/04.jpg', 'NORMAL', '6 眼机井，2 眼轮休', '2026-05-09 09:20:05'),
(3, 'WS-03', '南干渠引水口', 'RIVER', 9000, 3200, '孙立平', '13800001011', '/uploads/seed/source/03.jpg', 'SHORT', '上游来水偏少，按 60% 限供', '2026-05-14 14:05:14'),
(4, 'WS-04', '西支渠塘坝', 'POND', 1800, 0, '陈志远', '13800001012', '/uploads/seed/source/02.jpg', 'STOP', '清淤检修，预计 11 月中旬恢复', '2026-05-19 10:40:36');
INSERT INTO `canal` (`id`, `code`, `name`, `source_id`, `canal_level`, `design_flow`, `length_km`, `status`, `remark`, `create_time`) VALUES
(1, 'CN-01', '北干渠', 1, 'MAIN', 1.2, 12.4, 'NORMAL', '覆盖北干渠片区 4 个村', '2026-05-06 09:00:30'),
(2, 'CN-02', '东支渠', 2, 'BRANCH', 0.45, 6.8, 'NORMAL', NULL, '2026-05-07 10:00:11'),
(3, 'CN-03', '南干渠', 3, 'MAIN', 0.35, 9.2, 'LIMIT', '受来水影响限流运行', '2026-05-08 11:00:49'),
(4, 'CN-04', '西支渠', 4, 'BRANCH', 0.2, 4.6, 'CLOSED', '塘坝检修期间停水', '2026-05-09 15:00:24'),
(5, 'CN-05', '北干渠一支', 1, 'BRANCH', 0.38, 3.1, 'NORMAL', NULL, '2026-05-10 09:30:55'),
(6, 'CN-06', '北干渠二支', 1, 'BRANCH', 0.32, 2.8, 'NORMAL', NULL, '2026-05-11 09:30:42'),
(7, 'CN-07', '东支渠一支', 2, 'BRANCH', 0.22, 2.2, 'NORMAL', NULL, '2026-05-12 14:00:23'),
(8, 'CN-08', '南干渠一支', 3, 'BRANCH', 0.15, 3.6, 'LIMIT', '与 4# 闸共用渠段', '2026-05-13 16:00:51');
INSERT INTO `gate` (`id`, `code`, `name`, `canal_id`, `design_flow`, `open_degree`, `status`, `remark`) VALUES
(1, 'GT-01', '北干渠 1# 闸', 1, 0.4, 100, 'OPEN', NULL),
(2, 'GT-02', '北干渠 2# 闸', 1, 0.38, 85, 'OPEN', NULL),
(3, 'GT-03', '北干渠 3# 闸', 1, 0.3, 100, 'OPEN', NULL),
(4, 'GT-04', '东支渠 1# 闸', 2, 0.24, 90, 'OPEN', NULL),
(5, 'GT-05', '东支渠 2# 闸', 2, 0.2, 100, 'OPEN', NULL),
(6, 'GT-06', '南干渠 4# 闸', 3, 0.35, 60, 'OPEN', NULL),
(7, 'GT-07', '南干渠 5# 闸', 3, 0.3, 55, 'OPEN', NULL),
(8, 'GT-08', '西支渠 3# 闸', 4, 0.18, 0, 'CLOSED', NULL),
(9, 'GT-09', '北干一支 1# 闸', 5, 0.18, 100, 'OPEN', NULL),
(10, 'GT-10', '北干二支 1# 闸', 6, 0.15, 100, 'OPEN', NULL),
(11, 'GT-11', '东支一支 1# 闸', 7, 0.12, 100, 'FAULT', NULL),
(12, 'GT-12', '南干一支 1# 闸', 8, 0.1, 70, 'OPEN', NULL);
INSERT INTO `farmland` (`id`, `code`, `name`, `area`, `crop`, `growth_stage`, `soil_type`, `irrigation_type`, `region`, `address`, `owner_id`, `owner_name`, `org_id`, `photo`, `status`, `deleted`, `version`, `create_time`, `update_time`) VALUES
(1, 'FD-2026-0031', '北干渠一号地', 48.0, '水稻', '分蘖期', '壤土', '滴灌', '北干渠片区', '北干渠片区北干渠一号地渠段东侧', 8, '李国强', 3, '/uploads/seed/farmland/01.jpg', 'NORMAL', 0, 0, '2026-05-04 08:00:39', '2026-10-01 10:20:15'),
(2, 'FD-2026-0032', '东支渠二号地', 65.4, '小麦', '成熟期', '黏土', '喷灌', '东支渠片区', '东支渠片区东支渠二号地渠段东侧', 9, '王秀兰', 3, '/uploads/seed/farmland/08.jpg', 'NORMAL', 0, 0, '2026-05-10 09:11:06', '2026-10-02 10:20:02'),
(3, 'FD-2026-0033', '南干渠三号地', 82.8, '玉米', '成熟期', '砂壤土', '渠道灌溉', '南干渠片区', '南干渠片区南干渠三号地渠段东侧', 10, '赵德海', 4, '/uploads/seed/farmland/07.jpg', 'NORMAL', 0, 0, '2026-05-16 10:22:27', '2026-10-03 10:20:10'),
(4, 'FD-2026-0034', '西支渠五号地', 100.2, '蔬菜', '结果期', '砂土', '漫灌', '西支渠片区', '西支渠片区西支渠五号地渠段东侧', 11, '孙立平', 5, '/uploads/seed/farmland/06.jpg', 'NORMAL', 0, 0, '2026-05-22 11:33:40', '2026-10-04 10:20:26'),
(5, 'FD-2026-0035', '北干渠七号地', 117.6, '果树', '果实膨大期', '壤土', '滴灌', '北干渠片区', '北干渠片区北干渠七号地渠段东侧', 12, '陈志远', 6, '/uploads/seed/farmland/05.jpg', 'FALLOW', 0, 0, '2026-05-28 12:44:31', '2026-10-05 10:20:34'),
(6, 'FD-2026-0036', '东支渠九号地', 133.0, '棉花', '拔节期', '黏土', '喷灌', '东支渠片区', '东支渠片区东支渠九号地渠段东侧', 8, '李国强', 3, '/uploads/seed/farmland/04.jpg', 'NORMAL', 0, 0, '2026-06-03 13:55:21', '2026-10-06 10:20:29'),
(7, 'FD-2026-0037', '南干渠十号地', 150.4, '水稻', '成熟期', '砂壤土', '渠道灌溉', '南干渠片区', '南干渠片区南干渠十号地渠段东侧', 9, '王秀兰', 3, '/uploads/seed/farmland/03.jpg', 'NORMAL', 0, 0, '2026-06-09 14:06:23', '2026-10-07 10:20:24'),
(8, 'FD-2026-0038', '西支渠二号地', 167.8, '小麦', '拔节期', '砂土', '漫灌', '西支渠片区', '西支渠片区西支渠二号地渠段东侧', 10, '赵德海', 4, '/uploads/seed/farmland/02.jpg', 'NORMAL', 0, 0, '2026-06-15 15:17:23', '2026-10-08 10:20:41'),
(9, 'FD-2026-0039', '北干渠三号地', 185.2, '玉米', '拔节期', '壤土', '滴灌', '北干渠片区', '北干渠片区北干渠三号地渠段东侧', 11, '孙立平', 5, '/uploads/seed/farmland/01.jpg', 'NORMAL', 0, 0, '2026-06-21 08:28:25', '2026-10-09 10:20:23'),
(10, 'FD-2026-0040', '东支渠三号地', 202.6, '蔬菜', '结果期', '黏土', '喷灌', '东支渠片区', '东支渠片区东支渠三号地渠段东侧', 12, '陈志远', 6, '/uploads/seed/farmland/08.jpg', 'NORMAL', 0, 0, '2026-06-27 09:39:07', '2026-10-10 10:20:35'),
(11, 'FD-2026-0041', '南干渠三号地', 218.0, '果树', '果实膨大期', '砂壤土', '渠道灌溉', '南干渠片区', '南干渠片区南干渠三号地渠段东侧', 8, '李国强', 3, '/uploads/seed/farmland/07.jpg', 'SHORT', 0, 0, '2026-07-03 10:50:41', '2026-10-11 10:20:16'),
(12, 'FD-2026-0042', '西支渠三号地', 235.4, '棉花', '拔节期', '砂土', '漫灌', '西支渠片区', '西支渠片区西支渠三号地渠段东侧', 9, '王秀兰', 3, '/uploads/seed/farmland/06.jpg', 'NORMAL', 0, 0, '2026-07-09 11:01:11', '2026-10-12 10:20:02'),
(13, 'FD-2026-0043', '北干渠五号地', 252.8, '水稻', '孕穗期', '壤土', '滴灌', '北干渠片区', '北干渠片区北干渠五号地渠段东侧', 10, '赵德海', 4, '/uploads/seed/farmland/05.jpg', 'NORMAL', 0, 0, '2026-07-15 12:12:27', '2026-10-13 10:20:04'),
(14, 'FD-2026-0044', '东支渠五号地', 270.2, '小麦', '苗期', '黏土', '喷灌', '东支渠片区', '东支渠片区东支渠五号地渠段东侧', 11, '孙立平', 5, '/uploads/seed/farmland/04.jpg', 'NORMAL', 0, 0, '2026-07-21 13:23:18', '2026-10-14 10:20:24'),
(15, 'FD-2026-0045', '南干渠五号地', 287.6, '玉米', '成熟期', '砂壤土', '渠道灌溉', '南干渠片区', '南干渠片区南干渠五号地渠段东侧', 12, '陈志远', 6, '/uploads/seed/farmland/03.jpg', 'NORMAL', 0, 0, '2026-07-27 14:34:50', '2026-10-15 10:20:07'),
(16, 'FD-2026-0046', '西支渠五号地', 303.0, '蔬菜', '结果期', '砂土', '漫灌', '西支渠片区', '西支渠片区西支渠五号地渠段东侧', 8, '李国强', 3, '/uploads/seed/farmland/02.jpg', 'FALLOW', 0, 0, '2026-08-02 15:45:39', '2026-10-16 10:20:15'),
(17, 'FD-2026-0047', '北干渠七号地', 320.4, '果树', '果实膨大期', '壤土', '滴灌', '北干渠片区', '北干渠片区北干渠七号地渠段东侧', 9, '王秀兰', 3, '/uploads/seed/farmland/01.jpg', 'NORMAL', 0, 0, '2026-08-08 08:56:58', '2026-10-17 10:20:42'),
(18, 'FD-2026-0048', '东支渠七号地', 57.8, '棉花', '拔节期', '黏土', '喷灌', '东支渠片区', '东支渠片区东支渠七号地渠段东侧', 10, '赵德海', 4, '/uploads/seed/farmland/08.jpg', 'NORMAL', 0, 0, '2026-08-14 09:07:50', '2026-10-18 10:20:57'),
(19, 'FD-2026-0049', '南干渠七号地', 75.2, '水稻', '苗期', '砂壤土', '渠道灌溉', '南干渠片区', '南干渠片区南干渠七号地渠段东侧', 11, '孙立平', 5, '/uploads/seed/farmland/07.jpg', 'NORMAL', 0, 0, '2026-08-20 10:18:12', '2026-10-19 10:20:08'),
(20, 'FD-2026-0050', '西支渠七号地', 92.6, '小麦', '抽穗期', '砂土', '漫灌', '西支渠片区', '西支渠片区西支渠七号地渠段东侧', 12, '陈志远', 6, '/uploads/seed/farmland/06.jpg', 'SHORT', 0, 0, '2026-08-26 11:29:07', '2026-10-20 10:20:35'),
(21, 'FD-2026-0051', '北干渠九号地', 108.0, '玉米', '拔节期', '壤土', '滴灌', '北干渠片区', '北干渠片区北干渠九号地渠段东侧', 8, '李国强', 3, '/uploads/seed/farmland/05.jpg', 'NORMAL', 0, 0, '2026-09-01 12:40:57', '2026-10-21 10:20:12'),
(22, 'FD-2026-0052', '东支渠九号地', 125.4, '蔬菜', '结果期', '黏土', '喷灌', '东支渠片区', '东支渠片区东支渠九号地渠段东侧', 9, '王秀兰', 3, '/uploads/seed/farmland/04.jpg', 'NORMAL', 0, 0, '2026-09-07 13:51:05', '2026-10-22 10:20:10'),
(23, 'FD-2026-0053', '南干渠九号地', 142.8, '果树', '果实膨大期', '砂壤土', '渠道灌溉', '南干渠片区', '南干渠片区南干渠九号地渠段东侧', 10, '赵德海', 4, '/uploads/seed/farmland/03.jpg', 'STOP', 0, 0, '2026-09-13 14:02:32', '2026-10-23 10:20:54'),
(24, 'FD-2026-0054', '西支渠九号地', 160.2, '棉花', '拔节期', '砂土', '漫灌', '西支渠片区', '西支渠片区西支渠九号地渠段东侧', 11, '孙立平', 5, '/uploads/seed/farmland/02.jpg', 'NORMAL', 0, 0, '2026-09-19 15:13:15', '2026-10-24 10:20:55'),
(25, 'FD-2026-0055', '北干渠十号地', 177.6, '水稻', '抽穗期', '壤土', '滴灌', '北干渠片区', '北干渠片区北干渠十号地渠段东侧', 12, '陈志远', 6, '/uploads/seed/farmland/01.jpg', 'NORMAL', 0, 0, '2026-09-25 08:24:05', '2026-10-25 10:20:47'),
(26, 'FD-2026-0056', '东支渠十号地', 193.0, '小麦', '分蘖期', '黏土', '喷灌', '东支渠片区', '东支渠片区东支渠十号地渠段东侧', 8, '李国强', 3, '/uploads/seed/farmland/08.jpg', 'NORMAL', 0, 0, '2026-10-01 09:35:01', '2026-10-01 10:20:15');
INSERT INTO `water_quota` (`id`, `quota_year`, `farmland_id`, `farmer_id`, `farmer_name`, `quota_volume`, `used_volume`, `remaining_volume`, `status`, `version`, `create_time`, `update_time`) VALUES
(1, 2026, 1, 8, '李国强', 1504.0, 421.12, 1082.88, 'NORMAL', 0, '2026-06-03 09:15:54', '2026-10-11 15:30:40'),
(2, 2026, 2, 9, '王秀兰', 1904.2, 1833.74, 70.46, 'SHORT', 0, '2026-06-07 09:15:23', '2026-10-12 15:30:25'),
(3, 2026, 3, 10, '赵德海', 2304.4, 1060.02, 1244.38, 'NORMAL', 0, '2026-06-11 09:15:33', '2026-10-13 15:30:35'),
(4, 2026, 4, 11, '孙立平', 2704.6, 1487.53, 1217.07, 'NORMAL', 0, '2026-06-15 09:15:14', '2026-10-14 15:30:05'),
(5, 2026, 5, 12, '陈志远', 3104.8, 558.86, 2545.94, 'NORMAL', 0, '2026-06-19 09:15:21', '2026-10-15 15:30:36'),
(6, 2026, 6, 8, '李国强', 3459.0, 2525.07, 933.93, 'NORMAL', 0, '2026-06-23 09:15:34', '2026-10-16 15:30:12'),
(7, 2026, 7, 9, '王秀兰', 3859.2, 3164.54, 694.66, 'NORMAL', 0, '2026-06-27 09:15:13', '2026-10-17 15:30:29'),
(8, 2026, 8, 10, '赵德海', 4259.4, 1192.63, 3066.77, 'NORMAL', 0, '2026-07-01 09:15:28', '2026-10-18 15:30:40'),
(9, 2026, 9, 11, '孙立平', 4659.6, 1724.05, 2935.55, 'NORMAL', 0, '2026-07-05 09:15:41', '2026-10-19 15:30:35'),
(10, 2026, 10, 12, '陈志远', 5059.8, 2327.51, 2732.29, 'NORMAL', 0, '2026-07-09 09:15:08', '2026-10-20 15:30:32'),
(11, 2026, 11, 8, '李国强', 5414.0, 5668.46, -254.46, 'OVER', 0, '2026-07-13 09:15:51', '2026-10-21 15:30:36'),
(12, 2026, 12, 9, '王秀兰', 5814.2, 3721.09, 2093.11, 'NORMAL', 0, '2026-07-17 09:15:37', '2026-10-22 15:30:03'),
(13, 2026, 13, 10, '赵德海', 6214.4, 4536.51, 1677.89, 'NORMAL', 0, '2026-07-21 09:15:55', '2026-10-23 15:30:26'),
(14, 2026, 14, 11, '孙立平', 6614.6, 5423.97, 1190.63, 'NORMAL', 0, '2026-07-25 09:15:44', '2026-10-24 15:30:09'),
(15, 2026, 15, 12, '陈志远', 7014.8, 1964.14, 5050.66, 'NORMAL', 0, '2026-07-29 09:15:03', '2026-10-25 15:30:16'),
(16, 2026, 16, 8, '李国强', 7369.0, 1326.42, 6042.58, 'NORMAL', 0, '2026-08-02 09:15:02', '2026-10-26 15:30:58'),
(17, 2026, 17, 9, '王秀兰', 7769.2, 3573.83, 4195.37, 'NORMAL', 0, '2026-08-06 09:15:03', '2026-10-27 15:30:45'),
(18, 2026, 18, 10, '赵德海', 1729.4, 951.17, 778.23, 'NORMAL', 0, '2026-08-10 09:15:58', '2026-10-28 15:30:50'),
(19, 2026, 19, 11, '孙立平', 2129.6, 1362.94, 766.66, 'NORMAL', 0, '2026-08-14 09:15:06', '2026-10-11 15:30:00'),
(20, 2026, 20, 12, '陈志远', 2529.8, 2582.93, -53.13, 'OVER', 0, '2026-08-18 09:15:46', '2026-10-12 15:30:42'),
(21, 2026, 21, 8, '李国强', 2884.0, 2734.03, 149.97, 'SHORT', 0, '2026-08-22 09:15:04', '2026-10-13 15:30:18'),
(22, 2026, 22, 9, '王秀兰', 3284.2, 919.58, 2364.62, 'NORMAL', 0, '2026-08-26 09:15:54', '2026-10-14 15:30:12'),
(23, 2026, 23, 10, '赵德海', 3684.4, 1363.23, 2321.17, 'NORMAL', 0, '2026-08-30 09:15:23', '2026-10-15 15:30:15'),
(24, 2026, 24, 11, '孙立平', 4084.6, 1878.92, 2205.68, 'NORMAL', 0, '2026-09-03 09:15:56', '2026-10-16 15:30:46'),
(25, 2026, 25, 12, '陈志远', 4484.8, 2466.64, 2018.16, 'NORMAL', 0, '2026-09-07 09:15:52', '2026-10-17 15:30:33'),
(26, 2026, 26, 8, '李国强', 4839.0, 3096.96, 1742.04, 'NORMAL', 0, '2026-09-11 09:15:22', '2026-10-18 15:30:42');
INSERT INTO `water_application` (`id`, `code`, `farmland_id`, `crop`, `growth_stage`, `expect_date`, `apply_volume`, `urgency`, `applicant_id`, `applicant_name`, `status`, `audit_opinion`, `audit_by`, `audit_time`, `version`, `create_time`, `update_time`) VALUES
(1, 'AP-20261031-001', 1, '水稻', '分蘖期', '2026-10-25', 864.0, 'URGENT', 8, '李国强', 'PENDING_SCHEDULE', NULL, NULL, NULL, 0, '2026-10-01 08:00:25', '2026-10-19 16:10:51'),
(2, 'AP-20261031-002', 2, '小麦', '成熟期', '2026-10-26', 1281.84, 'NORMAL', 9, '王秀兰', 'SCHEDULED', '定额充足，转调度排程', '张建民', '2026-10-04 10:30:48', 0, '2026-10-02 09:13:10', '2026-10-20 16:10:48'),
(3, 'AP-20261031-003', 3, '玉米', '成熟期', '2026-10-27', 1755.36, 'NORMAL', 10, '赵德海', 'PENDING_SCHEDULE', NULL, NULL, NULL, 0, '2026-10-03 10:26:04', '2026-10-21 16:10:52'),
(4, 'AP-20261031-004', 4, '蔬菜', '结果期', '2026-10-28', 2284.56, 'NORMAL', 11, '孙立平', 'SCHEDULED', '定额充足，转调度排程', '张建民', '2026-10-06 10:30:45', 0, '2026-10-04 11:39:39', '2026-10-22 16:10:51'),
(5, 'AP-20261031-005', 5, '果树', '果实膨大期', '2026-10-29', 2869.44, 'NORMAL', 12, '陈志远', 'PENDING_AUDIT', NULL, NULL, NULL, 0, '2026-10-05 12:52:52', '2026-10-23 16:10:41'),
(6, 'AP-20261031-006', 6, '棉花', '拔节期', '2026-10-30', 3458.0, 'URGENT', 8, '李国强', 'PENDING_SCHEDULE', NULL, NULL, NULL, 0, '2026-10-06 13:05:48', '2026-10-24 16:10:20'),
(7, 'AP-20261031-007', 7, '水稻', '成熟期', '2026-10-31', 4151.04, 'NORMAL', 9, '王秀兰', 'SCHEDULED', '定额充足，转调度排程', '张建民', '2026-10-09 10:30:31', 0, '2026-10-07 14:18:32', '2026-10-25 16:10:17'),
(8, 'AP-20261031-008', 8, '小麦', '拔节期', '2026-11-01', 4899.76, 'NORMAL', 10, '赵德海', 'PENDING_AUDIT', NULL, NULL, NULL, 0, '2026-10-08 15:31:05', '2026-10-26 16:10:53'),
(9, 'AP-20261031-009', 9, '玉米', '拔节期', '2026-11-02', 5704.16, 'NORMAL', 11, '孙立平', 'SCHEDULED', '定额充足，转调度排程', '张建民', '2026-10-11 10:30:49', 0, '2026-10-09 16:44:18', '2026-10-27 16:10:44'),
(10, 'AP-20261031-010', 10, '蔬菜', '结果期', '2026-11-03', 3646.8, 'NORMAL', 12, '陈志远', 'REJECTED', '申请水量超出本地块年度定额余量，请核减后重新提交', '张建民', '2026-10-12 10:30:45', 0, '2026-10-10 08:57:26', '2026-10-28 16:10:49'),
(11, 'AP-20261031-011', 11, '果树', '果实膨大期', '2026-11-04', 4272.8, 'URGENT', 8, '李国强', 'REJECTED', '申请水量超出本地块年度定额余量，请核减后重新提交', '张建民', '2026-10-13 10:30:20', 0, '2026-10-11 09:10:53', '2026-10-29 16:10:14'),
(12, 'AP-20261031-012', 12, '棉花', '拔节期', '2026-11-05', 4990.48, 'NORMAL', 9, '王秀兰', 'PENDING_AUDIT', NULL, NULL, NULL, 0, '2026-10-12 10:23:22', '2026-10-19 16:10:46'),
(13, 'AP-20261031-013', 13, '水稻', '孕穗期', '2026-10-25', 5763.84, 'NORMAL', 10, '赵德海', 'SCHEDULED', '定额充足，转调度排程', '张建民', '2026-10-15 10:30:25', 0, '2026-10-13 11:36:03', '2026-10-20 16:10:02'),
(14, 'AP-20261031-014', 14, '小麦', '苗期', '2026-10-26', 6592.88, 'NORMAL', 11, '孙立平', 'SCHEDULED', '定额充足，转调度排程', '张建民', '2026-10-16 10:30:14', 0, '2026-10-14 12:49:49', '2026-10-21 16:10:35'),
(15, 'AP-20261031-015', 15, '玉米', '成熟期', '2026-10-27', 7477.6, 'NORMAL', 12, '陈志远', 'REJECTED', '申请水量超出本地块年度定额余量，请核减后重新提交', '张建民', '2026-10-17 10:30:07', 0, '2026-10-15 13:02:54', '2026-10-22 16:10:15'),
(16, 'AP-20261031-016', 16, '蔬菜', '结果期', '2026-10-28', 8362.8, 'URGENT', 8, '李国强', 'SCHEDULED', '定额充足，转调度排程', '张建民', '2026-10-18 10:30:21', 0, '2026-10-16 14:15:15', '2026-10-23 16:10:06'),
(17, 'AP-20261031-017', 17, '果树', '果实膨大期', '2026-10-29', 9355.68, 'NORMAL', 9, '王秀兰', 'SCHEDULED', '定额充足，转调度排程', '张建民', '2026-10-19 10:30:16', 0, '2026-10-17 15:28:38', '2026-10-24 16:10:22'),
(18, 'AP-20261031-018', 18, '棉花', '拔节期', '2026-10-30', 1780.24, 'NORMAL', 10, '赵德海', 'SCHEDULED', '定额充足，转调度排程', '张建民', '2026-10-20 10:30:48', 0, '2026-10-18 16:41:00', '2026-10-25 16:10:23'),
(19, 'AP-20261031-019', 19, '水稻', '苗期', '2026-10-31', 1353.6, 'NORMAL', 11, '孙立平', 'PENDING_AUDIT', NULL, NULL, NULL, 0, '2026-10-19 08:54:32', '2026-10-26 16:10:58'),
(20, 'AP-20261031-020', 20, '小麦', '抽穗期', '2026-11-01', 1814.96, 'NORMAL', 12, '陈志远', 'SCHEDULED', '定额充足，转调度排程', '张建民', '2026-10-22 10:30:44', 0, '2026-10-20 09:07:40', '2026-10-27 16:10:52'),
(21, 'AP-20261031-021', 21, '玉米', '拔节期', '2026-11-02', 2289.6, 'URGENT', 8, '李国强', 'PENDING_AUDIT', NULL, NULL, NULL, 0, '2026-10-21 10:20:20', '2026-10-28 16:10:38'),
(22, 'AP-20261031-022', 22, '蔬菜', '结果期', '2026-11-03', 2859.12, 'NORMAL', 9, '王秀兰', 'PENDING_AUDIT', NULL, NULL, NULL, 0, '2026-10-22 11:33:15', '2026-10-29 16:10:19'),
(23, 'AP-20261031-023', 23, '果树', '果实膨大期', '2026-11-04', 3484.32, 'NORMAL', 10, '赵德海', 'PENDING_SCHEDULE', NULL, NULL, NULL, 0, '2026-10-23 12:46:47', '2026-10-19 16:10:05'),
(24, 'AP-20261031-024', 24, '棉花', '拔节期', '2026-11-05', 4165.2, 'NORMAL', 11, '孙立平', 'REJECTED', '申请水量超出本地块年度定额余量，请核减后重新提交', '张建民', '2026-10-06 10:30:56', 0, '2026-10-24 13:59:09', '2026-10-20 16:10:52'),
(25, 'AP-20261031-025', 25, '水稻', '抽穗期', '2026-10-25', 4901.76, 'NORMAL', 12, '陈志远', 'SCHEDULED', '定额充足，转调度排程', '张建民', '2026-10-07 10:30:09', 0, '2026-10-25 14:12:02', '2026-10-21 16:10:35'),
(26, 'AP-20261031-026', 26, '小麦', '分蘖期', '2026-10-26', 5635.6, 'URGENT', 8, '李国强', 'SCHEDULED', '定额充足，转调度排程', '张建民', '2026-10-08 10:30:15', 0, '2026-10-26 15:25:43', '2026-10-22 16:10:51'),
(27, 'AP-20261031-027', 1, '水稻', '分蘖期', '2026-10-27', 1478.4, 'NORMAL', 8, '李国强', 'PENDING_SCHEDULE', NULL, NULL, NULL, 0, '2026-10-27 16:38:12', '2026-10-23 16:10:46'),
(28, 'AP-20261031-028', 2, '小麦', '成熟期', '2026-10-28', 1177.2, 'NORMAL', 9, '王秀兰', 'SCHEDULED', '定额充足，转调度排程', '张建民', '2026-10-10 10:30:36', 0, '2026-10-28 08:51:56', '2026-10-24 16:10:01'),
(29, 'AP-20261031-029', 3, '玉米', '成熟期', '2026-10-29', 1622.88, 'NORMAL', 10, '赵德海', 'PENDING_SCHEDULE', NULL, NULL, NULL, 0, '2026-10-01 09:04:41', '2026-10-25 16:10:26'),
(30, 'AP-20261031-030', 4, '蔬菜', '结果期', '2026-10-30', 2124.24, 'NORMAL', 11, '孙立平', 'REJECTED', '申请水量超出本地块年度定额余量，请核减后重新提交', '张建民', '2026-10-12 10:30:35', 0, '2026-10-02 10:17:00', '2026-10-26 16:10:47'),
(31, 'AP-20261031-031', 5, '果树', '果实膨大期', '2026-10-31', 2681.28, 'URGENT', 12, '陈志远', 'PENDING_SCHEDULE', NULL, NULL, NULL, 0, '2026-10-03 11:30:46', '2026-10-27 16:10:16'),
(32, 'AP-20261031-032', 6, '棉花', '拔节期', '2026-11-01', 3245.2, 'NORMAL', 8, '李国强', 'PENDING_AUDIT', NULL, NULL, NULL, 0, '2026-10-04 12:43:18', '2026-10-28 16:10:43'),
(33, 'AP-20261031-033', 7, '水稻', '成熟期', '2026-11-02', 3910.4, 'NORMAL', 9, '王秀兰', 'SCHEDULED', '定额充足，转调度排程', '张建民', '2026-10-15 10:30:15', 0, '2026-10-05 13:56:34', '2026-10-29 16:10:14'),
(34, 'AP-20261031-034', 8, '小麦', '拔节期', '2026-11-03', 4631.28, 'NORMAL', 10, '赵德海', 'PENDING_AUDIT', NULL, NULL, NULL, 0, '2026-10-06 14:09:13', '2026-10-19 16:10:32'),
(35, 'AP-20261031-035', 9, '玉米', '拔节期', '2026-11-04', 5407.84, 'NORMAL', 11, '孙立平', 'SCHEDULED', '定额充足，转调度排程', '张建民', '2026-10-17 10:30:36', 0, '2026-10-07 15:22:16', '2026-10-20 16:10:22'),
(36, 'AP-20261031-036', 10, '蔬菜', '结果期', '2026-11-05', 6240.08, 'URGENT', 12, '陈志远', 'SCHEDULED', '定额充足，转调度排程', '张建民', '2026-10-18 10:30:53', 0, '2026-10-08 16:35:18', '2026-10-21 16:10:31'),
(37, 'AP-20261031-037', 11, '果树', '果实膨大期', '2026-10-25', 3924.0, 'NORMAL', 8, '李国强', 'SCHEDULED', '定额充足，转调度排程', '张建民', '2026-10-19 10:30:26', 0, '2026-10-09 08:48:54', '2026-10-22 16:10:58'),
(38, 'AP-20261031-038', 12, '棉花', '拔节期', '2026-10-26', 4613.84, 'NORMAL', 9, '王秀兰', 'PENDING_SCHEDULE', NULL, NULL, NULL, 0, '2026-10-10 09:01:35', '2026-10-23 16:10:14'),
(39, 'AP-20261031-039', 13, '水稻', '孕穗期', '2026-10-27', 5359.36, 'NORMAL', 10, '赵德海', 'SCHEDULED', '定额充足，转调度排程', '张建民', '2026-10-21 10:30:17', 0, '2026-10-11 10:14:29', '2026-10-24 16:10:16'),
(40, 'AP-20261031-040', 14, '小麦', '苗期', '2026-10-28', 6160.56, 'NORMAL', 11, '孙立平', 'SCHEDULED', '定额充足，转调度排程', '张建民', '2026-10-22 10:30:14', 0, '2026-10-12 11:27:24', '2026-10-25 16:10:26'),
(41, 'AP-20261031-041', 15, '玉米', '成熟期', '2026-10-29', 7017.44, 'URGENT', 12, '陈志远', 'SCHEDULED', '定额充足，转调度排程', '张建民', '2026-10-03 10:30:59', 0, '2026-10-13 12:40:32', '2026-10-26 16:10:51'),
(42, 'AP-20261031-042', 16, '蔬菜', '结果期', '2026-10-30', 7878.0, 'NORMAL', 8, '李国强', 'SCHEDULED', '定额充足，转调度排程', '张建民', '2026-10-04 10:30:18', 0, '2026-10-14 13:53:35', '2026-10-27 16:10:08'),
(43, 'AP-20261031-043', 17, '果树', '果实膨大期', '2026-10-31', 8843.04, 'NORMAL', 9, '王秀兰', 'SCHEDULED', '定额充足，转调度排程', '张建民', '2026-10-05 10:30:59', 0, '2026-10-15 14:06:53', '2026-10-28 16:10:18'),
(44, 'AP-20261031-044', 18, '棉花', '拔节期', '2026-11-01', 1687.76, 'NORMAL', 10, '赵德海', 'PENDING_SCHEDULE', NULL, NULL, NULL, 0, '2026-10-16 15:19:30', '2026-10-29 16:10:39'),
(45, 'AP-20261031-045', 19, '水稻', '苗期', '2026-11-02', 2316.16, 'NORMAL', 11, '孙立平', 'SCHEDULED', '定额充足，转调度排程', '张建民', '2026-10-07 10:30:12', 0, '2026-10-17 16:32:15', '2026-10-19 16:10:21'),
(46, 'AP-20261031-046', 20, '小麦', '抽穗期', '2026-11-03', 1666.8, 'URGENT', 12, '陈志远', 'PENDING_SCHEDULE', NULL, NULL, NULL, 0, '2026-10-18 08:45:45', '2026-10-20 16:10:44'),
(47, 'AP-20261031-047', 21, '玉米', '拔节期', '2026-11-04', 2116.8, 'NORMAL', 8, '李国强', 'SCHEDULED', '定额充足，转调度排程', '张建民', '2026-10-09 10:30:18', 0, '2026-10-19 09:58:29', '2026-10-21 16:10:58'),
(48, 'AP-20261031-048', 22, '蔬菜', '结果期', '2026-11-05', 2658.48, 'NORMAL', 9, '王秀兰', 'REJECTED', '申请水量超出本地块年度定额余量，请核减后重新提交', '张建民', '2026-10-10 10:30:40', 0, '2026-10-20 10:11:17', '2026-10-22 16:10:58');
INSERT INTO `irrigation_plan` (`id`, `code`, `application_id`, `farmland_id`, `canal_id`, `gate_id`, `plan_start`, `plan_end`, `plan_volume`, `priority`, `status`, `dispatcher_id`, `dispatcher_name`, `reject_reason`, `remark`, `version`, `create_time`, `update_time`) VALUES
(1, 'PL-20261019-001', 1, 1, 1, 1, '2026-10-19 08:00:00', '2026-10-19 11:30:00', 816.0, 'HIGH', 'DRAFT', 2, '王海涛', NULL, NULL, 0, '2026-10-05 09:10:07', '2026-10-21 15:40:54'),
(2, 'PL-20261020-002', 2, 2, 1, 2, '2026-10-20 11:00:00', '2026-10-20 15:30:00', 1203.36, 'NORMAL', 'DRAFT', 2, '王海涛', NULL, NULL, 0, '2026-10-06 09:10:28', '2026-10-22 15:40:37'),
(3, 'PL-20261021-003', 3, 3, 1, 3, '2026-10-21 14:00:00', '2026-10-21 19:30:00', 1639.44, 'NORMAL', 'DRAFT', 2, '王海涛', NULL, NULL, 0, '2026-10-07 09:10:18', '2026-10-23 15:40:15'),
(4, 'PL-20261022-004', 4, 4, 2, 4, '2026-10-22 17:00:00', '2026-10-22 20:30:00', 2124.24, 'LOW', 'AUDITING', 2, '王海涛', NULL, NULL, 0, '2026-10-08 09:10:27', '2026-10-24 15:40:00'),
(5, 'PL-20261023-005', 5, 5, 2, 5, '2026-10-23 08:00:00', '2026-10-23 12:30:00', 2657.76, 'HIGH', 'AUDITING', 2, '王海涛', NULL, NULL, 0, '2026-10-09 09:10:01', '2026-10-25 15:40:44'),
(6, 'PL-20261024-006', 6, 6, 3, 6, '2026-10-24 11:00:00', '2026-10-24 16:30:00', 3192.0, 'NORMAL', 'AUDITING', 2, '王海涛', NULL, NULL, 0, '2026-10-10 09:10:10', '2026-10-26 15:40:39'),
(7, 'PL-20261025-007', 7, 7, 3, 7, '2026-10-25 14:00:00', '2026-10-25 17:30:00', 3820.16, 'NORMAL', 'AUDITING', 2, '王海涛', NULL, NULL, 0, '2026-10-11 09:10:09', '2026-10-27 15:40:22'),
(8, 'PL-20261026-008', 8, 8, 4, 8, '2026-10-26 17:00:00', '2026-10-26 21:30:00', 2852.6, 'LOW', 'ISSUED', 2, '王海涛', NULL, NULL, 0, '2026-10-12 09:10:14', '2026-10-28 15:40:32'),
(9, 'PL-20261027-009', 9, 9, 5, 9, '2026-10-27 08:00:00', '2026-10-27 13:30:00', 3407.68, 'HIGH', 'ISSUED', 2, '王海涛', NULL, NULL, 0, '2026-10-13 09:10:02', '2026-10-29 15:40:09'),
(10, 'PL-20261028-010', 10, 10, 6, 10, '2026-10-28 11:00:00', '2026-10-28 14:30:00', 4011.48, 'NORMAL', 'ISSUED', 2, '王海涛', NULL, NULL, 0, '2026-10-14 09:10:28', '2026-10-21 15:40:25'),
(11, 'PL-20261029-011', 11, 11, 7, 11, '2026-10-29 14:00:00', '2026-10-29 18:30:00', 4621.6, 'NORMAL', 'ISSUED', 2, '王海涛', NULL, NULL, 0, '2026-10-15 09:10:50', '2026-10-22 15:40:46'),
(12, 'PL-20261030-012', 12, 12, 8, 12, '2026-10-30 17:00:00', '2026-10-30 22:30:00', 5320.04, 'LOW', 'ISSUED', 2, '王海涛', NULL, NULL, 0, '2026-10-16 09:10:18', '2026-10-23 15:40:42'),
(13, 'PL-20261031-013', 13, 13, 1, 1, '2026-10-31 08:00:00', '2026-10-31 11:30:00', 6067.2, 'HIGH', 'ISSUED', 2, '王海涛', NULL, NULL, 0, '2026-10-17 09:10:52', '2026-10-24 15:40:20'),
(14, 'PL-20261101-014', 14, 14, 1, 2, '2026-11-01 11:00:00', '2026-11-01 15:30:00', 6863.08, 'NORMAL', 'ISSUED', 2, '王海涛', NULL, NULL, 0, '2026-10-18 09:10:53', '2026-10-25 15:40:42'),
(15, 'PL-20261102-015', 15, 15, 1, 3, '2026-11-02 14:00:00', '2026-11-02 19:30:00', 4889.2, 'NORMAL', 'ISSUED', 2, '王海涛', NULL, NULL, 0, '2026-10-19 09:10:20', '2026-10-26 15:40:22'),
(16, 'PL-20261103-016', 16, 16, 2, 4, '2026-11-03 17:00:00', '2026-11-03 20:30:00', 5575.2, 'LOW', 'ISSUED', 2, '王海涛', NULL, NULL, 0, '2026-10-20 09:10:20', '2026-10-27 15:40:40'),
(17, 'PL-20261104-017', 17, 17, 2, 5, '2026-11-04 08:00:00', '2026-11-04 12:30:00', 6343.92, 'HIGH', 'EXECUTING', 2, '王海涛', NULL, NULL, 0, '2026-10-21 09:10:44', '2026-10-28 15:40:53'),
(18, 'PL-20261105-018', 18, 18, 3, 6, '2026-11-05 11:00:00', '2026-11-05 16:30:00', 1225.36, 'NORMAL', 'EXECUTING', 2, '王海涛', NULL, NULL, 0, '2026-10-22 09:10:47', '2026-10-29 15:40:23'),
(19, 'PL-20261106-019', 19, 19, 3, 7, '2026-11-06 14:00:00', '2026-11-06 17:30:00', 1699.52, 'NORMAL', 'EXECUTING', 2, '王海涛', NULL, NULL, 0, '2026-10-23 09:10:53', '2026-10-21 15:40:59'),
(20, 'PL-20261107-020', 20, 20, 4, 8, '2026-11-07 17:00:00', '2026-11-07 21:30:00', 2222.4, 'LOW', 'EXECUTING', 2, '王海涛', NULL, NULL, 0, '2026-10-24 09:10:39', '2026-10-22 15:40:23'),
(21, 'PL-20261019-021', 21, 21, 5, 9, '2026-10-19 08:00:00', '2026-10-19 13:30:00', 2743.2, 'HIGH', 'EXECUTING', 2, '王海涛', NULL, NULL, 0, '2026-10-25 09:10:06', '2026-10-23 15:40:55'),
(22, 'PL-20261020-022', 22, 22, 6, 10, '2026-10-20 11:00:00', '2026-10-20 14:30:00', 2131.8, 'NORMAL', 'EXECUTING', 2, '王海涛', NULL, NULL, 0, '2026-10-26 09:10:22', '2026-10-24 15:40:54'),
(23, 'PL-20261021-023', 23, 23, 7, 11, '2026-10-21 14:00:00', '2026-10-21 18:30:00', 2627.52, 'NORMAL', 'CONFIRMING', 2, '王海涛', NULL, NULL, 0, '2026-10-27 09:10:10', '2026-10-25 15:40:27'),
(24, 'PL-20261022-024', 24, 24, 8, 12, '2026-10-22 17:00:00', '2026-10-22 22:30:00', 3171.96, 'LOW', 'CONFIRMING', 2, '王海涛', NULL, NULL, 0, '2026-10-28 09:10:00', '2026-10-26 15:40:41'),
(25, 'PL-20261023-025', 25, 25, 1, 1, '2026-10-23 08:00:00', '2026-10-23 11:30:00', 3765.12, 'HIGH', 'CONFIRMING', 2, '王海涛', NULL, NULL, 0, '2026-10-05 09:10:38', '2026-10-27 15:40:18'),
(26, 'PL-20261024-026', 26, 26, 1, 2, '2026-10-24 11:00:00', '2026-10-24 15:30:00', 4361.8, 'NORMAL', 'CONFIRMING', 2, '王海涛', NULL, NULL, 0, '2026-10-06 09:10:30', '2026-10-28 15:40:44'),
(27, 'PL-20261025-027', 27, 1, 1, 3, '2026-10-25 14:00:00', '2026-10-25 19:30:00', 1152.0, 'NORMAL', 'CONFIRMING', 2, '王海涛', NULL, NULL, 0, '2026-10-07 09:10:44', '2026-10-29 15:40:00'),
(28, 'PL-20261026-028', 28, 2, 2, 4, '2026-10-26 17:00:00', '2026-10-26 20:30:00', 1661.16, 'LOW', 'ARCHIVED', 2, '王海涛', NULL, NULL, 0, '2026-10-08 09:10:03', '2026-10-21 15:40:32'),
(29, 'PL-20261027-029', 29, 3, 2, 5, '2026-10-27 08:00:00', '2026-10-27 12:30:00', 1407.6, 'HIGH', 'ARCHIVED', 2, '王海涛', NULL, NULL, 0, '2026-10-09 09:10:02', '2026-10-22 15:40:46'),
(30, 'PL-20261028-030', 30, 4, 3, 6, '2026-10-28 11:00:00', '2026-10-28 16:30:00', 1843.68, 'NORMAL', 'ARCHIVED', 2, '王海涛', NULL, NULL, 0, '2026-10-10 09:10:49', '2026-10-23 15:40:49'),
(31, 'PL-20261029-031', 31, 5, 3, 7, '2026-10-29 14:00:00', '2026-10-29 17:30:00', 2328.48, 'NORMAL', 'ARCHIVED', 2, '王海涛', NULL, NULL, 0, '2026-10-11 09:10:39', '2026-10-24 15:40:01'),
(32, 'PL-20261030-032', 32, 6, 4, 8, '2026-10-30 17:00:00', '2026-10-30 21:30:00', 2819.6, 'LOW', 'ARCHIVED', 2, '王海涛', NULL, NULL, 0, '2026-10-12 09:10:15', '2026-10-25 15:40:56'),
(33, 'PL-20261031-033', 33, 7, 5, 9, '2026-10-31 08:00:00', '2026-10-31 13:30:00', 3399.04, 'HIGH', 'CONFLICT', 2, '王海涛', NULL, '同一闸口重叠时段需复核', 0, '2026-10-13 09:10:08', '2026-10-26 15:40:43'),
(34, 'PL-20261101-034', 34, 8, 6, 10, '2026-11-01 11:00:00', '2026-11-01 14:30:00', 4027.2, 'NORMAL', 'CONFLICT', 2, '王海涛', NULL, '同一闸口重叠时段需复核', 0, '2026-10-14 09:10:49', '2026-10-27 15:40:24');
INSERT INTO `irrigation_task` (`id`, `code`, `plan_id`, `farmland_id`, `operator_id`, `operator_name`, `plan_volume`, `start_reading`, `end_reading`, `actual_volume`, `start_time`, `end_time`, `status`, `photo`, `receiver_name`, `confirm_time`, `interrupt_reason`, `version`, `create_time`, `update_time`) VALUES
(1, 'TK-20261031-001', 1, 1, 4, '刘卫东', 816.0, 12000.0, 12701.76, 701.76, '2026-10-19 08:00:00', '2026-10-19 10:40:00', 'FINISHED', '/uploads/seed/task/01.jpg', '李国强', '2026-10-19 10:40:00', NULL, 0, '2026-10-11 08:20:36', '2026-10-25 17:25:03'),
(2, 'TK-20261031-002', 2, 2, 5, '陈立新', 1203.36, 12137.4, 13232.46, 1095.06, '2026-10-20 11:00:00', '2026-10-20 14:40:00', 'FINISHED', '/uploads/seed/task/04.jpg', '王秀兰', '2026-10-20 14:40:00', NULL, 0, '2026-10-12 08:20:38', '2026-10-26 17:25:34'),
(3, 'TK-20261031-003', 3, 3, 6, '杨春生', 1639.44, 12274.8, 13848.66, 1573.86, '2026-10-21 14:00:00', '2026-10-21 18:40:00', 'FINISHED', '/uploads/seed/task/03.jpg', '赵德海', '2026-10-21 18:40:00', NULL, 0, '2026-10-13 08:20:16', '2026-10-27 17:25:39'),
(4, 'TK-20261031-004', 4, 4, 7, '郭建军', 2124.24, 12412.2, 14557.68, 2145.48, '2026-10-22 17:00:00', '2026-10-22 19:40:00', 'FINISHED', '/uploads/seed/task/02.jpg', '孙立平', '2026-10-22 19:40:00', NULL, 0, '2026-10-14 08:20:57', '2026-10-28 17:25:13'),
(5, 'TK-20261031-005', 5, 5, 4, '刘卫东', 2657.76, 12549.6, 15366.83, 2817.23, '2026-10-23 08:00:00', '2026-10-23 11:40:00', 'FINISHED', '/uploads/seed/task/01.jpg', '陈志远', '2026-10-23 11:40:00', NULL, 0, '2026-10-15 08:20:17', '2026-10-29 17:25:43'),
(6, 'TK-20261031-006', 6, 6, 5, '陈立新', 3192.0, 12687.0, 16230.12, 3543.12, '2026-10-24 11:00:00', '2026-10-24 15:40:00', 'FINISHED', '/uploads/seed/task/04.jpg', '李国强', '2026-10-24 15:40:00', NULL, 0, '2026-10-16 08:20:58', '2026-10-25 17:25:39'),
(7, 'TK-20261031-007', 7, 7, 6, '杨春生', 3820.16, 12824.4, 16109.74, 3285.34, '2026-10-25 14:00:00', '2026-10-25 16:40:00', 'FINISHED', '/uploads/seed/task/03.jpg', '王秀兰', '2026-10-25 16:40:00', NULL, 0, '2026-10-17 08:20:59', '2026-10-26 17:25:22'),
(8, 'TK-20261031-008', 8, 8, 7, '郭建军', 2852.6, 12961.8, 15557.67, 2595.87, '2026-10-26 17:00:00', '2026-10-26 20:40:00', 'FINISHED', '/uploads/seed/task/02.jpg', '赵德海', '2026-10-26 20:40:00', NULL, 0, '2026-10-18 08:20:00', '2026-10-27 17:25:03'),
(9, 'TK-20261031-009', 9, 9, 4, '刘卫东', 3407.68, 13099.2, 16370.57, 3271.37, '2026-10-27 08:00:00', '2026-10-27 12:40:00', 'FINISHED', '/uploads/seed/task/01.jpg', '孙立平', '2026-10-27 12:40:00', NULL, 0, '2026-10-19 08:20:18', '2026-10-28 17:25:43'),
(10, 'TK-20261031-010', 10, 10, 5, '陈立新', 4011.48, 13236.6, 17288.19, 4051.59, '2026-10-28 11:00:00', '2026-10-28 13:40:00', 'FINISHED', '/uploads/seed/task/04.jpg', '陈志远', '2026-10-28 13:40:00', NULL, 0, '2026-10-20 08:20:46', '2026-10-29 17:25:11'),
(11, 'TK-20261031-011', 11, 11, 6, '杨春生', 4621.6, 13374.0, 18272.9, 4898.9, '2026-10-29 14:00:00', '2026-10-29 17:40:00', 'FINISHED', '/uploads/seed/task/03.jpg', '李国强', '2026-10-29 17:40:00', NULL, 0, '2026-10-21 08:20:03', '2026-10-25 17:25:56'),
(12, 'TK-20261031-012', 12, 12, 7, '郭建军', 5320.04, 13511.4, 19416.64, 5905.24, '2026-10-30 17:00:00', '2026-10-30 21:40:00', 'FINISHED', '/uploads/seed/task/02.jpg', '王秀兰', '2026-10-30 21:40:00', NULL, 0, '2026-10-22 08:20:31', '2026-10-26 17:25:21'),
(13, 'TK-20261031-013', 13, 13, 4, '刘卫东', 6067.2, 13648.8, 18866.59, 5217.79, '2026-10-31 08:00:00', '2026-10-31 10:40:00', 'FINISHED', '/uploads/seed/task/01.jpg', '赵德海', '2026-10-31 10:40:00', NULL, 0, '2026-10-23 08:20:33', '2026-10-27 17:25:14'),
(14, 'TK-20261031-014', 14, 14, 5, '陈立新', 6863.08, 13786.2, 20031.6, 6245.4, '2026-11-01 11:00:00', '2026-11-01 14:40:00', 'FINISHED', '/uploads/seed/task/04.jpg', '孙立平', '2026-11-01 14:40:00', NULL, 0, '2026-10-24 08:20:08', '2026-10-28 17:25:20'),
(15, 'TK-20261031-015', 15, 15, 6, '杨春生', 4889.2, 13923.6, 18617.23, 4693.63, '2026-11-02 14:00:00', '2026-11-02 18:40:00', 'FINISHED', '/uploads/seed/task/03.jpg', '陈志远', '2026-11-02 18:40:00', NULL, 0, '2026-10-25 08:20:53', '2026-10-29 17:25:43'),
(16, 'TK-20261031-016', 16, 16, 7, '郭建军', 5575.2, 14061.0, 19691.95, 5630.95, '2026-11-03 17:00:00', '2026-11-03 19:40:00', 'FINISHED', '/uploads/seed/task/02.jpg', '李国强', '2026-11-03 19:40:00', NULL, 0, '2026-10-26 08:20:33', '2026-10-25 17:25:37'),
(17, 'TK-20261031-017', 17, 17, 4, '刘卫东', 6343.92, 14198.4, 20922.96, 6724.56, '2026-11-04 08:00:00', '2026-11-04 11:40:00', 'FINISHED', '/uploads/seed/task/01.jpg', '王秀兰', '2026-11-04 11:40:00', NULL, 0, '2026-10-27 08:20:35', '2026-10-26 17:25:07'),
(18, 'TK-20261031-018', 18, 18, 5, '陈立新', 1225.36, 14335.8, 15695.95, 1360.15, '2026-11-05 11:00:00', '2026-11-05 15:40:00', 'FINISHED', '/uploads/seed/task/04.jpg', '赵德海', '2026-11-05 15:40:00', NULL, 0, '2026-10-28 08:20:09', '2026-10-27 17:25:19'),
(19, 'TK-20261031-019', 19, 19, 6, '杨春生', 1699.52, 14473.2, 15934.79, 1461.59, '2026-11-06 14:00:00', '2026-11-06 16:40:00', 'FINISHED', '/uploads/seed/task/03.jpg', '孙立平', '2026-11-06 16:40:00', NULL, 0, '2026-10-11 08:20:07', '2026-10-28 17:25:36'),
(20, 'TK-20261031-020', 20, 20, 7, '郭建军', 2222.4, 14610.6, 16632.98, 2022.38, '2026-11-07 17:00:00', '2026-11-07 20:40:00', 'FINISHED', '/uploads/seed/task/02.jpg', '陈志远', '2026-11-07 20:40:00', NULL, 0, '2026-10-12 08:20:49', '2026-10-29 17:25:22'),
(21, 'TK-20261031-021', 21, 21, 4, '刘卫东', 2743.2, 14748.0, 17381.47, 2633.47, '2026-10-19 08:00:00', '2026-10-19 12:40:00', 'FINISHED', '/uploads/seed/task/01.jpg', '李国强', '2026-10-19 12:40:00', NULL, 0, '2026-10-13 08:20:17', '2026-10-25 17:25:07'),
(22, 'TK-20261031-022', 22, 22, 5, '陈立新', 2131.8, 14885.4, 17038.52, 2153.12, '2026-10-20 11:00:00', '2026-10-20 13:40:00', 'FINISHED', '/uploads/seed/task/04.jpg', '王秀兰', '2026-10-20 13:40:00', NULL, 0, '2026-10-14 08:20:44', '2026-10-26 17:25:38'),
(23, 'TK-20261031-023', 23, 23, 6, '杨春生', 2627.52, 15022.8, NULL, NULL, '2026-10-21 14:00:00', NULL, 'RUNNING', '/uploads/seed/task/03.jpg', NULL, NULL, NULL, 0, '2026-10-15 08:20:16', '2026-10-27 17:25:28'),
(24, 'TK-20261031-024', 24, 24, 7, '郭建军', 3171.96, 15160.2, NULL, NULL, '2026-10-22 17:00:00', NULL, 'RUNNING', '/uploads/seed/task/02.jpg', NULL, NULL, NULL, 0, '2026-10-16 08:20:37', '2026-10-28 17:25:30'),
(25, 'TK-20261031-025', 25, 25, 4, '刘卫东', 3765.12, 15297.6, NULL, NULL, '2026-10-23 08:00:00', NULL, 'RUNNING', '/uploads/seed/task/01.jpg', NULL, NULL, NULL, 0, '2026-10-17 08:20:05', '2026-10-29 17:25:31'),
(26, 'TK-20261031-026', 26, 26, 5, '陈立新', 4361.8, 15435.0, NULL, NULL, '2026-10-24 11:00:00', NULL, 'RUNNING', '/uploads/seed/task/04.jpg', NULL, NULL, NULL, 0, '2026-10-18 08:20:37', '2026-10-25 17:25:54'),
(27, 'TK-20261031-027', 27, 1, 6, '杨春生', 1152.0, 15572.4, NULL, NULL, '2026-10-25 14:00:00', NULL, 'RUNNING', '/uploads/seed/task/03.jpg', NULL, NULL, NULL, 0, '2026-10-19 08:20:52', '2026-10-26 17:25:46'),
(28, 'TK-20261031-028', 28, 2, 7, '郭建军', 1661.16, NULL, NULL, NULL, NULL, NULL, 'PENDING', NULL, NULL, NULL, NULL, 0, '2026-10-20 08:20:00', '2026-10-27 17:25:38'),
(29, 'TK-20261031-029', 29, 3, 4, '刘卫东', 1407.6, NULL, NULL, NULL, NULL, NULL, 'PENDING', NULL, NULL, NULL, NULL, 0, '2026-10-21 08:20:41', '2026-10-28 17:25:18'),
(30, 'TK-20261031-030', 30, 4, 5, '陈立新', 1843.68, NULL, NULL, NULL, NULL, NULL, 'PENDING', NULL, NULL, NULL, NULL, 0, '2026-10-22 08:20:14', '2026-10-29 17:25:38'),
(31, 'TK-20261031-031', 31, 5, 6, '杨春生', 2328.48, NULL, NULL, NULL, NULL, NULL, 'PENDING', NULL, NULL, NULL, NULL, 0, '2026-10-23 08:20:43', '2026-10-25 17:25:42'),
(32, 'TK-20261031-032', 32, 6, 7, '郭建军', 2819.6, NULL, NULL, NULL, NULL, NULL, 'PENDING', NULL, NULL, NULL, NULL, 0, '2026-10-24 08:20:44', '2026-10-26 17:25:25'),
(33, 'TK-20261031-033', 33, 7, 4, '刘卫东', 3399.04, NULL, NULL, NULL, NULL, NULL, 'PENDING', NULL, NULL, NULL, NULL, 0, '2026-10-25 08:20:14', '2026-10-27 17:25:17'),
(34, 'TK-20261031-034', 34, 8, 5, '陈立新', 4027.2, NULL, NULL, NULL, NULL, NULL, 'PENDING', NULL, NULL, NULL, NULL, 0, '2026-10-26 08:20:59', '2026-10-28 17:25:43'),
(35, 'TK-20261031-035', 1, 1, 6, '杨春生', 816.0, NULL, NULL, NULL, NULL, NULL, 'PENDING', NULL, NULL, NULL, NULL, 0, '2026-10-27 08:20:27', '2026-10-29 17:25:22'),
(36, 'TK-20261031-036', 2, 2, 7, '郭建军', 1203.36, 16809.0, 18144.73, 1335.73, '2026-10-20 11:00:00', '2026-10-20 15:40:00', 'INTERRUPTED', '/uploads/seed/task/02.jpg', '王秀兰', '2026-10-20 15:40:00', '水源可用量不足临时中断', 0, '2026-10-28 08:20:11', '2026-10-25 17:25:52'),
(37, 'TK-20261031-037', 3, 3, 4, '刘卫东', 1639.44, 16946.4, 18356.32, 1409.92, '2026-10-21 14:00:00', '2026-10-21 16:40:00', 'INTERRUPTED', '/uploads/seed/task/01.jpg', '赵德海', '2026-10-21 16:40:00', '渠道堵塞导致末端无水', 0, '2026-10-11 08:20:39', '2026-10-26 17:25:38'),
(38, 'TK-20261031-038', 4, 4, 5, '陈立新', 2124.24, 17083.8, 19016.86, 1933.06, '2026-10-22 17:00:00', '2026-10-22 20:40:00', 'INTERRUPTED', '/uploads/seed/task/04.jpg', '孙立平', '2026-10-22 20:40:00', '渠段发现漏水点紧急停水', 0, '2026-10-12 08:20:22', '2026-10-27 17:25:13'),
(39, 'TK-20261031-039', 5, 5, 6, '杨春生', 2657.76, 17221.2, 19772.65, 2551.45, '2026-10-23 08:00:00', '2026-10-23 12:40:00', 'INTERRUPTED', '/uploads/seed/task/03.jpg', '陈志远', '2026-10-23 12:40:00', '闸门启闭机故障无法调流', 0, '2026-10-13 08:20:10', '2026-10-28 17:25:06'),
(40, 'TK-20261031-040', 6, 6, 7, '郭建军', 3192.0, 17358.6, 20582.52, 3223.92, '2026-10-24 11:00:00', '2026-10-24 13:40:00', 'INTERRUPTED', '/uploads/seed/task/02.jpg', '李国强', '2026-10-24 13:40:00', '水源可用量不足临时中断', 0, '2026-10-14 08:20:58', '2026-10-29 17:25:44');
INSERT INTO `water_meter` (`id`, `code`, `name`, `gate_id`, `farmland_id`, `init_reading`, `current_reading`, `install_date`, `photo`, `status`) VALUES
(1, 'WM-001', '北干渠一号地计量表', NULL, 1, 12000.0, 12701.76, '2025-11-20', '/uploads/seed/meter/01.jpg', 'NORMAL'),
(2, 'WM-002', '东支渠二号地计量表', NULL, 2, 12137.4, 13232.46, '2025-11-20', '/uploads/seed/meter/02.jpg', 'NORMAL'),
(3, 'WM-003', '南干渠三号地计量表', NULL, 3, 12274.8, 13848.66, '2025-11-20', '/uploads/seed/meter/01.jpg', 'NORMAL'),
(4, 'WM-004', '西支渠五号地计量表', NULL, 4, 12412.2, 14557.68, '2025-11-20', '/uploads/seed/meter/02.jpg', 'NORMAL'),
(5, 'WM-005', '北干渠七号地计量表', NULL, 5, 12549.6, 15366.83, '2025-11-20', '/uploads/seed/meter/01.jpg', 'NORMAL'),
(6, 'WM-006', '东支渠九号地计量表', NULL, 6, 12687.0, 16230.12, '2025-11-20', '/uploads/seed/meter/02.jpg', 'NORMAL'),
(7, 'WM-007', '南干渠十号地计量表', NULL, 7, 12824.4, 16109.74, '2025-11-20', '/uploads/seed/meter/01.jpg', 'NORMAL'),
(8, 'WM-008', '西支渠二号地计量表', NULL, 8, 12961.8, 15557.67, '2025-11-20', '/uploads/seed/meter/02.jpg', 'NORMAL'),
(9, 'WM-009', '北干渠三号地计量表', NULL, 9, 13099.2, 16370.57, '2025-11-20', '/uploads/seed/meter/01.jpg', 'NORMAL'),
(10, 'WM-010', '东支渠三号地计量表', NULL, 10, 13236.6, 17288.19, '2025-11-20', '/uploads/seed/meter/02.jpg', 'NORMAL'),
(11, 'WM-011', '南干渠三号地计量表', NULL, 11, 13374.0, 18272.9, '2025-11-20', '/uploads/seed/meter/01.jpg', 'NORMAL'),
(12, 'WM-012', '西支渠三号地计量表', NULL, 12, 13511.4, 19416.64, '2025-11-20', '/uploads/seed/meter/02.jpg', 'NORMAL'),
(13, 'WM-013', '北干渠五号地计量表', NULL, 13, 13648.8, 18866.59, '2025-11-20', '/uploads/seed/meter/01.jpg', 'NORMAL'),
(14, 'WM-014', '东支渠五号地计量表', NULL, 14, 13786.2, 20031.6, '2025-11-20', '/uploads/seed/meter/02.jpg', 'NORMAL'),
(15, 'WM-015', '南干渠五号地计量表', NULL, 15, 13923.6, 18617.23, '2025-11-20', '/uploads/seed/meter/01.jpg', 'NORMAL'),
(16, 'WM-016', '西支渠五号地计量表', NULL, 16, 14061.0, 19691.95, '2025-11-20', '/uploads/seed/meter/02.jpg', 'NORMAL'),
(17, 'WM-017', '北干渠七号地计量表', NULL, 17, 14198.4, 20922.96, '2025-11-20', '/uploads/seed/meter/01.jpg', 'NORMAL'),
(18, 'WM-018', '东支渠七号地计量表', NULL, 18, 14335.8, 15695.95, '2025-11-20', '/uploads/seed/meter/02.jpg', 'NORMAL'),
(19, 'WM-019', '南干渠七号地计量表', NULL, 19, 14473.2, 15934.79, '2025-11-20', '/uploads/seed/meter/01.jpg', 'NORMAL'),
(20, 'WM-020', '西支渠七号地计量表', NULL, 20, 14610.6, 16632.98, '2025-11-20', '/uploads/seed/meter/02.jpg', 'NORMAL'),
(21, 'WM-021', '北干渠九号地计量表', NULL, 21, 14748.0, 17381.47, '2025-11-20', '/uploads/seed/meter/01.jpg', 'NORMAL'),
(22, 'WM-022', '东支渠九号地计量表', NULL, 22, 14885.4, 17038.52, '2025-11-20', '/uploads/seed/meter/02.jpg', 'NORMAL'),
(23, 'WM-023', '东支渠二号地计量表', NULL, 2, 16809.0, 18144.73, '2025-11-20', '/uploads/seed/meter/02.jpg', 'NORMAL'),
(24, 'WM-024', '南干渠三号地计量表', NULL, 3, 16946.4, 18356.32, '2025-11-20', '/uploads/seed/meter/01.jpg', 'NORMAL'),
(25, 'WM-025', '西支渠五号地计量表', NULL, 4, 17083.8, 19016.86, '2025-11-20', '/uploads/seed/meter/02.jpg', 'NORMAL'),
(26, 'WM-026', '北干渠七号地计量表', NULL, 5, 17221.2, 19772.65, '2025-11-20', '/uploads/seed/meter/01.jpg', 'NORMAL'),
(27, 'WM-027', '东支渠九号地计量表', NULL, 6, 17358.6, 20582.52, '2025-11-20', '/uploads/seed/meter/02.jpg', 'NORMAL');
INSERT INTO `water_meter_record` (`id`, `task_id`, `meter_id`, `start_reading`, `end_reading`, `volume`, `record_time`, `recorder_id`, `recorder_name`, `photo`, `remark`) VALUES
(1, 1, 1, 12000.0, 12701.76, 701.76, '2026-10-19 10:40:00', 4, '刘卫东', '/uploads/seed/meter/01.jpg', '现场抄表，表盘清晰'),
(2, 2, 2, 12137.4, 13232.46, 1095.06, '2026-10-20 14:40:00', 5, '陈立新', '/uploads/seed/meter/02.jpg', '现场抄表，表盘清晰'),
(3, 3, 3, 12274.8, 13848.66, 1573.86, '2026-10-21 18:40:00', 6, '杨春生', '/uploads/seed/meter/01.jpg', '现场抄表，表盘清晰'),
(4, 4, 4, 12412.2, 14557.68, 2145.48, '2026-10-22 19:40:00', 7, '郭建军', '/uploads/seed/meter/02.jpg', '现场抄表，表盘清晰'),
(5, 5, 5, 12549.6, 15366.83, 2817.23, '2026-10-23 11:40:00', 4, '刘卫东', '/uploads/seed/meter/01.jpg', '现场抄表，表盘清晰'),
(6, 6, 6, 12687.0, 16230.12, 3543.12, '2026-10-24 15:40:00', 5, '陈立新', '/uploads/seed/meter/02.jpg', '现场抄表，表盘清晰'),
(7, 7, 7, 12824.4, 16109.74, 3285.34, '2026-10-25 16:40:00', 6, '杨春生', '/uploads/seed/meter/01.jpg', '现场抄表，表盘清晰'),
(8, 8, 8, 12961.8, 15557.67, 2595.87, '2026-10-26 20:40:00', 7, '郭建军', '/uploads/seed/meter/02.jpg', '现场抄表，表盘清晰'),
(9, 9, 9, 13099.2, 16370.57, 3271.37, '2026-10-27 12:40:00', 4, '刘卫东', '/uploads/seed/meter/01.jpg', '现场抄表，表盘清晰'),
(10, 10, 10, 13236.6, 17288.19, 4051.59, '2026-10-28 13:40:00', 5, '陈立新', '/uploads/seed/meter/02.jpg', '现场抄表，表盘清晰'),
(11, 11, 11, 13374.0, 18272.9, 4898.9, '2026-10-29 17:40:00', 6, '杨春生', '/uploads/seed/meter/01.jpg', '现场抄表，表盘清晰'),
(12, 12, 12, 13511.4, 19416.64, 5905.24, '2026-10-30 21:40:00', 7, '郭建军', '/uploads/seed/meter/02.jpg', '现场抄表，表盘清晰'),
(13, 13, 13, 13648.8, 18866.59, 5217.79, '2026-10-31 10:40:00', 4, '刘卫东', '/uploads/seed/meter/01.jpg', '现场抄表，表盘清晰'),
(14, 14, 14, 13786.2, 20031.6, 6245.4, '2026-11-01 14:40:00', 5, '陈立新', '/uploads/seed/meter/02.jpg', '现场抄表，表盘清晰'),
(15, 15, 15, 13923.6, 18617.23, 4693.63, '2026-11-02 18:40:00', 6, '杨春生', '/uploads/seed/meter/01.jpg', '现场抄表，表盘清晰'),
(16, 16, 16, 14061.0, 19691.95, 5630.95, '2026-11-03 19:40:00', 7, '郭建军', '/uploads/seed/meter/02.jpg', '现场抄表，表盘清晰'),
(17, 17, 17, 14198.4, 20922.96, 6724.56, '2026-11-04 11:40:00', 4, '刘卫东', '/uploads/seed/meter/01.jpg', '现场抄表，表盘清晰'),
(18, 18, 18, 14335.8, 15695.95, 1360.15, '2026-11-05 15:40:00', 5, '陈立新', '/uploads/seed/meter/02.jpg', '现场抄表，表盘清晰'),
(19, 19, 19, 14473.2, 15934.79, 1461.59, '2026-11-06 16:40:00', 6, '杨春生', '/uploads/seed/meter/01.jpg', '现场抄表，表盘清晰'),
(20, 20, 20, 14610.6, 16632.98, 2022.38, '2026-11-07 20:40:00', 7, '郭建军', '/uploads/seed/meter/02.jpg', '现场抄表，表盘清晰'),
(21, 21, 21, 14748.0, 17381.47, 2633.47, '2026-10-19 12:40:00', 4, '刘卫东', '/uploads/seed/meter/01.jpg', '现场抄表，表盘清晰'),
(22, 22, 22, 14885.4, 17038.52, 2153.12, '2026-10-20 13:40:00', 5, '陈立新', '/uploads/seed/meter/02.jpg', '现场抄表，表盘清晰'),
(36, 36, 23, 16809.0, 18144.73, 1335.73, '2026-10-20 15:40:00', 7, '郭建军', '/uploads/seed/meter/02.jpg', '现场抄表，表盘清晰'),
(37, 37, 24, 16946.4, 18356.32, 1409.92, '2026-10-21 16:40:00', 4, '刘卫东', '/uploads/seed/meter/01.jpg', '现场抄表，表盘清晰'),
(38, 38, 25, 17083.8, 19016.86, 1933.06, '2026-10-22 20:40:00', 5, '陈立新', '/uploads/seed/meter/02.jpg', '现场抄表，表盘清晰'),
(39, 39, 26, 17221.2, 19772.65, 2551.45, '2026-10-23 12:40:00', 6, '杨春生', '/uploads/seed/meter/01.jpg', '现场抄表，表盘清晰'),
(40, 40, 27, 17358.6, 20582.52, 3223.92, '2026-10-24 13:40:00', 7, '郭建军', '/uploads/seed/meter/02.jpg', '现场抄表，表盘清晰');
INSERT INTO `fee_ledger` (`id`, `code`, `task_id`, `farmland_id`, `farmer_name`, `actual_volume`, `base_volume`, `excess_volume`, `base_price`, `excess_price`, `amount`, `bill_month`, `status`, `pay_time`, `create_time`) VALUES
(1, 'FE-202610-001', 1, 1, '李国强', 701.76, 576.0, 125.76, 0.42, 0.55, 311.09, '2026-10', 'UNPAID', NULL, '2026-10-19 18:00:45'),
(2, 'FE-202610-002', 2, 2, '王秀兰', 1095.06, 784.8, 310.26, 0.42, 0.55, 500.26, '2026-10', 'PAID', '2026-10-27 11:00:03', '2026-10-20 18:00:42'),
(3, 'FE-202610-003', 3, 3, '赵德海', 1573.86, 993.6, 580.26, 0.42, 0.55, 736.46, '2026-10', 'PAID', '2026-10-26 11:00:53', '2026-10-21 18:00:23'),
(4, 'FE-202610-004', 4, 4, '孙立平', 2145.48, 1202.4, 943.08, 0.42, 0.55, 1023.7, '2026-10', 'PAID', '2026-10-25 11:00:18', '2026-10-22 18:00:32'),
(5, 'FE-202610-005', 5, 5, '陈志远', 2817.23, 1411.2, 1406.03, 0.42, 0.55, 1366.02, '2026-10', 'UNPAID', NULL, '2026-10-23 18:00:40'),
(6, 'FE-202610-006', 6, 6, '李国强', 3543.12, 1596.0, 1947.12, 0.42, 0.55, 1741.24, '2026-10', 'UNPAID', NULL, '2026-10-24 18:00:54'),
(7, 'FE-202610-007', 7, 7, '王秀兰', 3285.34, 1804.8, 1480.54, 0.42, 0.55, 1572.31, '2026-10', 'PAID', '2026-10-22 11:00:54', '2026-10-25 18:00:03'),
(8, 'FE-202610-008', 8, 8, '赵德海', 2595.87, 2013.6, 582.27, 0.42, 0.55, 1165.96, '2026-10', 'WAIVED', NULL, '2026-10-26 18:00:55'),
(9, 'FE-202610-009', 9, 9, '孙立平', 3271.37, 2222.4, 1048.97, 0.42, 0.55, 1510.34, '2026-10', 'PAID', '2026-10-20 11:00:50', '2026-10-27 18:00:50'),
(10, 'FE-202610-010', 10, 10, '陈志远', 4051.59, 2431.2, 1620.39, 0.42, 0.55, 1912.32, '2026-10', 'UNPAID', NULL, '2026-10-28 18:00:35'),
(11, 'FE-202610-011', 11, 11, '李国强', 4898.9, 2616.0, 2282.9, 0.42, 0.55, 2354.32, '2026-10', 'UNPAID', NULL, '2026-10-19 18:00:48'),
(12, 'FE-202610-012', 12, 12, '王秀兰', 5905.24, 2824.8, 3080.44, 0.42, 0.55, 2880.66, '2026-10', 'PAID', '2026-10-27 11:00:19', '2026-10-20 18:00:50'),
(13, 'FE-202610-013', 13, 13, '赵德海', 5217.79, 3033.6, 2184.19, 0.42, 0.55, 2475.42, '2026-10', 'PAID', '2026-10-26 11:00:21', '2026-10-21 18:00:47'),
(14, 'FE-202611-014', 14, 14, '孙立平', 6245.4, 3242.4, 3003.0, 0.42, 0.55, 3013.46, '2026-11', 'PAID', '2026-10-25 11:00:44', '2026-10-22 18:00:36'),
(15, 'FE-202611-015', 15, 15, '陈志远', 4693.63, 3451.2, 1242.43, 0.42, 0.55, 2132.84, '2026-11', 'UNPAID', NULL, '2026-10-23 18:00:49'),
(16, 'FE-202611-016', 16, 16, '李国强', 5630.95, 3636.0, 1994.95, 0.42, 0.55, 2624.34, '2026-11', 'UNPAID', NULL, '2026-10-24 18:00:04'),
(17, 'FE-202611-017', 17, 17, '王秀兰', 6724.56, 3844.8, 2879.76, 0.42, 0.55, 3198.68, '2026-11', 'PAID', '2026-10-22 11:00:45', '2026-10-25 18:00:25'),
(18, 'FE-202611-018', 18, 18, '赵德海', 1360.15, 693.6, 666.55, 0.42, 0.55, 657.91, '2026-11', 'PAID', '2026-10-21 11:00:25', '2026-10-26 18:00:16'),
(19, 'FE-202611-019', 19, 19, '孙立平', 1461.59, 902.4, 559.19, 0.42, 0.55, 686.56, '2026-11', 'PAID', '2026-10-20 11:00:47', '2026-10-27 18:00:57'),
(20, 'FE-202611-020', 20, 20, '陈志远', 2022.38, 1111.2, 911.18, 0.42, 0.55, 967.85, '2026-11', 'UNPAID', NULL, '2026-10-28 18:00:08'),
(21, 'FE-202610-021', 21, 21, '李国强', 2633.47, 1296.0, 1337.47, 0.42, 0.55, 1279.93, '2026-10', 'UNPAID', NULL, '2026-10-19 18:00:24'),
(22, 'FE-202610-022', 22, 22, '王秀兰', 2153.12, 1504.8, 648.32, 0.42, 0.55, 988.59, '2026-10', 'PAID', '2026-10-27 11:00:10', '2026-10-20 18:00:56');
INSERT INTO `exception_record` (`id`, `task_id`, `exc_type`, `description`, `loss_volume`, `handle_result`, `photo`, `reporter_id`, `reporter_name`, `status`, `create_time`) VALUES
(1, 1, 'BLOCK', '渠段内有秸秆淤积，过流断面缩小约三分之一', 60.0, '已组织人工清淤并恢复通水', '/uploads/seed/task/03.jpg', 4, '刘卫东', 'HANDLED', '2026-10-17 13:20:07'),
(2, 6, 'LEAK', '支渠衬砌板接缝渗漏，沿渠肩出现明显湿痕', 107.5, NULL, '/uploads/seed/task/02.jpg', 5, '陈立新', 'OPEN', '2026-10-18 13:20:27'),
(3, 11, 'FAULT', '闸门启闭机电机烧毁，无法电动调流', 155.0, '已组织人工清淤并恢复通水', '/uploads/seed/task/01.jpg', 6, '杨春生', 'HANDLED', '2026-10-19 13:20:24'),
(4, 16, 'SHORT', '水源可用量低于计划值，末端地块供水中断', 202.5, NULL, '/uploads/seed/task/04.jpg', 7, '郭建军', 'OPEN', '2026-10-20 13:20:00'),
(5, 21, 'BLOCK', '渠段内有秸秆淤积，过流断面缩小约三分之一', 250.0, '已组织人工清淤并恢复通水', '/uploads/seed/task/03.jpg', 4, '刘卫东', 'HANDLED', '2026-10-21 13:20:01'),
(6, 26, 'LEAK', '支渠衬砌板接缝渗漏，沿渠肩出现明显湿痕', 297.5, NULL, '/uploads/seed/task/02.jpg', 5, '陈立新', 'OPEN', '2026-10-22 13:20:58'),
(7, 31, 'FAULT', '闸门启闭机电机烧毁，无法电动调流', 345.0, '已组织人工清淤并恢复通水', '/uploads/seed/task/01.jpg', 6, '杨春生', 'HANDLED', '2026-10-23 13:20:46'),
(8, 36, 'SHORT', '水源可用量低于计划值，末端地块供水中断', 392.5, NULL, '/uploads/seed/task/04.jpg', 7, '郭建军', 'OPEN', '2026-10-24 13:20:31');
INSERT INTO `rule_config` (`id`, `name`, `version`, `crop_weight`, `stage_weight`, `area_weight`, `soil_weight`, `rain_weight`, `history_weight`, `status`, `effective_time`, `create_by`, `create_time`) VALUES
(1, '作物阶段用水建议（初版）', 'v1', 20, 20, 20, 15, 15, 10, 'DISABLED', '2026-05-24 09:00:56', '张建民', '2026-05-24 09:00:17'),
(2, '作物阶段用水建议（调整面积权重）', 'v2', 22, 20, 18, 15, 15, 10, 'DISABLED', '2026-08-02 09:00:05', '张建民', '2026-08-02 09:00:23'),
(3, '作物阶段用水建议（现行）', 'v3', 24, 22, 18, 14, 12, 10, 'ACTIVE', '2026-09-15 09:00:42', '张建民', '2026-09-15 09:00:41');
INSERT INTO `water_advice` (`id`, `task_id`, `farmland_id`, `rule_id`, `rule_version`, `snapshot`, `crop_score`, `stage_score`, `area_score`, `soil_score`, `rain_score`, `history_score`, `total_score`, `suggest_volume`, `quota_volume`, `deviation`, `grade`, `explain_main`, `explain_missing`, `explain_improve`, `adjust_volume`, `adjust_reason`, `adjust_by`, `adjust_time`, `create_time`) VALUES
(1, 1, 1, 3, 'v3', '{"crop":"水稻","stage":"分蘖期","area":48.0,"soil":"壤土","rain":8.6,"history":40.2}', 55.0, 48.0, 40.0, 42.0, 30.0, 46.0, 45.04, 1353.6, 1504.0, -10.0, 'RECOMMEND', '分蘖期需水系数偏高，作物与阶段合计权重 46%', '近 7 天降雨 18.6 mm，已折减 6%', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', NULL, NULL, NULL, NULL, '2026-10-13 09:05:50'),
(2, 2, 2, 3, 'v3', '{"crop":"小麦","stage":"成熟期","area":65.4,"soil":"黏土","rain":9.6,"history":41.2}', 63.5, 55.2, 46.8, 51.5, 37.4, 54.1, 52.92, 1751.86, 1904.2, -8.0, 'RECOMMEND', '土壤保水等级偏低，蒸发损失高于一级地块', '渠道末段水头不足，实际过流低于设计值', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', NULL, NULL, NULL, NULL, '2026-10-14 09:05:22'),
(3, 3, 3, 3, 'v3', '{"crop":"玉米","stage":"成熟期","area":82.8,"soil":"砂壤土","rain":10.6,"history":42.2}', 72.0, 62.4, 53.6, 61.0, 44.8, 62.2, 60.79, 2166.14, 2304.4, -6.0, 'RECOMMEND', '分蘖期需水系数偏高，作物与阶段合计权重 46%', '渠道末段水头不足，实际过流低于设计值', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', NULL, NULL, NULL, NULL, '2026-10-15 09:05:03'),
(4, 4, 4, 3, 'v3', '{"crop":"蔬菜","stage":"结果期","area":100.2,"soil":"砂土","rain":11.6,"history":43.2}', 80.5, 69.6, 60.4, 70.5, 52.2, 70.3, 68.67, 2596.42, 2704.6, -4.0, 'RECOMMEND', '土壤保水等级偏低，蒸发损失高于一级地块', '近 7 天降雨 18.6 mm，已折减 6%', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', 2622.38, '渠道末段水头不足需补量', '王海涛', '2026-10-26 16:10:41', '2026-10-16 09:05:48'),
(5, 5, 5, 3, 'v3', '{"crop":"果树","stage":"果实膨大期","area":117.6,"soil":"壤土","rain":12.6,"history":44.2}', 89.0, 76.8, 67.2, 42.0, 59.6, 78.4, 71.22, 3042.7, 3104.8, -2.0, 'RECOMMEND', '分蘖期需水系数偏高，作物与阶段合计权重 46%', '渠道末段水头不足，实际过流低于设计值', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', NULL, NULL, NULL, NULL, '2026-10-17 09:05:15'),
(6, 6, 6, 3, 'v3', '{"crop":"棉花","stage":"拔节期","area":133.0,"soil":"黏土","rain":13.6,"history":45.2}', 55.0, 84.0, 74.0, 51.5, 67.0, 46.0, 64.85, 3459.0, 3459.0, 0.0, 'RECOMMEND', '土壤保水等级偏低，蒸发损失高于一级地块', '渠道末段水头不足，实际过流低于设计值', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', NULL, NULL, NULL, NULL, '2026-10-18 09:05:01'),
(7, 7, 7, 3, 'v3', '{"crop":"水稻","stage":"成熟期","area":150.4,"soil":"砂壤土","rain":14.6,"history":46.2}', 63.5, 48.0, 80.8, 61.0, 74.4, 54.1, 63.22, 3936.38, 3859.2, 2.0, 'RECOMMEND', '分蘖期需水系数偏高，作物与阶段合计权重 46%', '近 7 天降雨 18.6 mm，已折减 6%', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', NULL, NULL, NULL, NULL, '2026-10-19 09:05:51'),
(8, 8, 8, 3, 'v3', '{"crop":"小麦","stage":"拔节期","area":167.8,"soil":"砂土","rain":15.6,"history":47.2}', 72.0, 55.2, 40.0, 70.5, 81.8, 62.2, 62.53, 4429.78, 4259.4, 4.0, 'RECOMMEND', '土壤保水等级偏低，蒸发损失高于一级地块', '渠道末段水头不足，实际过流低于设计值', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', NULL, NULL, NULL, NULL, '2026-10-20 09:05:56'),
(9, 9, 9, 3, 'v3', '{"crop":"玉米","stage":"拔节期","area":185.2,"soil":"壤土","rain":16.6,"history":48.2}', 80.5, 62.4, 46.8, 42.0, 30.0, 70.3, 57.98, 4939.18, 4659.6, 6.0, 'RECOMMEND', '分蘖期需水系数偏高，作物与阶段合计权重 46%', '渠道末段水头不足，实际过流低于设计值', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', NULL, NULL, NULL, NULL, '2026-10-21 09:05:14'),
(10, 10, 10, 3, 'v3', '{"crop":"蔬菜","stage":"结果期","area":202.6,"soil":"黏土","rain":17.6,"history":49.2}', 89.0, 69.6, 53.6, 51.5, 37.4, 78.4, 65.86, 4553.82, 5059.8, -10.0, 'RECOMMEND', '土壤保水等级偏低，蒸发损失高于一级地块', '近 7 天降雨 18.6 mm，已折减 6%', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', 4599.36, '渠道末段水头不足需补量', '王海涛', '2026-10-26 16:10:00', '2026-10-22 09:05:01'),
(11, 11, 11, 3, 'v3', '{"crop":"果树","stage":"果实膨大期","area":218.0,"soil":"砂壤土","rain":18.6,"history":50.2}', 55.0, 76.8, 60.4, 61.0, 44.8, 46.0, 59.48, 4980.88, 5414.0, -8.0, 'RECOMMEND', '分蘖期需水系数偏高，作物与阶段合计权重 46%', '渠道末段水头不足，实际过流低于设计值', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', NULL, NULL, NULL, NULL, '2026-10-23 09:05:12'),
(12, 12, 12, 3, 'v3', '{"crop":"棉花","stage":"拔节期","area":235.4,"soil":"砂土","rain":19.6,"history":51.2}', 63.5, 84.0, 67.2, 70.5, 52.2, 54.1, 67.36, 5465.35, 5814.2, -6.0, 'RECOMMEND', '土壤保水等级偏低，蒸发损失高于一级地块', '渠道末段水头不足，实际过流低于设计值', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', NULL, NULL, NULL, NULL, '2026-10-24 09:05:36'),
(13, 13, 13, 3, 'v3', '{"crop":"水稻","stage":"孕穗期","area":252.8,"soil":"壤土","rain":20.6,"history":40.2}', 72.0, 48.0, 74.0, 42.0, 59.6, 62.2, 60.41, 5965.82, 6214.4, -4.0, 'RECOMMEND', '分蘖期需水系数偏高，作物与阶段合计权重 46%', '近 7 天降雨 18.6 mm，已折减 6%', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', NULL, NULL, NULL, NULL, '2026-10-25 09:05:42'),
(14, 14, 14, 3, 'v3', '{"crop":"小麦","stage":"苗期","area":270.2,"soil":"黏土","rain":21.6,"history":41.2}', 80.5, 55.2, 80.8, 51.5, 67.0, 70.3, 68.29, 6482.31, 6614.6, -2.0, 'RECOMMEND', '土壤保水等级偏低，蒸发损失高于一级地块', '渠道末段水头不足，实际过流低于设计值', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', NULL, NULL, NULL, NULL, '2026-10-26 09:05:11'),
(15, 15, 15, 3, 'v3', '{"crop":"玉米","stage":"成熟期","area":287.6,"soil":"砂壤土","rain":22.6,"history":42.2}', 89.0, 62.4, 40.0, 61.0, 74.4, 78.4, 67.6, 7014.8, 7014.8, 0.0, 'REVIEW', '分蘖期需水系数偏高，作物与阶段合计权重 46%', '渠道末段水头不足，实际过流低于设计值', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', NULL, NULL, NULL, NULL, '2026-10-27 09:05:09'),
(16, 16, 16, 3, 'v3', '{"crop":"蔬菜","stage":"结果期","area":303.0,"soil":"砂土","rain":23.6,"history":43.2}', 55.0, 69.6, 46.8, 70.5, 81.8, 46.0, 61.22, 7516.38, 7369.0, 2.0, 'REVIEW', '土壤保水等级偏低，蒸发损失高于一级地块', '近 7 天降雨 18.6 mm，已折减 6%', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', 7591.54, '渠道末段水头不足需补量', '王海涛', '2026-10-26 16:10:08', '2026-10-28 09:05:27'),
(17, 17, 17, 3, 'v3', '{"crop":"果树","stage":"果实膨大期","area":320.4,"soil":"壤土","rain":24.6,"history":44.2}', 63.5, 76.8, 53.6, 42.0, 30.0, 54.1, 56.67, 8079.97, 7769.2, 4.0, 'REVIEW', '分蘖期需水系数偏高，作物与阶段合计权重 46%', '渠道末段水头不足，实际过流低于设计值', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', NULL, NULL, NULL, NULL, '2026-10-13 09:05:48'),
(18, 18, 18, 3, 'v3', '{"crop":"棉花","stage":"拔节期","area":57.8,"soil":"黏土","rain":25.6,"history":45.2}', 72.0, 84.0, 60.4, 51.5, 37.4, 62.2, 64.55, 1833.16, 1729.4, 6.0, 'REVIEW', '土壤保水等级偏低，蒸发损失高于一级地块', '渠道末段水头不足，实际过流低于设计值', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', NULL, NULL, NULL, NULL, '2026-10-14 09:05:06'),
(19, 19, 19, 3, 'v3', '{"crop":"水稻","stage":"苗期","area":75.2,"soil":"砂壤土","rain":26.6,"history":46.2}', 80.5, 48.0, 67.2, 61.0, 44.8, 70.3, 62.92, 1916.64, 2129.6, -10.0, 'REVIEW', '分蘖期需水系数偏高，作物与阶段合计权重 46%', '近 7 天降雨 18.6 mm，已折减 6%', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', NULL, NULL, NULL, NULL, '2026-10-15 09:05:46'),
(20, 20, 20, 3, 'v3', '{"crop":"小麦","stage":"抽穗期","area":92.6,"soil":"砂土","rain":27.6,"history":47.2}', 89.0, 55.2, 74.0, 70.5, 52.2, 78.4, 70.8, 2327.42, 2529.8, -8.0, 'REVIEW', '土壤保水等级偏低，蒸发损失高于一级地块', '渠道末段水头不足，实际过流低于设计值', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', NULL, NULL, NULL, NULL, '2026-10-16 09:05:09'),
(21, 21, 21, 3, 'v3', '{"crop":"玉米","stage":"拔节期","area":108.0,"soil":"壤土","rain":8.6,"history":48.2}', 55.0, 62.4, 80.8, 42.0, 59.6, 46.0, 59.1, 2710.96, 2884.0, -6.0, 'REVIEW', '分蘖期需水系数偏高，作物与阶段合计权重 46%', '渠道末段水头不足，实际过流低于设计值', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', NULL, NULL, NULL, NULL, '2026-10-17 09:05:28'),
(22, 22, 22, 3, 'v3', '{"crop":"蔬菜","stage":"结果期","area":125.4,"soil":"黏土","rain":9.6,"history":49.2}', 63.5, 69.6, 40.0, 51.5, 67.0, 54.1, 58.41, 3152.83, 3284.2, -4.0, 'REVIEW', '土壤保水等级偏低，蒸发损失高于一级地块', '近 7 天降雨 18.6 mm，已折减 6%', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', 3184.36, '渠道末段水头不足需补量', '王海涛', '2026-10-26 16:10:51', '2026-10-18 09:05:55'),
(23, 23, 23, 3, 'v3', '{"crop":"果树","stage":"果实膨大期","area":142.8,"soil":"砂壤土","rain":10.6,"history":50.2}', 72.0, 76.8, 46.8, 61.0, 74.4, 62.2, 66.29, 3610.71, 3684.4, -2.0, 'REVIEW', '分蘖期需水系数偏高，作物与阶段合计权重 46%', '渠道末段水头不足，实际过流低于设计值', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', NULL, NULL, NULL, NULL, '2026-10-19 09:05:30'),
(24, 24, 24, 3, 'v3', '{"crop":"棉花","stage":"拔节期","area":160.2,"soil":"砂土","rain":11.6,"history":51.2}', 80.5, 84.0, 53.6, 70.5, 81.8, 70.3, 74.16, 4084.6, 4084.6, 0.0, 'DEVIATE', '土壤保水等级偏低，蒸发损失高于一级地块', '渠道末段水头不足，实际过流低于设计值', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', NULL, NULL, NULL, NULL, '2026-10-20 09:05:56'),
(25, 25, 25, 3, 'v3', '{"crop":"水稻","stage":"抽穗期","area":177.6,"soil":"壤土","rain":12.6,"history":40.2}', 89.0, 48.0, 60.4, 42.0, 30.0, 78.4, 60.11, 4574.5, 4484.8, 2.0, 'DEVIATE', '分蘖期需水系数偏高，作物与阶段合计权重 46%', '近 7 天降雨 18.6 mm，已折减 6%', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', NULL, NULL, NULL, NULL, '2026-10-21 09:05:53'),
(26, 26, 26, 3, 'v3', '{"crop":"小麦","stage":"分蘖期","area":193.0,"soil":"黏土","rain":13.6,"history":41.2}', 55.0, 55.2, 67.2, 51.5, 37.4, 46.0, 53.74, 5032.56, 4839.0, 4.0, 'DEVIATE', '土壤保水等级偏低，蒸发损失高于一级地块', '渠道末段水头不足，实际过流低于设计值', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', NULL, NULL, NULL, NULL, '2026-10-22 09:05:54'),
(27, 27, 1, 3, 'v3', '{"crop":"水稻","stage":"分蘖期","area":48.0,"soil":"壤土","rain":14.6,"history":42.2}', 63.5, 62.4, 74.0, 61.0, 44.8, 54.1, 61.61, 1594.24, 1504.0, 6.0, 'DEVIATE', '分蘖期需水系数偏高，作物与阶段合计权重 46%', '渠道末段水头不足，实际过流低于设计值', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', NULL, NULL, NULL, NULL, '2026-10-23 09:05:37'),
(28, 28, 2, 3, 'v3', '{"crop":"小麦","stage":"成熟期","area":65.4,"soil":"黏土","rain":15.6,"history":43.2}', 72.0, 69.6, 80.8, 70.5, 52.2, 62.2, 69.49, 1713.78, 1904.2, -10.0, 'DEVIATE', '土壤保水等级偏低，蒸发损失高于一级地块', '近 7 天降雨 18.6 mm，已折减 6%', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', 1730.92, '渠道末段水头不足需补量', '王海涛', '2026-10-26 16:10:16', '2026-10-24 09:05:54'),
(29, 29, 3, 3, 'v3', '{"crop":"玉米","stage":"成熟期","area":82.8,"soil":"砂壤土","rain":16.6,"history":44.2}', 80.5, 76.8, 40.0, 42.0, 59.6, 70.3, 63.48, 2120.05, 2304.4, -8.0, 'DEVIATE', '分蘖期需水系数偏高，作物与阶段合计权重 46%', '渠道末段水头不足，实际过流低于设计值', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', NULL, NULL, NULL, NULL, '2026-10-25 09:05:03'),
(30, 30, 4, 3, 'v3', '{"crop":"蔬菜","stage":"结果期","area":100.2,"soil":"砂土","rain":17.6,"history":45.2}', 89.0, 84.0, 46.8, 51.5, 67.0, 78.4, 71.35, 2542.32, 2704.6, -6.0, 'DEVIATE', '土壤保水等级偏低，蒸发损失高于一级地块', '渠道末段水头不足，实际过流低于设计值', '建议改为傍晚时段灌溉，可减少约 6% 蒸发损失', NULL, NULL, NULL, NULL, '2026-10-26 09:05:06'),
(31, 31, 5, 3, 'v3', '{"crop":"果树","stage":"果实膨大期","area":117.6,"soil":"壤土","rain":18.6,"history":46.2}', 55.0, 48.0, 53.6, 61.0, 74.4, 46.0, 55.48, 0, 3104.8, 0, 'INSUFFICIENT', '缺少近期降雨记录，历史单耗不足 3 年，暂不给出建议水量', '近期降雨与历史单耗缺失', '补录近 7 天降雨量与最近 3 年灌溉记录后重新计算', NULL, NULL, NULL, NULL, '2026-10-27 09:05:37'),
(32, 32, 6, 3, 'v3', '{"crop":"棉花","stage":"拔节期","area":133.0,"soil":"黏土","rain":19.6,"history":47.2}', 63.5, 55.2, 60.4, 70.5, 81.8, 54.1, 63.35, 0, 3459.0, 0, 'INSUFFICIENT', '缺少近期降雨记录，历史单耗不足 3 年，暂不给出建议水量', '近期降雨与历史单耗缺失', '补录近 7 天降雨量与最近 3 年灌溉记录后重新计算', NULL, NULL, NULL, NULL, '2026-10-28 09:05:37');
INSERT INTO `fee_rule` (`id`, `name`, `base_price`, `excess_price`, `free_quota_per_mu`, `status`, `effective_time`) VALUES
(1, '2026 年度农业水价', 0.42, 0.55, 30.0, 'ACTIVE', '2026-04-14 00:00:54');
INSERT INTO `sys_message` (`id`, `title`, `content`, `biz_no`, `biz_type`, `receiver_id`, `read_flag`, `create_time`) VALUES
(1, '任务待执行提醒', '业务单据 TK-20261031-001 需要处理，请及时进入详情页确认。', 'TK-20261031-001', 'TASK', 4, 0, '2026-10-22 08:15:43'),
(2, '用水申请待审核', '业务单据 TK-20261031-002 需要处理，请及时进入详情页确认。', 'TK-20261031-002', 'APPLICATION', 1, 0, '2026-10-23 09:15:03'),
(3, '定额余量不足预警', '业务单据 TK-20261031-003 需要处理，请及时进入详情页确认。', 'TK-20261031-003', 'QUOTA', 8, 0, '2026-10-24 10:15:34'),
(4, '任务待执行提醒', '业务单据 TK-20261031-004 需要处理，请及时进入详情页确认。', 'TK-20261031-004', 'TASK', 4, 0, '2026-10-25 11:15:11'),
(5, '用水申请待审核', '业务单据 TK-20261031-005 需要处理，请及时进入详情页确认。', 'TK-20261031-005', 'APPLICATION', 1, 0, '2026-10-26 12:15:03'),
(6, '定额余量不足预警', '业务单据 TK-20261031-006 需要处理，请及时进入详情页确认。', 'TK-20261031-006', 'QUOTA', 8, 1, '2026-10-27 13:15:49'),
(7, '任务待执行提醒', '业务单据 TK-20261031-007 需要处理，请及时进入详情页确认。', 'TK-20261031-007', 'TASK', 4, 1, '2026-10-28 08:15:33'),
(8, '用水申请待审核', '业务单据 TK-20261031-008 需要处理，请及时进入详情页确认。', 'TK-20261031-008', 'APPLICATION', 1, 1, '2026-10-29 09:15:38'),
(9, '定额余量不足预警', '业务单据 TK-20261031-009 需要处理，请及时进入详情页确认。', 'TK-20261031-009', 'QUOTA', 8, 1, '2026-10-22 10:15:01'),
(10, '任务待执行提醒', '业务单据 TK-20261031-010 需要处理，请及时进入详情页确认。', 'TK-20261031-010', 'TASK', 4, 1, '2026-10-23 11:15:46'),
(11, '用水申请待审核', '业务单据 TK-20261031-011 需要处理，请及时进入详情页确认。', 'TK-20261031-011', 'APPLICATION', 1, 1, '2026-10-24 12:15:51'),
(12, '定额余量不足预警', '业务单据 TK-20261031-012 需要处理，请及时进入详情页确认。', 'TK-20261031-012', 'QUOTA', 8, 1, '2026-10-25 13:15:18');
INSERT INTO `sys_operation_log` (`id`, `biz_type`, `biz_id`, `biz_no`, `action`, `before_status`, `after_status`, `reason`, `operator_id`, `operator_name`, `create_time`) VALUES
(1, 'APPLICATION', 1, 'AP-20261031-001', '提交申请', 'DRAFT', 'PENDING_AUDIT', '渠道容量不足需重新排程', 1, '张建民', '2026-10-07 09:00:59'),
(2, 'PLAN', 2, 'PL-20261020-002', '审核通过', 'PENDING_AUDIT', 'PENDING_SCHEDULE', NULL, 2, '王海涛', '2026-10-08 10:17:58'),
(3, 'APPLICATION', 3, 'AP-20261031-003', '编制计划', NULL, 'DRAFT', NULL, 1, '张建民', '2026-10-09 11:34:47'),
(4, 'PLAN', 4, 'PL-20261022-004', '提交审批', 'DRAFT', 'AUDITING', NULL, 2, '王海涛', '2026-10-10 12:51:26'),
(5, 'APPLICATION', 5, 'AP-20261031-005', '审批通过', 'AUDITING', 'ISSUED', NULL, 1, '张建民', '2026-10-11 13:08:37'),
(6, 'PLAN', 6, 'PL-20261024-006', '下达任务', 'ISSUED', 'EXECUTING', NULL, 2, '王海涛', '2026-10-12 14:25:41'),
(7, 'APPLICATION', 7, 'AP-20261031-007', '开始执行', 'PENDING', 'RUNNING', NULL, 1, '张建民', '2026-10-13 15:42:23'),
(8, 'PLAN', 8, 'PL-20261026-008', '用量确认', 'RUNNING', 'FINISHED', NULL, 2, '王海涛', '2026-10-14 16:59:16'),
(9, 'APPLICATION', 9, 'AP-20261031-009', '归档', 'CONFIRMING', 'ARCHIVED', NULL, 1, '张建民', '2026-10-15 09:16:28'),
(10, 'PLAN', 10, 'PL-20261028-010', '提交申请', 'DRAFT', 'PENDING_AUDIT', NULL, 2, '王海涛', '2026-10-16 10:33:26'),
(11, 'APPLICATION', 11, 'AP-20261031-011', '审核通过', 'PENDING_AUDIT', 'PENDING_SCHEDULE', NULL, 1, '张建民', '2026-10-17 11:50:53'),
(12, 'PLAN', 12, 'PL-20261030-012', '编制计划', NULL, 'DRAFT', '渠道容量不足需重新排程', 2, '王海涛', '2026-10-18 12:07:45'),
(13, 'APPLICATION', 13, 'AP-20261031-013', '提交审批', 'DRAFT', 'AUDITING', NULL, 1, '张建民', '2026-10-19 13:24:57'),
(14, 'PLAN', 14, 'PL-20261101-014', '审批通过', 'AUDITING', 'ISSUED', NULL, 2, '王海涛', '2026-10-20 14:41:00'),
(15, 'APPLICATION', 15, 'AP-20261031-015', '下达任务', 'ISSUED', 'EXECUTING', NULL, 1, '张建民', '2026-10-21 15:58:38'),
(16, 'PLAN', 16, 'PL-20261103-016', '开始执行', 'PENDING', 'RUNNING', NULL, 2, '王海涛', '2026-10-22 16:15:04'),
(17, 'APPLICATION', 17, 'AP-20261031-017', '用量确认', 'RUNNING', 'FINISHED', NULL, 1, '张建民', '2026-10-23 09:32:50'),
(18, 'PLAN', 18, 'PL-20261105-018', '归档', 'CONFIRMING', 'ARCHIVED', NULL, 2, '王海涛', '2026-10-24 10:49:47'),
(19, 'APPLICATION', 19, 'AP-20261031-019', '提交申请', 'DRAFT', 'PENDING_AUDIT', NULL, 1, '张建民', '2026-10-25 11:06:13'),
(20, 'PLAN', 20, 'PL-20261107-020', '审核通过', 'PENDING_AUDIT', 'PENDING_SCHEDULE', NULL, 2, '王海涛', '2026-10-26 12:23:09'),
(21, 'APPLICATION', 21, 'AP-20261031-021', '编制计划', NULL, 'DRAFT', NULL, 1, '张建民', '2026-10-27 13:40:13'),
(22, 'PLAN', 22, 'PL-20261020-022', '提交审批', 'DRAFT', 'AUDITING', NULL, 2, '王海涛', '2026-10-28 14:57:21'),
(23, 'APPLICATION', 23, 'AP-20261031-023', '审批通过', 'AUDITING', 'ISSUED', '渠道容量不足需重新排程', 1, '张建民', '2026-10-07 15:14:29'),
(24, 'PLAN', 24, 'PL-20261022-024', '下达任务', 'ISSUED', 'EXECUTING', NULL, 2, '王海涛', '2026-10-08 16:31:09'),
(25, 'APPLICATION', 25, 'AP-20261031-025', '开始执行', 'PENDING', 'RUNNING', NULL, 1, '张建民', '2026-10-09 09:48:59'),
(26, 'PLAN', 26, 'PL-20261024-026', '用量确认', 'RUNNING', 'FINISHED', NULL, 2, '王海涛', '2026-10-10 10:05:45'),
(27, 'APPLICATION', 27, 'AP-20261031-027', '归档', 'CONFIRMING', 'ARCHIVED', NULL, 1, '张建民', '2026-10-11 11:22:32'),
(28, 'PLAN', 28, 'PL-20261026-028', '提交申请', 'DRAFT', 'PENDING_AUDIT', NULL, 2, '王海涛', '2026-10-12 12:39:31'),
(29, 'APPLICATION', 29, 'AP-20261031-029', '审核通过', 'PENDING_AUDIT', 'PENDING_SCHEDULE', NULL, 1, '张建民', '2026-10-13 13:56:43'),
(30, 'PLAN', 30, 'PL-20261028-030', '编制计划', NULL, 'DRAFT', NULL, 2, '王海涛', '2026-10-14 14:13:02'),
(31, 'APPLICATION', 31, 'AP-20261031-031', '提交审批', 'DRAFT', 'AUDITING', NULL, 1, '张建民', '2026-10-15 15:30:40'),
(32, 'PLAN', 32, 'PL-20261030-032', '审批通过', 'AUDITING', 'ISSUED', NULL, 2, '王海涛', '2026-10-16 16:47:33'),
(33, 'APPLICATION', 33, 'AP-20261031-033', '下达任务', 'ISSUED', 'EXECUTING', NULL, 1, '张建民', '2026-10-17 09:04:02'),
(34, 'PLAN', 34, 'PL-20261101-034', '开始执行', 'PENDING', 'RUNNING', '渠道容量不足需重新排程', 2, '王海涛', '2026-10-18 10:21:21'),
(35, 'APPLICATION', 35, 'AP-20261031-035', '用量确认', 'RUNNING', 'FINISHED', NULL, 1, '张建民', '2026-10-19 11:38:14'),
(36, 'PLAN', 2, 'PL-20261020-002', '归档', 'CONFIRMING', 'ARCHIVED', NULL, 2, '王海涛', '2026-10-20 12:55:03'),
(37, 'APPLICATION', 37, 'AP-20261031-037', '提交申请', 'DRAFT', 'PENDING_AUDIT', NULL, 1, '张建民', '2026-10-21 13:12:50'),
(38, 'PLAN', 4, 'PL-20261022-004', '审核通过', 'PENDING_AUDIT', 'PENDING_SCHEDULE', NULL, 2, '王海涛', '2026-10-22 14:29:30'),
(39, 'APPLICATION', 39, 'AP-20261031-039', '编制计划', NULL, 'DRAFT', NULL, 1, '张建民', '2026-10-23 15:46:19'),
(40, 'PLAN', 6, 'PL-20261024-006', '提交审批', 'DRAFT', 'AUDITING', NULL, 2, '王海涛', '2026-10-24 16:03:48'),
(41, 'APPLICATION', 41, 'AP-20261031-041', '审批通过', 'AUDITING', 'ISSUED', NULL, 1, '张建民', '2026-10-25 09:20:41'),
(42, 'PLAN', 8, 'PL-20261026-008', '下达任务', 'ISSUED', 'EXECUTING', NULL, 2, '王海涛', '2026-10-26 10:37:16'),
(43, 'APPLICATION', 43, 'AP-20261031-043', '开始执行', 'PENDING', 'RUNNING', NULL, 1, '张建民', '2026-10-27 11:54:44'),
(44, 'PLAN', 10, 'PL-20261028-010', '用量确认', 'RUNNING', 'FINISHED', NULL, 2, '王海涛', '2026-10-28 12:11:07'),
(45, 'APPLICATION', 45, 'AP-20261031-045', '归档', 'CONFIRMING', 'ARCHIVED', '渠道容量不足需重新排程', 1, '张建民', '2026-10-07 13:28:08'),
(46, 'PLAN', 12, 'PL-20261030-012', '提交申请', 'DRAFT', 'PENDING_AUDIT', NULL, 2, '王海涛', '2026-10-08 14:45:15'),
(47, 'APPLICATION', 47, 'AP-20261031-047', '审核通过', 'PENDING_AUDIT', 'PENDING_SCHEDULE', NULL, 1, '张建民', '2026-10-09 15:02:06'),
(48, 'PLAN', 14, 'PL-20261101-014', '编制计划', NULL, 'DRAFT', NULL, 2, '王海涛', '2026-10-10 16:19:18');

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
