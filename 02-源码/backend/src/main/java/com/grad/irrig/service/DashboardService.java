package com.grad.irrig.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.grad.irrig.entity.*;
import com.grad.irrig.mapper.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * 农业用水分析看板。
 * 所有指标与图表数据都在后端聚合后返回，前端不做全表二次聚合，
 * 保证看板数字与明细列表口径一致（点击图表可带筛选回到列表）。
 */
@Service
@RequiredArgsConstructor
public class DashboardService {

    private final IrrigationTaskMapper taskMapper;
    private final IrrigationPlanMapper planMapper;
    private final FarmlandMapper farmlandMapper;
    private final FeeLedgerMapper feeMapper;
    private final ExceptionRecordMapper excMapper;
    private final WaterAdviceMapper adviceMapper;
    private final WaterQuotaMapper quotaMapper;
    private final WaterSourceMapper sourceMapper;
    private final CanalMapper canalMapper;
    private final WaterApplicationMapper appMapper;

    public Map<String, Object> overview(Integer days, String range) {
        int span = days == null || days <= 0 ? 30 : days;
        LocalDateTime from = LocalDateTime.now().minusDays(span);
        List<IrrigationTask> tasks = taskMapper.selectList(new LambdaQueryWrapper<IrrigationTask>()
                .ge(IrrigationTask::getCreateTime, from));
        List<IrrigationTask> allFinished = taskMapper.selectList(new LambdaQueryWrapper<IrrigationTask>()
                .eq(IrrigationTask::getStatus, "FINISHED"));

        BigDecimal actual = BigDecimal.ZERO, planVol = BigDecimal.ZERO;
        int finished = 0;
        for (IrrigationTask t : tasks) {
            if (t.getPlanVolume() != null) {
                planVol = planVol.add(t.getPlanVolume());
            }
            if ("FINISHED".equals(t.getStatus()) && t.getActualVolume() != null) {
                actual = actual.add(t.getActualVolume());
                finished++;
            }
        }
        // 亩均用水：按已确认水量 / 涉及地块面积
        Set<Long> landIds = new HashSet<>();
        tasks.stream().filter(t -> t.getFarmlandId() != null).forEach(t -> landIds.add(t.getFarmlandId()));
        BigDecimal areaSum = BigDecimal.ZERO;
        for (Long id : landIds) {
            Farmland f = farmlandMapper.selectById(id);
            if (f != null && f.getArea() != null) {
                areaSum = areaSum.add(f.getArea());
            }
        }
        BigDecimal perMu = areaSum.compareTo(BigDecimal.ZERO) == 0 ? BigDecimal.ZERO
                : actual.divide(areaSum, 1, RoundingMode.HALF_UP);

        // 定额偏差：全部地块「已用 - 定额」的合计占比
        List<WaterQuota> quotas = quotaMapper.selectList(null);
        BigDecimal quotaSum = BigDecimal.ZERO, usedSum = BigDecimal.ZERO;
        for (WaterQuota q : quotas) {
            quotaSum = quotaSum.add(q.getQuotaVolume());
            usedSum = usedSum.add(q.getUsedVolume());
        }
        BigDecimal quotaDev = quotaSum.compareTo(BigDecimal.ZERO) == 0 ? BigDecimal.ZERO
                : usedSum.subtract(quotaSum).multiply(BigDecimal.valueOf(100))
                    .divide(quotaSum, 1, RoundingMode.HALF_UP);

        List<ExceptionRecord> excs = excMapper.selectList(new LambdaQueryWrapper<ExceptionRecord>()
                .ge(ExceptionRecord::getCreateTime, from));
        BigDecimal loss = BigDecimal.ZERO;
        for (ExceptionRecord e : excs) {
            loss = loss.add(e.getLossVolume() == null ? BigDecimal.ZERO : e.getLossVolume());
        }
        long openExc = excs.stream().filter(e -> "OPEN".equals(e.getStatus())).count();

        long taskTotal = tasks.size();
        double finishRate = taskTotal == 0 ? 0
                : Math.round(finished * 1000.0 / taskTotal) / 10.0;

        Map<String, Object> m = new LinkedHashMap<>();
        m.put("planVolume", planVol);
        m.put("actualVolume", actual);
        m.put("quotaDeviation", quotaDev);
        m.put("finishRate", finishRate);
        m.put("perMu", perMu);
        m.put("lossVolume", loss);
        m.put("openException", openExc);
        m.put("range", range == null ? "30d" : range);
        m.put("days", span);

        m.put("trend", trend(span));
        m.put("statusDist", statusDist());
        m.put("cropDist", cropDist());
        m.put("gateLoad", gateLoad());
        m.put("topLand", topLand());
        m.put("adviceDist", adviceDist());
        m.put("sourceSupply", sourceSupply());
        m.put("counts", counts());
        return m;
    }

