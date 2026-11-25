package com.grad.irrig.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableField;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import lombok.Data;

/** 闸口。字段与 sql/init.sql 中 `gate` 一一对应。 */
@Data
@TableName("gate")
public class Gate {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 闸口编号 */
    private String code;
    /** 闸口名称 */
    private String name;
    /** 所属渠道 */
    private Long canalId;
    /** 设计流量 */
    private BigDecimal designFlow;
    /** 开度百分比 */
    private Integer openDegree;
    /** 状态 */
    private String status;
    /** 备注 */
    private String remark;
}
