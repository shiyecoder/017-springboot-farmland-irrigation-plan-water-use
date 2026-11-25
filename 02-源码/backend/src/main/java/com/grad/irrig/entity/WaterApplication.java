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

/** 用水申请。字段与 sql/init.sql 中 `water_application` 一一对应。 */
@Data
@TableName("water_application")
public class WaterApplication {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 申请编号 */
    private String code;
    /** 地块 */
    private Long farmlandId;
    /** 作物 */
    private String crop;
    /** 种植阶段 */
    private String growthStage;
    /** 期望用水日期 */
    private LocalDate expectDate;
    /** 申请水量 */
    private BigDecimal applyVolume;
    /** 紧急程度 */
    private String urgency;
    /** 申请人 */
    private Long applicantId;
    /** 申请人姓名 */
    private String applicantName;
    /** 状态 */
    private String status;
    /** 审核意见 */
    private String auditOpinion;
    /** 审核人 */
    private String auditBy;
    /** 审核时间 */
    private LocalDateTime auditTime;
    /** 乐观锁版本号 */
    @Version
    private Integer version;
    /** 创建时间 */
    private LocalDateTime createTime;
    /** 更新时间 */
    private LocalDateTime updateTime;
}
