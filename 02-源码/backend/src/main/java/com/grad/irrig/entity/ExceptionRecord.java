package com.grad.irrig.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableField;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import lombok.Data;

/** 异常处置。字段与 sql/init.sql 中 `exception_record` 一一对应。 */
@Data
@TableName("exception_record")
public class ExceptionRecord {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 任务 */
    private Long taskId;
    /** 异常类型 */
    private String excType;
    /** 异常描述 */
    private String description;
    /** 损失水量 */
    private BigDecimal lossVolume;
    /** 处理结果 */
    private String handleResult;
    /** 现场照片 */
    private String photo;
    /** 上报人 */
    private Long reporterId;
    /** 上报人姓名 */
    private String reporterName;
    /** 状态 */
    private String status;
    /** 上报时间 */
    private LocalDateTime createTime;
}
