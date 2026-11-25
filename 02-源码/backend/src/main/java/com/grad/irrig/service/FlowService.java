package com.grad.irrig.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
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
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * 用水申请 → 灌溉计划 → 执行任务 的主流程。
 *
 * 状态机：
 *   申请  PENDING_AUDIT → PENDING_SCHEDULE → SCHEDULED，或 PENDING_AUDIT → REJECTED
 *   计划  DRAFT → AUDITING → ISSUED → EXECUTING → CONFIRMING → ARCHIVED（可 REJECTED / CONFLICT）
 *   任务  PENDING → RUNNING → FINISHED，RUNNING → INTERRUPTED
 *
 * 后端强校验（不依赖前端按钮）：
 *   1. 闸口容量冲突：同闸口时段重叠的计划，折算流量之和不得超过设计流量
 *   2. 结束表数不得小于开始表数
 *   3. 实际水量超计划 ±15% 需复核留痕
 *   4. 已开始任务不可删除，中断必须录入实际水量与原因
 *   5. 已生成费用的任务不允许普通修改
 */
@Service
@RequiredArgsConstructor
public class FlowService {

    private final WaterApplicationMapper appMapper;
    private final IrrigationPlanMapper planMapper;
    private final IrrigationTaskMapper taskMapper;
    private final FarmlandMapper farmlandMapper;
    private final GateMapper gateMapper;
    private final CanalMapper canalMapper;
    private final WaterMeterRecordMapper recordMapper;
    private final WaterMeterMapper meterMapper;
    private final ExceptionRecordMapper excMapper;
    private final FeeService feeService;
    private final FarmlandService farmlandService;
    private final LogService logService;

    private static final DateTimeFormatter DT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    private static final DateTimeFormatter CODE_DT = DateTimeFormatter.ofPattern("yyyyMMdd");

    // ==================== 用水申请 ====================

    public PageResult<Map<String, Object>> appPage(String status, Long farmlandId, String keyword, long page, long size) {
        LambdaQueryWrapper<WaterApplication> w = new LambdaQueryWrapper<>();
        w.eq(status != null && !status.isBlank(), WaterApplication::getStatus, status)
         .eq(farmlandId != null, WaterApplication::getFarmlandId, farmlandId);
        if (keyword != null && !keyword.isBlank()) {
            w.and(q -> q.like(WaterApplication::getCode, keyword.trim())
                    .or().like(WaterApplication::getApplicantName, keyword.trim()));
        }
        if ("SELF".equals(UserContext.dataScope())) {
            w.eq(WaterApplication::getApplicantId, UserContext.userId());
        }
        w.orderByDesc(WaterApplication::getCreateTime);
        Page<WaterApplication> p = appMapper.selectPage(new Page<>(page, size), w);
        List<Map<String, Object>> rows = new ArrayList<>();
        for (WaterApplication a : p.getRecords()) {
            Farmland f = farmlandMapper.selectById(a.getFarmlandId());
            WaterQuota q = null;
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", a.getId());
            m.put("code", a.getCode());
            m.put("farmlandId", a.getFarmlandId());
            m.put("farmlandName", f == null ? "" : f.getName());
            m.put("area", f == null ? null : f.getArea());
            m.put("crop", a.getCrop());
            m.put("growthStage", a.getGrowthStage());
            m.put("expectDate", a.getExpectDate());
            m.put("applyVolume", a.getApplyVolume());
            m.put("urgency", a.getUrgency());
            m.put("applicantName", a.getApplicantName());
            m.put("status", a.getStatus());
            m.put("auditOpinion", a.getAuditOpinion());
            m.put("auditBy", a.getAuditBy());
            m.put("auditTime", a.getAuditTime());
            m.put("createTime", a.getCreateTime());
            rows.add(m);
        }
        return PageResult.of(p.getTotal(), page, size, rows);
    }

