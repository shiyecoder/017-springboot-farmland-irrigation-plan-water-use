package com.grad.irrig.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableField;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import lombok.Data;

/** 用户。字段与 sql/init.sql 中 `sys_user` 一一对应。 */
@Data
@TableName("sys_user")
public class SysUser {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 登录账号 */
    private String username;
    /** BCrypt 密码 */
    private String password;
    /** 姓名 */
    private String realName;
    /** 联系电话 */
    private String phone;
    /** 邮箱 */
    private String email;
    /** 头像相对路径 */
    private String avatar;
    /** 角色 */
    private Long roleId;
    /** 所属组织 */
    private Long orgId;
    /** 状态 */
    private Integer status;
    /** 连续登录失败次数 */
    private Integer loginFailCount;
    /** 锁定截止时间 */
    private LocalDateTime lockUntil;
    /** 最近登录时间 */
    private LocalDateTime lastLoginTime;
    /** 创建时间 */
    private LocalDateTime createTime;
    /** 更新时间 */
    private LocalDateTime updateTime;
}
