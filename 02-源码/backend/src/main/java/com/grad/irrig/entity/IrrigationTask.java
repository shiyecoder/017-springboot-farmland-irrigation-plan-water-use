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

/** 灌溉任务。字段与 sql/init.sql 中 `irrigation_task` 一一对应。 */
@Data
@TableName("irrigation_task")
public class IrrigationTask {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 任务编号 */
    private String code;
    /** 灌溉计划 */
    private Long planId;
    /** 地块 */
    private Long farmlandId;
    /** 放水员 */
    private Long operatorId;
    /** 放水员姓名 */
    private String operatorName;
    /** 计划水量 */
    private BigDecimal planVolume;
    /** 开始表数 */
    private BigDecimal startReading;
    /** 结束表数 */
    private BigDecimal endReading;
    /** 实际水量 */
    private BigDecimal actualVolume;
    /** 实际开始 */
    private LocalDateTime startTime;
    /** 实际结束 */
    private LocalDateTime endTime;
    /** 状态 */
    private String status;
    /** 现场照片 */
    private String photo;
    /** 受水人确认 */
    private String receiverName;
    /** 确认时间 */
    private LocalDateTime confirmTime;
    /** 中断原因 */
    private String interruptReason;
    /** 乐观锁版本号 */
    @Version
    private Integer version;
    /** 创建时间 */
    private LocalDateTime createTime;
    /** 更新时间 */
    private LocalDateTime updateTime;
}