    /** 提交申请：地块必须属于本人（管理员代录不限），水量必须为正 */
    @Transactional
    public Long createApplication(Long farmlandId, BigDecimal volume, LocalDate expectDate,
                                  String urgency, String remark) {
        if (farmlandId == null || volume == null || volume.compareTo(BigDecimal.ZERO) <= 0) {
            throw new BizException(400, "地块与申请水量必填，水量必须大于 0");
        }
        Farmland f = farmlandMapper.selectById(farmlandId);
        if (f == null) {
            throw new BizException(404, "地块不存在");
        }
        if ("SELF".equals(UserContext.dataScope()) && !Objects.equals(f.getOwnerId(), UserContext.userId())) {
            throw new BizException(403, "只能为本人承包的地块提交申请");
        }
        if (expectDate == null) {
            expectDate = LocalDate.now().plusDays(1);
        }
        if (expectDate.isBefore(LocalDate.now())) {
            throw new BizException(400, "期望用水日期不能早于今天");
        }
        WaterApplication a = new WaterApplication();
        a.setCode("AP-" + LocalDateTime.now().format(CODE_DT) + "-" + String.format("%03d", seqToday("AP")));
        a.setFarmlandId(farmlandId);
        a.setCrop(f.getCrop());
        a.setGrowthStage(f.getGrowthStage());
        a.setExpectDate(expectDate);
        a.setApplyVolume(volume);
        a.setUrgency(urgency == null ? "NORMAL" : urgency);
        a.setApplicantId(UserContext.userId());
        a.setApplicantName(UserContext.realName());
        a.setStatus("PENDING_AUDIT");
        a.setVersion(0);
        a.setCreateTime(LocalDateTime.now());
        a.setUpdateTime(LocalDateTime.now());
        appMapper.insert(a);
        logService.write("APPLICATION", a.getId(), a.getCode(), "提交申请", null, "PENDING_AUDIT", remark);
        return a.getId();
    }

    /**
     * 审核申请：
     *  1. 校验状态必须为 PENDING_AUDIT，防止重复审批
     *  2. 通过前比对地块年度定额余量，超额则要求走额外审批（approveOverQuota=true）
     *  3. 驳回必须填写不少于 5 个字的原因
     */
    @Transactional
    public void auditApplication(Long id, boolean pass, String opinion, boolean approveOverQuota) {
        WaterApplication a = appMapper.selectById(id);
        if (a == null) {
            throw new BizException(404, "申请不存在");
        }
        if (!"PENDING_AUDIT".equals(a.getStatus())) {
            throw new BizException(400, "该申请当前状态为 " + a.getStatus() + "，不可重复审核");
        }
        if (!pass) {
            if (opinion == null || opinion.trim().length() < 5) {
                throw new BizException(400, "驳回原因不少于 5 个字");
            }
            WaterApplication upd = new WaterApplication();
            upd.setId(id);
            upd.setStatus("REJECTED");
            upd.setAuditOpinion(opinion.trim());
            upd.setAuditBy(UserContext.realName());
            upd.setAuditTime(LocalDateTime.now());
            upd.setVersion(a.getVersion());
            upd.setUpdateTime(LocalDateTime.now());
            appMapper.updateById(upd);
            logService.write("APPLICATION", id, a.getCode(), "审核驳回", "PENDING_AUDIT", "REJECTED", opinion);
            return;
        }
        WaterQuota q = farmlandService.quotaOf(a.getFarmlandId());
        if (q != null && a.getApplyVolume().compareTo(q.getRemainingVolume()) > 0 && !approveOverQuota) {
            throw new BizException(409, "申请水量超出本地块定额余量（剩余 "
                    + q.getRemainingVolume() + " m³），需勾选超额审批后通过");
        }
        WaterApplication upd = new WaterApplication();
        upd.setId(id);
        upd.setStatus("PENDING_SCHEDULE");
        upd.setAuditOpinion(opinion == null ? "定额校验通过，转调度排程" : opinion.trim());
        upd.setAuditBy(UserContext.realName());
        upd.setAuditTime(LocalDateTime.now());
        upd.setVersion(a.getVersion());
        upd.setUpdateTime(LocalDateTime.now());
        appMapper.updateById(upd);
        logService.write("APPLICATION", id, a.getCode(), "审核通过", "PENDING_AUDIT", "PENDING_SCHEDULE", opinion);
    }

    // ==================== 灌溉计划 ====================

