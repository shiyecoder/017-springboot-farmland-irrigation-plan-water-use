package com.grad.irrig.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableField;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import lombok.Data;

/** 用水建议留痕。字段与 sql/init.sql 中 `water_advice` 一一对应。 */
@Data
@TableName("water_advice")
public class WaterAdvice {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 关联任务 */
    private Long taskId;
    /** 地块 */
    private Long farmlandId;
    /** 规则版本 */
    private Long ruleId;
    /** 规则版本号 */
    private String ruleVersion;
    /** 输入快照 */
    private String snapshot;
    /** 作物得分 */
    private BigDecimal cropScore;
    /** 阶段得分 */
    private BigDecimal stageScore;
    /** 面积得分 */
    private BigDecimal areaScore;
    /** 土壤得分 */
    private BigDecimal soilScore;
    /** 降雨得分 */
    private BigDecimal rainScore;
    /** 历史得分 */
    private BigDecimal historyScore;
    /** 加权总分 */
    private BigDecimal totalScore;
    /** 建议水量 */
    private BigDecimal suggestVolume;
    /** 对比定额 */
    private BigDecimal quotaVolume;
    /** 偏差百分比 */
    private BigDecimal deviation;
    /** 结果等级 */
    private String grade;
    /** 主要影响因素 */
    private String explainMain;
    /** 未满足条件 */
    private String explainMissing;
    /** 可改进项 */
    private String explainImprove;
    /** 人工修正水量 */
    private BigDecimal adjustVolume;
    /** 修正原因 */
    private String adjustReason;
    /** 修正人 */
    private String adjustBy;
    /** 修正时间 */
    private LocalDateTime adjustTime;
    /** 计算时间 */
    private LocalDateTime createTime;
}
