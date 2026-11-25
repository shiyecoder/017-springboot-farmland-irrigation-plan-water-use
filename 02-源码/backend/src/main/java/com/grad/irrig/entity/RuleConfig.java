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

/** 用水建议规则。字段与 sql/init.sql 中 `rule_config` 一一对应。 */
@Data
@TableName("rule_config")
public class RuleConfig {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 规则名称 */
    private String name;
    /** 版本号 */
    @Version
    private String version;
    /** 作物权重 */
    private Integer cropWeight;
    /** 阶段权重 */
    private Integer stageWeight;
    /** 面积权重 */
    private Integer areaWeight;
    /** 土壤权重 */
    private Integer soilWeight;
    /** 降雨权重 */
    private Integer rainWeight;
    /** 历史权重 */
    private Integer historyWeight;
    /** 状态 */
    private String status;
    /** 生效时间 */
    private LocalDateTime effectiveTime;
    /** 创建人 */
    private String createBy;
    /** 创建时间 */
    private LocalDateTime createTime;
}
