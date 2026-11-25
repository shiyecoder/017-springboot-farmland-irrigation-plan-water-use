package com.grad.irrig.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.grad.irrig.common.BizException;
import com.grad.irrig.common.PageResult;
import com.grad.irrig.common.UserContext;
import com.grad.irrig.entity.*;
import com.grad.irrig.mapper.*;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * 费用台账：按实际用水量分段计费。
 * 规则：定额内执行基础价，超出定额部分加价；免费定额按亩折算，不参与计费。
 * 已生成费用的任务不允许普通修改，调整需走审批记录（见 FlowService 的状态校验）。
 */
@Service
@RequiredArgsConstructor
public class FeeService {

    private final FeeLedgerMapper feeMapper;
    private final FarmlandMapper farmlandMapper;
    private final IrrigationTaskMapper taskMapper;
    private final WaterQuotaMapper quotaMapper;

    @Value("${app.base-price:0.42}")
    private BigDecimal basePrice;
    @Value("${app.excess-price:0.55}")
    private BigDecimal excessPrice;
    @Value("${app.free-quota-per-mu:30}")
    private BigDecimal freeQuotaPerMu;

    /** 任务完成时调用：按当次实际水量拆分定额内/超额，写入费用台账（幂等，同一任务只生成一条） */
    @Transactional
    public FeeLedger calcForTask(IrrigationTask task, BigDecimal actual) {
        Long exists = feeMapper.selectCount(new LambdaQueryWrapper<FeeLedger>()
                .eq(FeeLedger::getTaskId, task.getId()));
        if (exists != null && exists > 0) {
            return feeMapper.selectOne(new LambdaQueryWrapper<FeeLedger>()
                    .eq(FeeLedger::getTaskId, task.getId()).last("limit 1"));
        }
        Farmland f = farmlandMapper.selectById(task.getFarmlandId());
        WaterQuota q = quotaMapper.selectOne(new LambdaQueryWrapper<WaterQuota>()
                .eq(WaterQuota::getFarmlandId, task.getFarmlandId())
                .eq(WaterQuota::getQuotaYear, 2026).last("limit 1"));

        // 定额内额度取「地块年度剩余定额」与「按亩免费定额」的较大者，避免小地块被过度加价
        BigDecimal freeByMu = f == null ? BigDecimal.ZERO : f.getArea().multiply(freeQuotaPerMu);
        BigDecimal remainQuota = q == null ? BigDecimal.ZERO : q.getRemainingVolume().max(BigDecimal.ZERO);
        BigDecimal baseCap = remainQuota.max(freeByMu);
        BigDecimal baseVol = actual.min(baseCap);
        BigDecimal excess = actual.subtract(baseVol).max(BigDecimal.ZERO);
        BigDecimal amount = baseVol.multiply(basePrice).add(excess.multiply(excessPrice))
                .setScale(2, RoundingMode.HALF_UP);

        FeeLedger fee = new FeeLedger();
        fee.setCode("FE-" + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMM")) + "-"
                + String.format("%04d", (feeMapper.selectCount(null) == null ? 0 : feeMapper.selectCount(null)) + 1));
        fee.setTaskId(task.getId());
        fee.setFarmlandId(task.getFarmlandId());
        fee.setFarmerName(f == null ? "" : f.getOwnerName());
        fee.setActualVolume(actual);
        fee.setBaseVolume(baseVol);
        fee.setExcessVolume(excess);
        fee.setBasePrice(basePrice);
        fee.setExcessPrice(excessPrice);
        fee.setAmount(amount);
        fee.setBillMonth(LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM")));
        fee.setStatus("UNPAID");
        fee.setCreateTime(LocalDateTime.now());
        feeMapper.insert(fee);

        if (excess.compareTo(BigDecimal.ZERO) > 0) {
            log(excess, amount);
        }
        return fee;
    }

    private void log(BigDecimal excess, BigDecimal amount) {
        // 超额加价留痕，便于后续核对与统计
        org.slf4j.LoggerFactory.getLogger(FeeService.class)
                .info("超额计费：超额 {} m³，金额 {} 元", excess, amount);
    }

    public PageResult<Map<String, Object>> page(String month, String status, String keyword, long page, long size) {
        LambdaQueryWrapper<FeeLedger> w = new LambdaQueryWrapper<>();
        w.eq(month != null && !month.isBlank(), FeeLedger::getBillMonth, month)
         .eq(status != null && !status.isBlank(), FeeLedger::getStatus, status);
        if (keyword != null && !keyword.isBlank()) {
            w.and(q -> q.like(FeeLedger::getCode, keyword.trim()).or().like(FeeLedger::getFarmerName, keyword.trim()));
        }
        if ("SELF".equals(UserContext.dataScope())) {
            // 种植户只看本人地块产生的费用
            List<Long> ids = farmlandMapper.selectList(new LambdaQueryWrapper<Farmland>()
                            .eq(Farmland::getOwnerId, UserContext.userId()))
                    .stream().map(Farmland::getId).toList();
            if (ids.isEmpty()) {
                return PageResult.of(0, page, size, List.of());
            }
            w.in(FeeLedger::getFarmlandId, ids);
        }
        w.orderByDesc(FeeLedger::getCreateTime);
        Page<FeeLedger> p = feeMapper.selectPage(new Page<>(page, size), w);
        List<Map<String, Object>> rows = new ArrayList<>();
        for (FeeLedger f : p.getRecords()) {
            Farmland land = farmlandMapper.selectById(f.getFarmlandId());
            IrrigationTask t = taskMapper.selectById(f.getTaskId());
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", f.getId());
            m.put("code", f.getCode());
            m.put("taskCode", t == null ? "" : t.getCode());
            m.put("farmlandName", land == null ? "" : land.getName());
            m.put("farmerName", f.getFarmerName());
            m.put("actualVolume", f.getActualVolume());
            m.put("baseVolume", f.getBaseVolume());
            m.put("excessVolume", f.getExcessVolume());
            m.put("basePrice", f.getBasePrice());
            m.put("excessPrice", f.getExcessPrice());
            m.put("amount", f.getAmount());
            m.put("billMonth", f.getBillMonth());
            m.put("status", f.getStatus());
            m.put("createTime", f.getCreateTime());
            rows.add(m);
        }
        return PageResult.of(p.getTotal(), page, size, rows);
    }

    @Transactional
    public void pay(Long id) {
        FeeLedger f = feeMapper.selectById(id);
        if (f == null) {
            throw new BizException(404, "费用单不存在");
        }
        if (!"UNPAID".equals(f.getStatus())) {
            throw new BizException(400, "该费用单当前状态为 " + f.getStatus() + "，无需重复缴费");
        }
        FeeLedger upd = new FeeLedger();
        upd.setId(id);
        upd.setStatus("PAID");
        upd.setPayTime(LocalDateTime.now());
        feeMapper.updateById(upd);
    }

    /** 汇总：本月应收、已收、超额加价金额，供看板与台账头部使用 */
    public Map<String, Object> summary(String month) {
        LambdaQueryWrapper<FeeLedger> w = new LambdaQueryWrapper<>();
        if (month != null && !month.isBlank()) {
            w.eq(FeeLedger::getBillMonth, month);
        }
        List<FeeLedger> all = feeMapper.selectList(w);
        BigDecimal total = BigDecimal.ZERO, paid = BigDecimal.ZERO, excessAmount = BigDecimal.ZERO;
        for (FeeLedger f : all) {
            total = total.add(f.getAmount());
            if ("PAID".equals(f.getStatus())) {
                paid = paid.add(f.getAmount());
            }
            excessAmount = excessAmount.add(f.getExcessVolume().multiply(f.getExcessPrice()));
        }
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("totalAmount", total.setScale(2, RoundingMode.HALF_UP));
        m.put("paidAmount", paid.setScale(2, RoundingMode.HALF_UP));
        m.put("unpaidAmount", total.subtract(paid).setScale(2, RoundingMode.HALF_UP));
        m.put("excessAmount", excessAmount.setScale(2, RoundingMode.HALF_UP));
        m.put("count", all.size());
        m.put("basePrice", basePrice);
        m.put("excessPrice", excessPrice);
        return m;
    }
}
