package com.grad.irrig.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.grad.irrig.common.BizException;
import com.grad.irrig.common.PageResult;
import com.grad.irrig.common.UserContext;
import com.grad.irrig.entity.*;
import com.grad.irrig.mapper.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.util.*;

/**
 * 创新点：作物阶段用水建议。
 *
 * 设计原则——「可解释的业务辅助工具」：
 *   1. 权重可配置，合计必须 100%，调整后生成新版本并记录生效时间
 *   2. 每次计算保存输入快照 + 规则版本 + 各项得分 + 结果等级，可追溯
 *   3. 结果页同时给出推荐结果、主要影响因素、未满足条件、可改进项
 *   4. 允许人工修正，但原始计算结果不覆盖，只追加修正记录
 *   5. 统计采纳率与人工调整率，验证模块效果
 *
 * 计算不依赖外部大模型或硬件，全部基于本地库表与可配置系数。
 */
@Service
@RequiredArgsConstructor
public class AdviceService {

    private final RuleConfigMapper ruleMapper;
    private final WaterAdviceMapper adviceMapper;
    private final FarmlandMapper farmlandMapper;
    private final IrrigationTaskMapper taskMapper;
    private final WaterQuotaMapper quotaMapper;
    private final ObjectMapper objectMapper;

    /** 作物基础需水系数（亩均 m³），来自本地农艺经验值，可在规则页调整权重间接影响结果 */
    private static final Map<String, BigDecimal> CROP_BASE = Map.of(
            "水稻", new BigDecimal("24"), "小麦", new BigDecimal("16"),
            "玉米", new BigDecimal("15"), "蔬菜", new BigDecimal("18"),
            "果树", new BigDecimal("14"), "棉花", new BigDecimal("13"));

    /** 生育阶段需水系数，分蘖/孕穗期为需水高峰 */
    private static final Map<String, BigDecimal> STAGE_COEF = Map.of(
            "苗期", new BigDecimal("0.45"), "分蘖期", new BigDecimal("0.95"),
            "拔节期", new BigDecimal("0.85"), "孕穗期", new BigDecimal("1.00"),
            "抽穗期", new BigDecimal("0.88"), "结果期", new BigDecimal("0.80"),
            "果实膨大期", new BigDecimal("0.92"), "成熟期", new BigDecimal("0.30"));

    /** 土壤保水等级：黏土保水最好，砂土最差 */
    private static final Map<String, BigDecimal> SOIL_KEEP = Map.of(
            "黏土", new BigDecimal("0.85"), "壤土", new BigDecimal("0.70"),
            "砂壤土", new BigDecimal("0.55"), "砂土", new BigDecimal("0.40"));

    public List<RuleConfig> rules() {
        return ruleMapper.selectList(new LambdaQueryWrapper<RuleConfig>()
                .orderByDesc(RuleConfig::getId));
    }

    /** 保存规则：权重合计必须 100%，旧版本自动停用，新版本记录生效时间 */
    @Transactional
    public RuleConfig saveRule(String name, int crop, int stage, int area, int soil, int rain, int history) {
        int sum = crop + stage + area + soil + rain + history;
        if (sum != 100) {
            throw new BizException(400, "权重合计必须等于 100%，当前为 " + sum + "%");
        }
        for (int w : new int[]{crop, stage, area, soil, rain, history}) {
            if (w < 0 || w > 100) {
                throw new BizException(400, "单项权重必须在 0–100 之间");
            }
        }
        List<RuleConfig> all = rules();
        int next = all.stream().mapToInt(r -> {
            try {
                return Integer.parseInt(r.getVersion().replace("v", ""));
            } catch (NumberFormatException e) {
                return 0;
            }
        }).max().orElse(0) + 1;
        for (RuleConfig r : all) {
            if ("ACTIVE".equals(r.getStatus())) {
                RuleConfig off = new RuleConfig();
                off.setId(r.getId());
                off.setStatus("DISABLED");
                ruleMapper.updateById(off);
            }
        }
        RuleConfig rc = new RuleConfig();
        rc.setName(name == null || name.isBlank() ? "作物阶段用水建议（v" + next + "）" : name);
        rc.setVersion("v" + next);
        rc.setCropWeight(crop);
        rc.setStageWeight(stage);
        rc.setAreaWeight(area);
        rc.setSoilWeight(soil);
        rc.setRainWeight(rain);
        rc.setHistoryWeight(history);
        rc.setStatus("ACTIVE");
        rc.setEffectiveTime(LocalDateTime.now());
        rc.setCreateBy(UserContext.realName());
        rc.setCreateTime(LocalDateTime.now());
        ruleMapper.insert(rc);
        return rc;
    }

