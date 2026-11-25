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

/** 水权定额。字段与 sql/init.sql 中 `water_quota` 一一对应。 */
@Data
@TableName("water_quota")
public class WaterQuota {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 年度 */
    private Integer quotaYear;
    /** 地块 */
    private Long farmlandId;
    /** 种植户 */
    private Long farmerId;
    /** 种植户姓名 */
    private String farmerName;
    /** 定额水量 */
    private BigDecimal quotaVolume;
    /** 已用水量 */
    private BigDecimal usedVolume;
    /** 剩余水量 */
    private BigDecimal remainingVolume;
    /** 状态 */
    private String status;
    /** 乐观锁版本号 */
    @Version
    private Integer version;
    /** 创建时间 */
    private LocalDateTime createTime;
    /** 更新时间 */
    private LocalDateTime updateTime;
}