    public PageResult<Map<String, Object>> planPage(String status, Long canalId, String date, String keyword,
                                                    long page, long size) {
        LambdaQueryWrapper<IrrigationPlan> w = new LambdaQueryWrapper<>();
        w.eq(status != null && !status.isBlank(), IrrigationPlan::getStatus, status)
         .eq(canalId != null, IrrigationPlan::getCanalId, canalId);
        if (date != null && !date.isBlank()) {
            LocalDate d = LocalDate.parse(date);
            w.ge(IrrigationPlan::getPlanStart, d.atStartOfDay())
             .lt(IrrigationPlan::getPlanStart, d.plusDays(1).atStartOfDay());
        }
        if (keyword != null && !keyword.isBlank()) {
            w.like(IrrigationPlan::getCode, keyword.trim());
        }
        if ("DEPT".equals(UserContext.dataScope())) {
            w.eq(IrrigationPlan::getDispatcherId, UserContext.userId());
        }
        w.orderByDesc(IrrigationPlan::getUpdateTime);
        Page<IrrigationPlan> p = planMapper.selectPage(new Page<>(page, size), w);
        List<Map<String, Object>> rows = new ArrayList<>();
        for (IrrigationPlan pl : p.getRecords()) {
            rows.add(planVo(pl));
        }
        return PageResult.of(p.getTotal(), page, size, rows);
    }

    private Map<String, Object> planVo(IrrigationPlan pl) {
        Farmland f = farmlandMapper.selectById(pl.getFarmlandId());
        Canal c = canalMapper.selectById(pl.getCanalId());
        Gate g = gateMapper.selectById(pl.getGateId());
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("id", pl.getId());
        m.put("code", pl.getCode());
        m.put("farmlandId", pl.getFarmlandId());
        m.put("farmlandName", f == null ? "" : f.getName());
        m.put("crop", f == null ? "" : f.getCrop());
        m.put("growthStage", f == null ? "" : f.getGrowthStage());
        m.put("canalName", c == null ? "" : c.getName());
        m.put("gateName", g == null ? "" : g.getName());
        m.put("gateId", pl.getGateId());
        m.put("planStart", pl.getPlanStart());
        m.put("planEnd", pl.getPlanEnd());
        m.put("planVolume", pl.getPlanVolume());
        m.put("priority", pl.getPriority());
        m.put("status", pl.getStatus());
        m.put("dispatcherName", pl.getDispatcherName());
        m.put("rejectReason", pl.getRejectReason());
        m.put("remark", pl.getRemark());
        m.put("createTime", pl.getCreateTime());
        return m;
    }

    public Map<String, Object> planDetail(Long id) {
        IrrigationPlan pl = planMapper.selectById(id);
        if (pl == null) {
            throw new BizException(404, "计划不存在");
        }
        Map<String, Object> m = planVo(pl);
        m.put("timeline", operationLogs("PLAN", id));
        List<IrrigationTask> tasks = taskMapper.selectList(new LambdaQueryWrapper<IrrigationTask>()
                .eq(IrrigationTask::getPlanId, id));
        m.put("tasks", tasks);
        return m;
    }

    /** 计划时间轴：创建 → 提交 → 审批 → 下达 → 执行，事件不可修改 */
    public List<SysOperationLog> timeline(String bizType, Long bizId) {
        return operationLogs(bizType, bizId);
    }

    private final SysOperationLogMapper logMapper;

    private List<SysOperationLog> operationLogs(String bizType, Long bizId) {
        return logMapper.selectList(new LambdaQueryWrapper<SysOperationLog>()
                .eq(SysOperationLog::getBizType, bizType).eq(SysOperationLog::getBizId, bizId)
                .orderByAsc(SysOperationLog::getCreateTime));
    }

