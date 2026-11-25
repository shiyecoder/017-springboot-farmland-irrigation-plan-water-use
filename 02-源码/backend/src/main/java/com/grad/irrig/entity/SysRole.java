package com.grad.irrig.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableField;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import lombok.Data;

/** 角色。字段与 sql/init.sql 中 `sys_role` 一一对应。 */
@Data
@TableName("sys_role")
public class SysRole {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 角色编码 */
    private String code;
    /** 角色名称 */
    private String name;
    /** 数据范围 ALL/DEPT/SELF */
    private String dataScope;
    /** 说明 */
    private String remark;
    /** 创建时间 */
    private LocalDateTime createTime;
}