    /** 近 N 天实际用水趋势，按日聚合，缺失日期补 0 */
    private List<Map<String, Object>> trend(int span) {
        LocalDateTime from = LocalDateTime.now().minusDays(span).toLocalDate().atStartOfDay();
        List<IrrigationTask> list = taskMapper.selectList(new LambdaQueryWrapper<IrrigationTask>()
                .eq(IrrigationTask::getStatus, "FINISHED").ge(IrrigationTask::getEndTime, from));
        Map<String, BigDecimal> byDay = new TreeMap<>();
        for (int i = span - 1; i >= 0; i--) {
            byDay.put(LocalDate.now().minusDays(i).format(DateTimeFormatter.ofPattern("MM-dd")), BigDecimal.ZERO);
        }
        for (IrrigationTask t : list) {
            if (t.getEndTime() == null) {
                continue;
            }
            String k = t.getEndTime().format(DateTimeFormatter.ofPattern("MM-dd"));
            byDay.merge(k, t.getActualVolume() == null ? BigDecimal.ZERO : t.getActualVolume(), BigDecimal::add);
        }
        List<Map<String, Object>> out = new ArrayList<>();
        byDay.forEach((k, v) -> {
            Map<String, Object> row = new LinkedHashMap<>();
            row.put("date", k);
            row.put("volume", v);
            out.add(row);
        });
        return out;
    }

    private List<Map<String, Object>> statusDist() {
        List<IrrigationTask> all = taskMapper.selectList(null);
        Map<String, Integer> c = new LinkedHashMap<>();
        for (IrrigationTask t : all) {
            c.merge(t.getStatus(), 1, Integer::sum);
        }
        List<Map<String, Object>> out = new ArrayList<>();
        c.forEach((k, v) -> {
            Map<String, Object> r = new LinkedHashMap<>();
            r.put("status", k);
            r.put("count", v);
            out.add(r);
        });
        return out;
    }

    /** 作物用水占比：按地块作物归集实际水量 */
    private List<Map<String, Object>> cropDist() {
        Map<Long, String> cropOf = new HashMap<>();
        for (Farmland f : farmlandMapper.selectList(null)) {
            cropOf.put(f.getId(), f.getCrop());
        }
        Map<String, BigDecimal> sum = new LinkedHashMap<>();
        for (IrrigationTask t : taskMapper.selectList(new LambdaQueryWrapper<IrrigationTask>()
                .eq(IrrigationTask::getStatus, "FINISHED"))) {
            String crop = cropOf.getOrDefault(t.getFarmlandId(), "其他");
            sum.merge(crop, t.getActualVolume() == null ? BigDecimal.ZERO : t.getActualVolume(), BigDecimal::add);
        }
        BigDecimal total = sum.values().stream().reduce(BigDecimal.ZERO, BigDecimal::add);
        List<Map<String, Object>> out = new ArrayList<>();
        sum.forEach((k, v) -> {
            Map<String, Object> r = new LinkedHashMap<>();
            r.put("crop", k);
            r.put("volume", v);
            r.put("percent", total.compareTo(BigDecimal.ZERO) == 0 ? 0
                    : v.multiply(BigDecimal.valueOf(100)).divide(total, 1, RoundingMode.HALF_UP));
            out.add(r);
        });
        out.sort((a, b) -> ((BigDecimal) b.get("volume")).compareTo((BigDecimal) a.get("volume")));
        return out;
    }