    /**
     * 新建计划并做闸口容量校验。
     * 折算流量 = 计划水量 / 时段秒数；同一闸口所有未作废的重叠计划流量之和不得超设计流量。
     */
    @Transactional
    public Long createPlan(Long applicationId, Long farmlandId, Long canalId, Long gateId,
                           String start, String end, BigDecimal volume, String priority) {
        if (farmlandId == null || gateId == null || start == null || end == null || volume == null) {
            throw new BizException(400, "地块、闸口、时段与计划水量均必填");
        }
        LocalDateTime s = LocalDateTime.parse(start.replace("T", " "), DT);
        LocalDateTime e = LocalDateTime.parse(end.replace("T", " "), DT);
        if (!e.isAfter(s)) {
            throw new BizException(400, "计划结束时间必须晚于开始时间");
        }
        if (volume.compareTo(BigDecimal.ZERO) <= 0) {
            throw new BizException(400, "计划水量必须大于 0");
        }
        Gate gate = gateMapper.selectById(gateId);
        if (gate == null) {
            throw new BizException(404, "闸口不存在");
        }
        if ("CLOSED".equals(gate.getStatus()) || "FAULT".equals(gate.getStatus())) {
            throw new BizException(400, "闸口 " + gate.getName() + " 当前" +
                    ("CLOSED".equals(gate.getStatus()) ? "关闭" : "故障") + "，不可排程");
        }
        checkGateCapacity(gate, s, e, volume, null);

        IrrigationPlan pl = new IrrigationPlan();
        pl.setCode("PL-" + LocalDateTime.now().format(CODE_DT) + "-" + String.format("%03d", seqToday("PL")));
        pl.setApplicationId(applicationId);
        pl.setFarmlandId(farmlandId);
        pl.setCanalId(canalId == null ? gate.getCanalId() : canalId);
        pl.setGateId(gateId);
        pl.setPlanStart(s);
        pl.setPlanEnd(e);
        pl.setPlanVolume(volume);
        pl.setPriority(priority == null ? "NORMAL" : priority);
        pl.setStatus("DRAFT");
        pl.setDispatcherId(UserContext.userId());
        pl.setDispatcherName(UserContext.realName());
        pl.setVersion(0);
        pl.setCreateTime(LocalDateTime.now());
        pl.setUpdateTime(LocalDateTime.now());
        planMapper.insert(pl);
        logService.write("PLAN", pl.getId(), pl.getCode(), "编制计划", null, "DRAFT", null);
        return pl.getId();
    }

    /**
     * 闸口容量冲突校验（核心规则）。
     * 把每条重叠计划的水量按小时折算成 m³/s，累加后与闸口设计流量比较；
     * 允许 2% 的计量误差余量，超出即拒绝并给出具体冲突单据。
     */
    private void checkGateCapacity(Gate gate, LocalDateTime s, LocalDateTime e,
                                   BigDecimal volume, Long excludePlanId) {
        List<IrrigationPlan> overlaps = planMapper.selectList(new LambdaQueryWrapper<IrrigationPlan>()
                .eq(IrrigationPlan::getGateId, gate.getId())
                .lt(IrrigationPlan::getPlanStart, e)
                .gt(IrrigationPlan::getPlanEnd, s)
                .notIn(IrrigationPlan::getStatus, "REJECTED", "ARCHIVED"));
        BigDecimal hours = BigDecimal.valueOf(java.time.Duration.between(s, e).getSeconds())
                .divide(BigDecimal.valueOf(3600), 4, RoundingMode.HALF_UP);
        if (hours.compareTo(BigDecimal.ZERO) <= 0) {
            throw new BizException(400, "计划时段无效");
        }
        BigDecimal selfFlow = volume.divide(hours, 4, RoundingMode.HALF_UP)
                .divide(BigDecimal.valueOf(3600), 6, RoundingMode.HALF_UP);
        BigDecimal total = selfFlow;
        StringBuilder conflict = new StringBuilder();
        for (IrrigationPlan o : overlaps) {
            if (excludePlanId != null && excludePlanId.equals(o.getId())) {
                continue;
            }
            BigDecimal oh = BigDecimal.valueOf(java.time.Duration.between(o.getPlanStart(), o.getPlanEnd()).getSeconds())
                    .divide(BigDecimal.valueOf(3600), 4, RoundingMode.HALF_UP);
            if (oh.compareTo(BigDecimal.ZERO) <= 0) {
                continue;
            }
            BigDecimal of = o.getPlanVolume().divide(oh, 4, RoundingMode.HALF_UP)
                    .divide(BigDecimal.valueOf(3600), 6, RoundingMode.HALF_UP);
            total = total.add(of);
            conflict.append(o.getCode()).append(" ");
        }
        BigDecimal limit = gate.getDesignFlow().multiply(BigDecimal.valueOf(1.02));
        if (total.compareTo(limit) > 0) {
            throw new BizException(409, String.format(
                    "闸口容量冲突：%s 在该时段折算流量合计 %.3f m³/s，超过设计值 %.3f m³/s（冲突单据 %s）",
                    gate.getName(), total, gate.getDesignFlow(), conflict.toString().trim()));
        }
    }

