package com.grad.irrig.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableField;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import lombok.Data;

/** 附件。字段与 sql/init.sql 中 `sys_file` 一一对应。 */
@Data
@TableName("sys_file")
public class SysFile {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 业务类型 */
    private String bizType;
    /** 业务主键 */
    private Long bizId;
    /** 原始文件名 */
    private String originName;
    /** 相对路径 */
    private String filePath;
    /** 字节数 */
    private Long fileSize;
    /** 上传人 */
    private Long uploaderId;
    /** 上传时间 */
    private LocalDateTime uploadTime;
}
