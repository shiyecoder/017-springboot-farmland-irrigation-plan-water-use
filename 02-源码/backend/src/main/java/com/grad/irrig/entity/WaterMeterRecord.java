package com.grad.irrig.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableField;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import lombok.Data;

/** 水表记录。字段与 sql/init.sql 中 `water_meter_record` 一一对应。 */
@Data
@TableName("water_meter_record")
public class WaterMeterRecord {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 任务 */
    private Long taskId;
    /** 水表 */
    private Long meterId;
    /** 开始表数 */
    private BigDecimal startReading;
    /** 结束表数 */
    private BigDecimal endReading;
    /** 本段水量 */
    private BigDecimal volume;
    /** 抄表时间 */
    private LocalDateTime recordTime;
    /** 抄表人 */
    private Long recorderId;
    /** 抄表人姓名 */
    private String recorderName;
    /** 表盘照片 */
    private String photo;
    /** 备注 */
    private String remark;
}