    /** 渠道时段负荷：按 4 小时时段统计计划水量 */
    private List<Map<String, Object>> gateLoad() {
        List<IrrigationPlan> plans = planMapper.selectList(new LambdaQueryWrapper<IrrigationPlan>()
                .notIn(IrrigationPlan::getStatus, "REJECTED"));
        String[] labels = {"00-04", "04-08", "08-12", "12-16", "16-20", "20-24"};
        BigDecimal[] buckets = new BigDecimal[6];
        Arrays.fill(buckets, BigDecimal.ZERO);
        for (IrrigationPlan p : plans) {
            if (p.getPlanStart() == null || p.getPlanVolume() == null) {
                continue;
            }
            int idx = p.getPlanStart().getHour() / 4;
            idx = Math.min(5, Math.max(0, idx));
            buckets[idx] = buckets[idx].add(p.getPlanVolume());
        }
        List<Map<String, Object>> out = new ArrayList<>();
        for (int i = 0; i < labels.length; i++) {
            Map<String, Object> r = new LinkedHashMap<>();
            r.put("slot", labels[i]);
            r.put("volume", buckets[i]);
            out.add(r);
        }
        return out;
    }

    /** 地块单耗排行：实际水量 / 面积，取前 6 */
    private List<Map<String, Object>> topLand() {
        Map<Long, BigDecimal> volOf = new HashMap<>();
        for (IrrigationTask t : taskMapper.selectList(new LambdaQueryWrapper<IrrigationTask>()
                .eq(IrrigationTask::getStatus, "FINISHED"))) {
            volOf.merge(t.getFarmlandId(), t.getActualVolume() == null ? BigDecimal.ZERO : t.getActualVolume(),
                    BigDecimal::add);
        }
        List<Map<String, Object>> out = new ArrayList<>();
        volOf.forEach((id, v) -> {
            Farmland f = farmlandMapper.selectById(id);
            if (f == null || f.getArea() == null || f.getArea().compareTo(BigDecimal.ZERO) == 0) {
                return;
            }
            Map<String, Object> r = new LinkedHashMap<>();
            r.put("name", f.getName());
            r.put("farmlandId", id);
            r.put("perMu", v.divide(f.getArea(), 1, RoundingMode.HALF_UP));
            out.add(r);
        });
        out.sort((a, b) -> ((BigDecimal) b.get("perMu")).compareTo((BigDecimal) a.get("perMu")));
        return out.size() > 6 ? out.subList(0, 6) : out;
    }

    private List<Map<String, Object>> adviceDist() {
        Map<String, Integer> c = new LinkedHashMap<>();
        for (WaterAdvice a : adviceMapper.selectList(null)) {
            c.merge(a.getGrade(), 1, Integer::sum);
        }
        List<Map<String, Object>> out = new ArrayList<>();
        for (String g : List.of("RECOMMEND", "REVIEW", "DEVIATE", "INSUFFICIENT")) {
            Map<String, Object> r = new LinkedHashMap<>();
            r.put("grade", g);
            r.put("count", c.getOrDefault(g, 0));
            out.add(r);
        }
        return out;
    }

    private List<Map<String, Object>> sourceSupply() {
        List<Map<String, Object>> out = new ArrayList<>();
        for (WaterSource s : sourceMapper.selectList(null)) {
            Map<String, Object> r = new LinkedHashMap<>();
            r.put("name", s.getName());
            r.put("available", s.getAvailableVolume());
            r.put("design", s.getDesignSupply());
            out.add(r);
        }
        return out;
    }

    private Map<String, Object> counts() {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("farmland", farmlandMapper.selectCount(null));
        m.put("application", appMapper.selectCount(null));
        m.put("pendingAudit", appMapper.selectCount(new LambdaQueryWrapper<WaterApplication>()
                .eq(WaterApplication::getStatus, "PENDING_AUDIT")));
        m.put("plan", planMapper.selectCount(null));
        m.put("task", taskMapper.selectCount(null));
        m.put("canal", canalMapper.selectCount(null));
        m.put("fee", feeMapper.selectCount(null));
        m.put("advice", adviceMapper.selectCount(null));
        return m;
    }
}
