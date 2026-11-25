package com.grad.irrig.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableField;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import lombok.Data;

/** 操作日志。字段与 sql/init.sql 中 `sys_operation_log` 一一对应。 */
@Data
@TableName("sys_operation_log")
public class SysOperationLog {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 业务类型 */
    private String bizType;
    /** 业务主键 */
    private Long bizId;
    /** 业务编号 */
    private String bizNo;
    /** 动作 */
    private String action;
    /** 变更前状态 */
    private String beforeStatus;
    /** 变更后状态 */
    private String afterStatus;
    /** 原因 */
    private String reason;
    /** 操作人 */
    private Long operatorId;
    /** 操作人姓名 */
    private String operatorName;
    /** 操作时间 */
    private LocalDateTime createTime;
}
