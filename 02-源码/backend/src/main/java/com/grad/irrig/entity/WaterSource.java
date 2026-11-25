package com.grad.irrig.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableField;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import lombok.Data;

/** 水源。字段与 sql/init.sql 中 `water_source` 一一对应。 */
@Data
@TableName("water_source")
public class WaterSource {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 水源编号 */
    private String code;
    /** 水源名称 */
    private String name;
    /** 水库/机井/河道/塘坝 */
    private String sourceType;
    /** 设计日供水 */
    private BigDecimal designSupply;
    /** 当前可用水量 */
    private BigDecimal availableVolume;
    /** 负责人 */
    private String manager;
    /** 联系电话 */
    private String phone;
    /** 现场照片 */
    private String photo;
    /** 状态 */
    private String status;
    /** 备注 */
    private String remark;
    /** 创建时间 */
    private LocalDateTime createTime;
}
