package com.grad.irrig.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableField;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import lombok.Data;

/** 计费规则。字段与 sql/init.sql 中 `fee_rule` 一一对应。 */
@Data
@TableName("fee_rule")
public class FeeRule {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 规则名称 */
    private String name;
    /** 定额内单价 */
    private BigDecimal basePrice;
    /** 超额单价 */
    private BigDecimal excessPrice;
    /** 每亩免费定额 */
    private BigDecimal freeQuotaPerMu;
    /** 状态 */
    private String status;
    /** 生效时间 */
    private LocalDateTime effectiveTime;
}
