package com.grad.irrig.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.Version;
import com.baomidou.mybatisplus.annotation.TableField;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import lombok.Data;

/** 灌溉计划。字段与 sql/init.sql 中 `irrigation_plan` 一一对应。 */
@Data
@TableName("irrigation_plan")
public class IrrigationPlan {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 计划编号 */
    private String code;
    /** 来源申请 */
    private Long applicationId;
    /** 地块 */
    private Long farmlandId;
    /** 渠道 */
    private Long canalId;
    /** 闸口 */
    private Long gateId;
    /** 计划开始 */
    private LocalDateTime planStart;
    /** 计划结束 */
    private LocalDateTime planEnd;
    /** 计划水量 */
    private BigDecimal planVolume;
    /** 优先级 */
    private String priority;
    /** 状态 */
    private String status;
    /** 调度员 */
    private Long dispatcherId;
    /** 调度员姓名 */
    private String dispatcherName;
    /** 驳回原因 */
    private String rejectReason;
    /** 备注 */
    private String remark;
    /** 乐观锁版本号 */
    @Version
    private Integer version;
    /** 创建时间 */
    private LocalDateTime createTime;
    /** 更新时间 */
    private LocalDateTime updateTime;
}
