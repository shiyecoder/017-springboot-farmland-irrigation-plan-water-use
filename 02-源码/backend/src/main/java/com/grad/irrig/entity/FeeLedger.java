package com.grad.irrig.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableField;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import lombok.Data;

/** 费用台账。字段与 sql/init.sql 中 `fee_ledger` 一一对应。 */
@Data
@TableName("fee_ledger")
public class FeeLedger {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 费用单号 */
    private String code;
    /** 任务 */
    private Long taskId;
    /** 地块 */
    private Long farmlandId;
    /** 种植户 */
    private String farmerName;
    /** 实际水量 */
    private BigDecimal actualVolume;
    /** 定额内水量 */
    private BigDecimal baseVolume;
    /** 超额水量 */
    private BigDecimal excessVolume;
    /** 基础单价 */
    private BigDecimal basePrice;
    /** 超额单价 */
    private BigDecimal excessPrice;
    /** 金额 */
    private BigDecimal amount;
    /** 计费月份 */
    private String billMonth;
    /** 状态 */
    private String status;
    /** 缴费时间 */
    private LocalDateTime payTime;
    /** 创建时间 */
    private LocalDateTime createTime;
}