    /**
     * 执行计算并落库留痕。
     * @param rainMm 近期降雨量（人工录入），为空则视为缺失数据
     */
    @Transactional
    public WaterAdvice evaluate(Long farmlandId, Long taskId, BigDecimal rainMm) {
        Farmland f = farmlandMapper.selectById(farmlandId);
        if (f == null) {
            throw new BizException(404, "地块不存在");
        }
        RuleConfig rule = ruleMapper.selectOne(new LambdaQueryWrapper<RuleConfig>()
                .eq(RuleConfig::getStatus, "ACTIVE").orderByDesc(RuleConfig::getId).last("limit 1"));
        if (rule == null) {
            throw new BizException(400, "没有生效中的规则，请先在规则配置页启用一个版本");
        }
        IrrigationTask task = taskId == null ? null : taskMapper.selectById(taskId);
        WaterQuota quota = quotaMapper.selectOne(new LambdaQueryWrapper<WaterQuota>()
                .eq(WaterQuota::getFarmlandId, farmlandId).eq(WaterQuota::getQuotaYear, 2026).last("limit 1"));

        BigDecimal cropScore = CROP_BASE.getOrDefault(f.getCrop(), BigDecimal.ZERO).multiply(BigDecimal.valueOf(4))
                .min(BigDecimal.valueOf(100));
        BigDecimal stageScore = STAGE_COEF.getOrDefault(f.getGrowthStage(), BigDecimal.ZERO)
                .multiply(BigDecimal.valueOf(100));
        BigDecimal areaScore = f.getArea().multiply(BigDecimal.valueOf(11)).min(BigDecimal.valueOf(100));
        BigDecimal soilScore = SOIL_KEEP.getOrDefault(f.getSoilType(), BigDecimal.ZERO)
                .multiply(BigDecimal.valueOf(100));
        // 降雨越多，建议补水量越小；无降雨记录则该项记 0 并在解释中提示补录
        BigDecimal rainScore = rainMm == null ? BigDecimal.ZERO
                : BigDecimal.valueOf(100).subtract(rainMm.multiply(BigDecimal.valueOf(3.2)))
                    .max(BigDecimal.ZERO).min(BigDecimal.valueOf(100));
        BigDecimal histBase = quota != null && f.getArea().compareTo(BigDecimal.ZERO) > 0
                ? quota.getUsedVolume().divide(f.getArea(), 2, RoundingMode.HALF_UP)
                : BigDecimal.ZERO;
        BigDecimal historyScore = histBase.multiply(BigDecimal.valueOf(2.2)).min(BigDecimal.valueOf(100));

        BigDecimal total = cropScore.multiply(BigDecimal.valueOf(rule.getCropWeight()))
                .add(stageScore.multiply(BigDecimal.valueOf(rule.getStageWeight())))
                .add(areaScore.multiply(BigDecimal.valueOf(rule.getAreaWeight())))
                .add(soilScore.multiply(BigDecimal.valueOf(rule.getSoilWeight())))
                .add(rainScore.multiply(BigDecimal.valueOf(rule.getRainWeight())))
                .add(historyScore.multiply(BigDecimal.valueOf(rule.getHistoryWeight())))
                .divide(BigDecimal.valueOf(100), 2, RoundingMode.HALF_UP);

        BigDecimal cropBase = CROP_BASE.getOrDefault(f.getCrop(), new BigDecimal("15"));
        BigDecimal suggest = f.getArea().multiply(cropBase)
                .multiply(total.divide(BigDecimal.valueOf(70), 4, RoundingMode.HALF_UP))
                .setScale(2, RoundingMode.HALF_UP);
        BigDecimal compare = task != null ? task.getPlanVolume()
                : (quota == null ? suggest : quota.getQuotaVolume());
        BigDecimal deviation = compare.compareTo(BigDecimal.ZERO) == 0 ? BigDecimal.ZERO
                : suggest.subtract(compare).multiply(BigDecimal.valueOf(100))
                    .divide(compare, 2, RoundingMode.HALF_UP);

        String grade;
        String missing;
        String improve;
        if (rainMm == null || f.getCrop() == null || f.getGrowthStage() == null) {
            grade = "INSUFFICIENT";
            missing = "近期降雨量未录入，或作物/生育阶段缺失，建议结果仅供参考";
            improve = "补录近 7 天降雨量后重新计算，可提升结果可靠性";
        } else if (deviation.abs().compareTo(BigDecimal.valueOf(10)) <= 0) {
            grade = "RECOMMEND";
            missing = "土壤保水等级为" + f.getSoilType() + "，蒸发损失高于黏土地块";
            improve = "建议改为傍晚时段灌溉，可减少约 6% 蒸发损失";
        } else if (deviation.abs().compareTo(BigDecimal.valueOf(20)) <= 0) {
            grade = "REVIEW";
            missing = "近 7 天降雨 " + rainMm + " mm，已按权重折减";
            improve = "渠道末段水头不足时，建议分两次短时段灌溉";
        } else {
            grade = "DEVIATE";
            missing = "当前计划水量与建议值偏差 " + deviation + "%，需现场核实作物长势";
            improve = "核对地块面积与土壤类型是否更新，必要时调整定额分配";
        }

        String main = String.format("作物%s（权重%d%%）与%s（权重%d%%）合计占 %d%%，是结果的主要影响因素",
                f.getCrop(), rule.getCropWeight(), f.getGrowthStage(), rule.getStageWeight(),
                rule.getCropWeight() + rule.getStageWeight());

        WaterAdvice a = new WaterAdvice();
        a.setTaskId(taskId);
        a.setFarmlandId(farmlandId);
        a.setRuleId(rule.getId());
        a.setRuleVersion(rule.getVersion());
        a.setSnapshot(snapshot(f, rainMm, histBase, rule));
        a.setCropScore(cropScore);
        a.setStageScore(stageScore);
        a.setAreaScore(areaScore);
        a.setSoilScore(soilScore);
        a.setRainScore(rainScore);
        a.setHistoryScore(historyScore);
        a.setTotalScore(total);
        a.setSuggestVolume(suggest);
        a.setQuotaVolume(compare);
        a.setDeviation(deviation);
        a.setGrade(grade);
        a.setExplainMain(main);
        a.setExplainMissing(missing);
        a.setExplainImprove(improve);
        a.setCreateTime(LocalDateTime.now());
        adviceMapper.insert(a);
        return a;
    }