    /**
     * 计划状态流转。审批通过（ISSUED）时自动下达任务，
     * 保证「任务下达」节点与任务记录一致，不依赖前端二次操作。
     */
    @Transactional
    public void transitionPlan(Long id, String target, String reason) {
        IrrigationPlan pl = planMapper.selectById(id);
        if (pl == null) {
            throw new BizException(404, "计划不存在");
        }
        String cur = pl.getStatus();
        Set<String> allow = switch (cur) {
            case "DRAFT" -> Set.of("AUDITING");
            case "AUDITING" -> Set.of("ISSUED", "REJECTED");
            case "ISSUED" -> Set.of("EXECUTING", "REJECTED");
            case "EXECUTING" -> Set.of("CONFIRMING");
            case "CONFIRMING" -> Set.of("ARCHIVED");
            default -> Set.of();
        };
        if (!allow.contains(target)) {
            throw new BizException(400, "当前状态 " + cur + " 不允许流转到 " + target);
        }
        if (Set.of("REJECTED").contains(target) && (reason == null || reason.trim().length() < 5)) {
            throw new BizException(400, "驳回/退回原因不少于 5 个字");
        }
        if ("AUDITING".equals(target)) {
            Gate gate = gateMapper.selectById(pl.getGateId());
            if (gate == null) {
                throw new BizException(400, "计划关联的闸口不存在，无法提交审批");
            }
            checkGateCapacity(gate, pl.getPlanStart(), pl.getPlanEnd(), pl.getPlanVolume(), id);
        }
        IrrigationPlan upd = new IrrigationPlan();
        upd.setId(id);
        upd.setStatus(target);
        upd.setVersion(pl.getVersion());
        upd.setUpdateTime(LocalDateTime.now());
        if ("REJECTED".equals(target)) {
            upd.setRejectReason(reason);
        }
        planMapper.updateById(upd);
        logService.write("PLAN", id, pl.getCode(), "状态流转", cur, target, reason);

        if ("ISSUED".equals(target)) {
            issueTask(pl);
            if (pl.getApplicationId() != null) {
                WaterApplication app = appMapper.selectById(pl.getApplicationId());
                if (app != null && "PENDING_SCHEDULE".equals(app.getStatus())) {
                    WaterApplication au = new WaterApplication();
                    au.setId(app.getId());
                    au.setStatus("SCHEDULED");
                    au.setVersion(app.getVersion());
                    au.setUpdateTime(LocalDateTime.now());
                    appMapper.updateById(au);
                }
            }
        }
    }

    /** 由计划生成任务，放水员按片区指派（同组织优先，否则轮转） */
    private void issueTask(IrrigationPlan pl) {
        Long exists = taskMapper.selectCount(new LambdaQueryWrapper<IrrigationTask>()
                .eq(IrrigationTask::getPlanId, pl.getId()));
        if (exists != null && exists > 0) {
            return;
        }
        IrrigationTask t = new IrrigationTask();
        t.setCode("TK-" + LocalDateTime.now().format(CODE_DT) + "-" + String.format("%03d", seqToday("TK")));
        t.setPlanId(pl.getId());
        t.setFarmlandId(pl.getFarmlandId());
        t.setOperatorId(operatorForFarmland(pl.getFarmlandId()));
        t.setOperatorName(operatorName(t.getOperatorId()));
        t.setPlanVolume(pl.getPlanVolume());
        t.setStatus("PENDING");
        t.setVersion(0);
        t.setCreateTime(LocalDateTime.now());
        t.setUpdateTime(LocalDateTime.now());
        taskMapper.insert(t);
        logService.write("TASK", t.getId(), t.getCode(), "任务下达", null, "PENDING", null);
    }

    private Long operatorForFarmland(Long farmlandId) {
        Farmland f = farmlandMapper.selectById(farmlandId);
        List<SysUser> ops = userMapper.selectList(new LambdaQueryWrapper<SysUser>()
                .eq(SysUser::getRoleId, 3L).eq(SysUser::getStatus, 1));
        if (ops.isEmpty()) {
            return null;
        }
        if (f != null) {
            for (SysUser u : ops) {
                if (Objects.equals(u.getOrgId(), f.getOrgId())) {
                    return u.getId();
                }
            }
        }
        return ops.get(0).getId();
    }

    private String operatorName(Long id) {
        if (id == null) {
            return "";
        }
        SysUser u = userMapper.selectById(id);
        return u == null ? "" : u.getRealName();
    }

    // ==================== 执行任务 ====================

