package com.grad.irrig.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.Version;
import com.baomidou.mybatisplus.annotation.TableField;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import lombok.Data;

/** 农田地块。字段与 sql/init.sql 中 `farmland` 一一对应。 */
@Data
@TableName("farmland")
public class Farmland {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 地块编号 */
    private String code;
    /** 地块名称 */
    private String name;
    /** 面积（亩） */
    private BigDecimal area;
    /** 作物 */
    private String crop;
    /** 种植阶段 */
    private String growthStage;
    /** 土壤类型 */
    private String soilType;
    /** 灌溉方式 */
    private String irrigationType;
    /** 所属片区 */
    private String region;
    /** 位置描述 */
    private String address;
    /** 承包种植户 */
    private Long ownerId;
    /** 种植户姓名 */
    private String ownerName;
    /** 所属组织 */
    private Long orgId;
    /** 地块照片 */
    private String photo;
    /** 状态 */
    private String status;
    /** 逻辑删除 */
    @TableLogic
    private Integer deleted;
    /** 乐观锁版本号 */
    @Version
    private Integer version;
    /** 创建时间 */
    private LocalDateTime createTime;
    /** 更新时间 */
    private LocalDateTime updateTime;
}
