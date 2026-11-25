package com.grad.irrig.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableField;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import lombok.Data;

/** 渠道。字段与 sql/init.sql 中 `canal` 一一对应。 */
@Data
@TableName("canal")
public class Canal {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 渠道编号 */
    private String code;
    /** 渠道名称 */
    private String name;
    /** 所属水源 */
    private Long sourceId;
    /** 干渠/支渠 */
    private String canalLevel;
    /** 设计流量 */
    private BigDecimal designFlow;
    /** 长度 km */
    private BigDecimal lengthKm;
    /** 状态 */
    private String status;
    /** 备注 */
    private String remark;
    /** 创建时间 */
    private LocalDateTime createTime;
}
