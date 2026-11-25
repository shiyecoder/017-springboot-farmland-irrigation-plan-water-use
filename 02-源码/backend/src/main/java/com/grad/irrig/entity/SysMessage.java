package com.grad.irrig.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableField;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import lombok.Data;

/** 站内消息。字段与 sql/init.sql 中 `sys_message` 一一对应。 */
@Data
@TableName("sys_message")
public class SysMessage {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 标题 */
    private String title;
    /** 内容 */
    private String content;
    /** 业务编号 */
    private String bizNo;
    /** 业务类型 */
    private String bizType;
    /** 接收人 */
    private Long receiverId;
    /** 是否已读 */
    private Integer readFlag;
    /** 创建时间 */
    private LocalDateTime createTime;
}
