package com.grad.irrig.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableField;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import lombok.Data;

/** 组织架构。字段与 sql/init.sql 中 `sys_org` 一一对应。 */
@Data
@TableName("sys_org")
public class SysOrg {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 组织编码 */
    private String code;
    /** 组织名称 */
    private String name;
    /** 上级组织 */
    private Long parentId;
    /** 组织类型 */
    private String orgType;
    /** 排序 */
    private Integer sortNo;
    /** 状态：1 启用 0 停用 */
    private Integer status;
    /** 创建时间 */
    private LocalDateTime createTime;
}
