package com.grad.irrig.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableField;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import lombok.Data;

/** 字典项。字段与 sql/init.sql 中 `sys_dict_item` 一一对应。 */
@Data
@TableName("sys_dict_item")
public class SysDictItem {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 字典类型 */
    private String dictType;
    /** 显示文本 */
    private String label;
    /** 存储值 */
    private String value;
    /** 排序 */
    private Integer sortNo;
    /** 状态 */
    private Integer status;
}