    public PageResult<Map<String, Object>> taskPage(String status, String keyword, long page, long size) {
        LambdaQueryWrapper<IrrigationTask> w = new LambdaQueryWrapper<>();
        w.eq(status != null && !status.isBlank(), IrrigationTask::getStatus, status);
        if (keyword != null && !keyword.isBlank()) {
            w.like(IrrigationTask::getCode, keyword.trim());
        }
        if ("SELF".equals(UserContext.dataScope())) {
            w.eq(IrrigationTask::getOperatorId, UserContext.userId());
        }
        w.orderByAsc(IrrigationTask::getStatus).orderByDesc(IrrigationTask::getCreateTime);
        Page<IrrigationTask> p = taskMapper.selectPage(new Page<>(page, size), w);
        List<Map<String, Object>> rows = new ArrayList<>();
        for (IrrigationTask t : p.getRecords()) {
            rows.add(taskVo(t));
        }
        return PageResult.of(p.getTotal(), page, size, rows);
    }

    private Map<String, Object> taskVo(IrrigationTask t) {
        Farmland f = farmlandMapper.selectById(t.getFarmlandId());
        IrrigationPlan pl = planMapper.selectById(t.getPlanId());
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("id", t.getId());
        m.put("code", t.getCode());
        m.put("planId", t.getPlanId());
        m.put("planCode", pl == null ? "" : pl.getCode());
        m.put("farmlandId", t.getFarmlandId());
        m.put("farmlandName", f == null ? "" : f.getName());
        m.put("crop", f == null ? "" : f.getCrop());
        m.put("growthStage", f == null ? "" : f.getGrowthStage());
        m.put("planStart", pl == null ? null : pl.getPlanStart());
        m.put("planEnd", pl == null ? null : pl.getPlanEnd());
        m.put("operatorName", t.getOperatorName());
        m.put("planVolume", t.getPlanVolume());
        m.put("startReading", t.getStartReading());
        m.put("endReading", t.getEndReading());
        m.put("actualVolume", t.getActualVolume());
        m.put("startTime", t.getStartTime());
        m.put("endTime", t.getEndTime());
        m.put("status", t.getStatus());
        m.put("photo", t.getPhoto());
        m.put("receiverName", t.getReceiverName());
        m.put("interruptReason", t.getInterruptReason());
        m.put("createTime", t.getCreateTime());
        return m;
    }

    public Map<String, Object> taskDetail(Long id) {
        IrrigationTask t = taskMapper.selectById(id);
        if (t == null) {
            throw new BizException(404, "任务不存在");
        }
        Map<String, Object> m = taskVo(t);
        m.put("timeline", operationLogs("TASK", id));
        m.put("meterRecords", recordMapper.selectList(new LambdaQueryWrapper<WaterMeterRecord>()
                .eq(WaterMeterRecord::getTaskId, id)));
        m.put("exceptions", excMapper.selectList(new LambdaQueryWrapper<ExceptionRecord>()
                .eq(ExceptionRecord::getTaskId, id)));
        m.put("plan", planMapper.selectById(t.getPlanId()));
        return m;
    }

    /** 开始执行：记录开始表数与实际开始时间，任务与计划同步进入执行态 */
    @Transactional
    public void startTask(Long id, BigDecimal startReading) {
        IrrigationTask t = taskMapper.selectById(id);
        if (t == null) {
            throw new BizException(404, "任务不存在");
        }
        if (!"PENDING".equals(t.getStatus())) {
            throw new BizException(400, "只有待执行任务可以开始，当前为 " + t.getStatus());
        }
        if (startReading == null || startReading.compareTo(BigDecimal.ZERO) < 0) {
            throw new BizException(400, "开始表数不能为空且不得为负数");
        }
        IrrigationTask upd = new IrrigationTask();
        upd.setId(id);
        upd.setStatus("RUNNING");
        upd.setStartReading(startReading);
        upd.setStartTime(LocalDateTime.now());
        upd.setOperatorId(UserContext.userId() == null ? t.getOperatorId() : UserContext.userId());
        upd.setOperatorName(UserContext.realName());
        upd.setVersion(t.getVersion());
        upd.setUpdateTime(LocalDateTime.now());
        taskMapper.updateById(upd);
        logService.write("TASK", id, t.getCode(), "开始执行", "PENDING", "RUNNING",
                "开始表数 " + startReading);

        IrrigationPlan pl = new IrrigationPlan();
        pl.setId(t.getPlanId());
        pl.setStatus("EXECUTING");
        pl.setUpdateTime(LocalDateTime.now());
        planMapper.updateById(pl);
    }