    private String snapshot(Farmland f, BigDecimal rain, BigDecimal hist, RuleConfig r) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("crop", f.getCrop());
        m.put("growthStage", f.getGrowthStage());
        m.put("area", f.getArea());
        m.put("soilType", f.getSoilType());
        m.put("rainMm", rain);
        m.put("historyPerMu", hist);
        m.put("ruleVersion", r.getVersion());
        m.put("weights", Map.of("crop", r.getCropWeight(), "stage", r.getStageWeight(),
                "area", r.getAreaWeight(), "soil", r.getSoilWeight(),
                "rain", r.getRainWeight(), "history", r.getHistoryWeight()));
        try {
            return objectMapper.writeValueAsString(m);
        } catch (JsonProcessingException e) {
            return "{}";
        }
    }

    /** 人工修正：只写修正字段，原始 suggestVolume 与各项得分保持不变 */
    @Transactional
    public void adjust(Long id, BigDecimal volume, String reason) {
        WaterAdvice a = adviceMapper.selectById(id);
        if (a == null) {
            throw new BizException(404, "计算记录不存在");
        }
        if (volume == null || volume.compareTo(BigDecimal.ZERO) <= 0) {
            throw new BizException(400, "修正水量必须大于 0");
        }
        if (reason == null || reason.trim().length() < 5) {
            throw new BizException(400, "人工调整原因不少于 5 个字");
        }
        WaterAdvice upd = new WaterAdvice();
        upd.setId(id);
        upd.setAdjustVolume(volume);
        upd.setAdjustReason(reason.trim());
        upd.setAdjustBy(UserContext.realName());
        upd.setAdjustTime(LocalDateTime.now());
        adviceMapper.updateById(upd);
    }

    public PageResult<WaterAdvice> page(String grade, Long farmlandId, long page, long size) {
        LambdaQueryWrapper<WaterAdvice> w = new LambdaQueryWrapper<>();
        w.eq(grade != null && !grade.isBlank(), WaterAdvice::getGrade, grade)
         .eq(farmlandId != null, WaterAdvice::getFarmlandId, farmlandId)
         .orderByDesc(WaterAdvice::getCreateTime);
        Page<WaterAdvice> p = adviceMapper.selectPage(new Page<>(page, size), w);
        return PageResult.of(p.getTotal(), page, size, p.getRecords());
    }

    public Map<String, Object> detail(Long id) {
        WaterAdvice a = adviceMapper.selectById(id);
        if (a == null) {
            throw new BizException(404, "计算记录不存在");
        }
        Farmland f = farmlandMapper.selectById(a.getFarmlandId());
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("advice", a);
        m.put("farmland", f);
        m.put("rule", ruleMapper.selectById(a.getRuleId()));
        return m;
    }

    /** 效果统计：推荐采纳率、人工调整率、各等级分布，用于验证模块是否有效 */
    public Map<String, Object> stats() {
        List<WaterAdvice> all = adviceMapper.selectList(null);
        int total = all.size();
        int adjusted = 0;
        Map<String, Integer> gradeCount = new LinkedHashMap<>();
        BigDecimal sumDev = BigDecimal.ZERO;
        int devCount = 0;
        for (WaterAdvice a : all) {
            if (a.getAdjustVolume() != null) {
                adjusted++;
            }
            gradeCount.merge(a.getGrade(), 1, Integer::sum);
            if (a.getDeviation() != null && a.getDeviation().compareTo(BigDecimal.ZERO) != 0) {
                sumDev = sumDev.add(a.getDeviation().abs());
                devCount++;
            }
        }
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("total", total);
        m.put("adjusted", adjusted);
        m.put("adjustRate", total == 0 ? 0 : Math.round(adjusted * 1000.0 / total) / 10.0);
        m.put("adoptRate", total == 0 ? 0 : Math.round((total - adjusted) * 1000.0 / total) / 10.0);
        m.put("avgDeviation", devCount == 0 ? 0
                : sumDev.divide(BigDecimal.valueOf(devCount), 2, RoundingMode.HALF_UP));
        m.put("gradeCount", gradeCount);
        m.put("activeRule", ruleMapper.selectOne(new LambdaQueryWrapper<RuleConfig>()
                .eq(RuleConfig::getStatus, "ACTIVE").last("limit 1")));
        return m;
    }
}
