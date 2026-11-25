package com.grad.irrig.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableField;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import lombok.Data;

/** 菜单。字段与 sql/init.sql 中 `sys_menu` 一一对应。 */
@Data
@TableName("sys_menu")
public class SysMenu {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 上级菜单 */
    private Long parentId;
    /** 菜单名称 */
    private String name;
    /** 前端路由 */
    private String path;
    /** 图标 */
    private String icon;
    /** M 目录 C 菜单 F 按钮 */
    private String menuType;
    /** 权限标识 */
    private String perm;
    /** 排序 */
    private Integer sortNo;
    /** 是否显示 */
    private Integer visible;
}