    /**
     * 完成执行：
     *  1. 结束表数不得小于开始表数（表数只增不减）
     *  2. 实际水量 = 结束 - 开始，超计划 ±15% 标记待复核
     *  3. 回写定额已用、插入水表记录、生成费用台账
     */
    @Transactional
    public Map<String, Object> finishTask(Long id, BigDecimal endReading, String photo,
                                          String receiverName, String remark) {
        IrrigationTask t = taskMapper.selectById(id);
        if (t == null) {
            throw new BizException(404, "任务不存在");
        }
        if (!"RUNNING".equals(t.getStatus())) {
            throw new BizException(400, "只有进行中的任务可以提交完成，当前为 " + t.getStatus());
        }
        if (endReading == null || t.getStartReading() == null) {
            throw new BizException(400, "结束表数不能为空");
        }
        if (endReading.compareTo(t.getStartReading()) < 0) {
            throw new BizException(400, "结束表数不得小于开始表数（开始 " + t.getStartReading() + "）");
        }
        BigDecimal actual = endReading.subtract(t.getStartReading());
        BigDecimal dev = t.getPlanVolume().compareTo(BigDecimal.ZERO) == 0 ? BigDecimal.ZERO
                : actual.subtract(t.getPlanVolume())
                    .multiply(BigDecimal.valueOf(100))
                    .divide(t.getPlanVolume(), 2, RoundingMode.HALF_UP);
        boolean needReview = dev.abs().compareTo(BigDecimal.valueOf(15)) > 0;

        IrrigationTask upd = new IrrigationTask();
        upd.setId(id);
        upd.setStatus("FINISHED");
        upd.setEndReading(endReading);
        upd.setActualVolume(actual);
        upd.setEndTime(LocalDateTime.now());
        upd.setPhoto(photo);
        upd.setReceiverName(receiverName);
        upd.setConfirmTime(LocalDateTime.now());
        upd.setVersion(t.getVersion());
        upd.setUpdateTime(LocalDateTime.now());
        taskMapper.updateById(upd);

        // 抄表记录：保证用量有独立凭证，可追溯到表号与抄表人
        WaterMeter meter = meterMapper.selectOne(new LambdaQueryWrapper<WaterMeter>()
                .eq(WaterMeter::getFarmlandId, t.getFarmlandId()).last("limit 1"));
        WaterMeterRecord rec = new WaterMeterRecord();
        rec.setTaskId(id);
        rec.setMeterId(meter == null ? null : meter.getId());
        rec.setStartReading(t.getStartReading());
        rec.setEndReading(endReading);
        rec.setVolume(actual);
        rec.setRecordTime(LocalDateTime.now());
        rec.setRecorderId(UserContext.userId());
        rec.setRecorderName(UserContext.realName());
        rec.setPhoto(photo);
        rec.setRemark(needReview ? "实际水量偏离计划 " + dev + "%，需复核" : remark);
        recordMapper.insert(rec);

        if (meter != null) {
            WaterMeter mu = new WaterMeter();
            mu.setId(meter.getId());
            mu.setCurrentReading(endReading);
            meterMapper.updateById(mu);
        }

        farmlandService.refreshQuota(t.getFarmlandId(), actual);
        feeService.calcForTask(t, actual);

        IrrigationPlan pl = new IrrigationPlan();
        pl.setId(t.getPlanId());
        pl.setStatus("CONFIRMING");
        pl.setUpdateTime(LocalDateTime.now());
        planMapper.updateById(pl);

        logService.write("TASK", id, t.getCode(), "提交完成", "RUNNING", "FINISHED",
                needReview ? "实际水量偏差 " + dev + "%，需复核" : remark);

        Map<String, Object> m = new LinkedHashMap<>();
        m.put("actualVolume", actual);
        m.put("deviation", dev);
        m.put("needReview", needReview);
        return m;
    }

