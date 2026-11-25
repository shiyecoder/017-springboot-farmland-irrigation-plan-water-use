package com.grad.irrig.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableField;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import lombok.Data;

/** 水表。字段与 sql/init.sql 中 `water_meter` 一一对应。 */
@Data
@TableName("water_meter")
public class WaterMeter {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 水表编号 */
    private String code;
    /** 水表名称 */
    private String name;
    /** 安装闸口 */
    private Long gateId;
    /** 关联地块 */
    private Long farmlandId;
    /** 初始读数 */
    private BigDecimal initReading;
    /** 当前读数 */
    private BigDecimal currentReading;
    /** 安装日期 */
    private LocalDate installDate;
    /** 表具照片 */
    private String photo;
    /** 状态 */
    private String status;
}