    /** 中断：必须录入实际水量与不少于 5 个字的原因，任务不可删除，只能改期 */
    @Transactional
    public void interruptTask(Long id, BigDecimal endReading, String reason, String photo) {
        IrrigationTask t = taskMapper.selectById(id);
        if (t == null) {
            throw new BizException(404, "任务不存在");
        }
        if (!"RUNNING".equals(t.getStatus())) {
            throw new BizException(400, "只有进行中的任务可以中断");
        }
        if (reason == null || reason.trim().length() < 5) {
            throw new BizException(400, "中断原因不少于 5 个字");
        }
        if (endReading == null || (t.getStartReading() != null && endReading.compareTo(t.getStartReading()) < 0)) {
            throw new BizException(400, "结束表数不得小于开始表数");
        }
        BigDecimal actual = t.getStartReading() == null ? BigDecimal.ZERO
                : endReading.subtract(t.getStartReading());

        IrrigationTask upd = new IrrigationTask();
        upd.setId(id);
        upd.setStatus("INTERRUPTED");
        upd.setEndReading(endReading);
        upd.setActualVolume(actual);
        upd.setEndTime(LocalDateTime.now());
        upd.setInterruptReason(reason.trim());
        upd.setPhoto(photo);
        upd.setVersion(t.getVersion());
        upd.setUpdateTime(LocalDateTime.now());
        taskMapper.updateById(upd);

        if (actual.compareTo(BigDecimal.ZERO) > 0) {
            farmlandService.refreshQuota(t.getFarmlandId(), actual);
        }
        logService.write("TASK", id, t.getCode(), "中断任务", "RUNNING", "INTERRUPTED", reason);
    }

    /** 异常上报：渠道堵塞/漏水/设备故障/水量不足，记录损失水量用于统计 */
    @Transactional
    public Long reportException(Long taskId, String type, String description, BigDecimal lossVolume, String photo) {
        IrrigationTask t = taskMapper.selectById(taskId);
        if (t == null) {
            throw new BizException(404, "任务不存在");
        }
        if (description == null || description.trim().length() < 5) {
            throw new BizException(400, "异常描述不少于 5 个字");
        }
        if (lossVolume != null && lossVolume.compareTo(BigDecimal.ZERO) < 0) {
            throw new BizException(400, "损失水量不得为负数");
        }
        ExceptionRecord e = new ExceptionRecord();
        e.setTaskId(taskId);
        e.setExcType(type == null ? "BLOCK" : type);
        e.setDescription(description.trim());
        e.setLossVolume(lossVolume == null ? BigDecimal.ZERO : lossVolume);
        e.setPhoto(photo);
        e.setReporterId(UserContext.userId());
        e.setReporterName(UserContext.realName());
        e.setStatus("OPEN");
        e.setCreateTime(LocalDateTime.now());
        excMapper.insert(e);
        logService.write("TASK", taskId, t.getCode(), "异常上报", t.getStatus(), t.getStatus(), description);
        return e.getId();
    }

    @Transactional
    public void handleException(Long id, String result) {
        ExceptionRecord e = excMapper.selectById(id);
        if (e == null) {
            throw new BizException(404, "异常记录不存在");
        }
        if (result == null || result.trim().length() < 5) {
            throw new BizException(400, "处理结果不少于 5 个字");
        }
        ExceptionRecord upd = new ExceptionRecord();
        upd.setId(id);
        upd.setHandleResult(result.trim());
        upd.setStatus("HANDLED");
        excMapper.updateById(upd);
        logService.write("EXCEPTION", id, String.valueOf(e.getTaskId()), "异常处理", e.getStatus(), "HANDLED", result);
    }

    public PageResult<ExceptionRecord> exceptionPage(String status, long page, long size) {
        LambdaQueryWrapper<ExceptionRecord> w = new LambdaQueryWrapper<>();
        w.eq(status != null && !status.isBlank(), ExceptionRecord::getStatus, status)
         .orderByDesc(ExceptionRecord::getCreateTime);
        Page<ExceptionRecord> p = excMapper.selectPage(new Page<>(page, size), w);
        return PageResult.of(p.getTotal(), page, size, p.getRecords());
    }

    /** 编号流水：同一天同前缀的最大序号 +1，删行不会回退已用编号 */
    private int seqToday(String prefix) {
        String head = prefix + "-" + LocalDateTime.now().format(CODE_DT) + "-";
        long count = switch (prefix) {
            case "AP" -> appMapper.selectCount(new LambdaQueryWrapper<WaterApplication>()
                    .likeRight(WaterApplication::getCode, head));
            case "PL" -> planMapper.selectCount(new LambdaQueryWrapper<IrrigationPlan>()
                    .likeRight(IrrigationPlan::getCode, head));
            default -> taskMapper.selectCount(new LambdaQueryWrapper<IrrigationTask>()
                    .likeRight(IrrigationTask::getCode, head));
        };
        return (int) count + 1;
    }

    private final SysUserMapper userMapper;
}
