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
import java.time.LocalDateTime;
import java.util.*;

/**
 * 农田地块与水权定额。
 * 数据范围：管理员全部、调度员本部门、放水员/种植户仅本人负责或承包的地块。
 * 定额剩余 = 定额 - 已用，由任务用量确认回写，避免前端自行相减造成口径不一致。
 */
@Service
@RequiredArgsConstructor
public class FarmlandService {

    private final FarmlandMapper farmlandMapper;
    private final WaterQuotaMapper quotaMapper;
    private final IrrigationPlanMapper planMapper;
    private final IrrigationTaskMapper taskMapper;
    private final LogService logService;

    public PageResult<Farmland> page(String keyword, String region, String crop, String growthStage,
                                     String irrigationType, String status, long page, long size) {
        LambdaQueryWrapper<Farmland> w = new LambdaQueryWrapper<>();
        if (keyword != null && !keyword.isBlank()) {
            w.and(q -> q.like(Farmland::getName, keyword.trim()).or().like(Farmland::getCode, keyword.trim()));
        }
        w.eq(region != null && !region.isBlank(), Farmland::getRegion, region)
         .eq(crop != null && !crop.isBlank(), Farmland::getCrop, crop)
         .eq(growthStage != null && !growthStage.isBlank(), Farmland::getGrowthStage, growthStage)
         .eq(irrigationType != null && !irrigationType.isBlank(), Farmland::getIrrigationType, irrigationType)
         .eq(status != null && !status.isBlank(), Farmland::getStatus, status);
        applyScope(w);
        w.orderByDesc(Farmland::getUpdateTime);
        Page<Farmland> p = farmlandMapper.selectPage(new Page<>(page, size), w);
        return PageResult.of(p.getTotal(), page, size, p.getRecords());
    }

    /** 数据范围过滤：SELF 仅本人承包，DEPT 本组织，ALL 不加条件 */
    private void applyScope(LambdaQueryWrapper<Farmland> w) {
        String scope = UserContext.dataScope();
        if ("SELF".equals(scope)) {
            w.eq(Farmland::getOwnerId, UserContext.userId());
        } else if ("DEPT".equals(scope)) {
            w.eq(Farmland::getOrgId, UserContext.orgId());
        }
    }

    /** 详情：基础信息 + 年度定额 + 最近 5 次任务，详情页不重复拼接列表 */
    public Map<String, Object> detail(Long id) {
        Farmland f = farmlandMapper.selectById(id);
        if (f == null) {
            throw new BizException(404, "地块不存在或已删除");
        }
        WaterQuota quota = quotaMapper.selectOne(new LambdaQueryWrapper<WaterQuota>()
                .eq(WaterQuota::getFarmlandId, id).eq(WaterQuota::getQuotaYear, 2026).last("limit 1"));
        List<IrrigationTask> tasks = taskMapper.selectList(new LambdaQueryWrapper<IrrigationTask>()
                .eq(IrrigationTask::getFarmlandId, id).orderByDesc(IrrigationTask::getCreateTime).last("limit 5"));
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("farmland", f);
        m.put("quota", quota);
        m.put("recentTasks", tasks);
        return m;
    }

    @Transactional
    public Long save(Map<String, Object> body) {
        Farmland f = new Farmland();
        String code = str(body.get("code"));
        String name = str(body.get("name"));
        if (code == null || code.isBlank()) {
            throw new BizException(400, "地块编号必填");
        }
        code = code.trim();
        if (code.length() > 50) {
            throw new BizException(400, "地块编号不超过 50 个字符");
        }
        if (name == null || name.isBlank()) {
            throw new BizException(400, "地块名称必填");
        }
        Long dup = farmlandMapper.selectCount(new LambdaQueryWrapper<Farmland>().eq(Farmland::getCode, code));
        if (dup != null && dup > 0) {
            throw new BizException(400, "地块编号 " + code + " 已存在");
        }
        BigDecimal area = dec(body.get("area"));
        if (area == null || area.compareTo(BigDecimal.ZERO) < 0) {
            throw new BizException(400, "面积不能为空且不得为负数");
        }
        String[] dictCheck = {"growthStage", "soilType", "status"};
        for (String key : dictCheck) {
            if (str(body.get(key)) == null) {
                throw new BizException(400, key + " 不能为空");
            }
        }
        f.setCode(code);
        f.setName(name.trim());
        f.setArea(area);
        f.setCrop(str(body.get("crop")));
        f.setGrowthStage(str(body.get("growthStage")));
        f.setSoilType(str(body.get("soilType")));
        f.setIrrigationType(str(body.get("irrigationType")));
        f.setRegion(str(body.get("region")));
        f.setAddress(str(body.get("address")));
        f.setOwnerId(body.get("ownerId") == null ? UserContext.userId() : Long.valueOf(body.get("ownerId").toString()));
        f.setOwnerName(str(body.get("ownerName")));
        f.setOrgId(body.get("orgId") == null ? UserContext.orgId() : Long.valueOf(body.get("orgId").toString()));
        f.setPhoto(str(body.get("photo")));
        f.setStatus(str(body.get("status")));
        f.setDeleted(0);
        f.setVersion(0);
        f.setCreateTime(LocalDateTime.now());
        f.setUpdateTime(LocalDateTime.now());
        farmlandMapper.insert(f);
        logService.write("FARMLAND", f.getId(), code, "新增地块", null, f.getStatus(), null);
        return f.getId();
    }

    @Transactional
    public void update(Long id, Map<String, Object> body) {
        Farmland old = farmlandMapper.selectById(id);
        if (old == null) {
            throw new BizException(404, "地块不存在");
        }
        Object version = body.get("version");
        if (version != null && !version.toString().equals(String.valueOf(old.getVersion()))) {
            throw new BizException(409, "数据已被他人更新，请刷新后重试");
        }
        Farmland f = new Farmland();
        f.setId(id);
        f.setVersion(old.getVersion());
        if (body.get("name") != null) f.setName(str(body.get("name")));
        if (body.get("area") != null) {
            BigDecimal area = dec(body.get("area"));
            if (area == null || area.compareTo(BigDecimal.ZERO) < 0) {
                throw new BizException(400, "面积不得为负数");
            }
            f.setArea(area);
        }
        if (body.get("crop") != null) f.setCrop(str(body.get("crop")));
        if (body.get("growthStage") != null) f.setGrowthStage(str(body.get("growthStage")));
        if (body.get("soilType") != null) f.setSoilType(str(body.get("soilType")));
        if (body.get("irrigationType") != null) f.setIrrigationType(str(body.get("irrigationType")));
        if (body.get("region") != null) f.setRegion(str(body.get("region")));
        if (body.get("address") != null) f.setAddress(str(body.get("address")));
        if (body.get("photo") != null) f.setPhoto(str(body.get("photo")));
        if (body.get("status") != null) f.setStatus(str(body.get("status")));
        f.setUpdateTime(LocalDateTime.now());
        int rows = farmlandMapper.updateById(f);
        if (rows == 0) {
            throw new BizException(409, "数据已被他人更新，请刷新后重试");
        }
        logService.write("FARMLAND", id, old.getCode(), "编辑地块", old.getStatus(), f.getStatus(), null);
    }

    /** 删除前检查是否被计划引用，避免主数据被单据悬挂 */
    @Transactional
    public void delete(Long id) {
        Farmland f = farmlandMapper.selectById(id);
        if (f == null) {
            throw new BizException(404, "地块不存在");
        }
        Long used = planMapper.selectCount(new LambdaQueryWrapper<IrrigationPlan>()
                .eq(IrrigationPlan::getFarmlandId, id));
        if (used != null && used > 0) {
            throw new BizException(400, "该地块已被 " + used + " 条灌溉计划引用，不能删除");
        }
        farmlandMapper.deleteById(id);
        logService.write("FARMLAND", id, f.getCode(), "删除地块", f.getStatus(), null, null);
    }

    /** 筛选下拉选项，全部取自库内真实值，避免前端硬编码与字典不一致 */
    public Map<String, Object> options() {
        List<Farmland> all = farmlandMapper.selectList(null);
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("regions", uniq(all, Farmland::getRegion));
        m.put("crops", uniq(all, Farmland::getCrop));
        m.put("stages", uniq(all, Farmland::getGrowthStage));
        m.put("soils", uniq(all, Farmland::getSoilType));
        m.put("irrigations", uniq(all, Farmland::getIrrigationType));
        return m;
    }

    private List<String> uniq(List<Farmland> all,
                              java.util.function.Function<Farmland, String> getter) {
        return all.stream().map(getter).filter(Objects::nonNull).distinct().sorted().toList();
    }

    // ---------------- 水权定额 ----------------

    public PageResult<Map<String, Object>> quotaPage(Integer year, String status, String keyword, long page, long size) {
        LambdaQueryWrapper<WaterQuota> w = new LambdaQueryWrapper<>();
        w.eq(year != null, WaterQuota::getQuotaYear, year)
         .eq(status != null && !status.isBlank(), WaterQuota::getStatus, status);
        if (keyword != null && !keyword.isBlank()) {
            w.like(WaterQuota::getFarmerName, keyword.trim());
        }
        if ("SELF".equals(UserContext.dataScope())) {
            w.eq(WaterQuota::getFarmerId, UserContext.userId());
        }
        w.orderByDesc(WaterQuota::getQuotaYear).orderByAsc(WaterQuota::getId);
        Page<WaterQuota> p = quotaMapper.selectPage(new Page<>(page, size), w);
        List<Map<String, Object>> rows = new ArrayList<>();
        for (WaterQuota q : p.getRecords()) {
            Farmland f = farmlandMapper.selectById(q.getFarmlandId());
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", q.getId());
            m.put("year", q.getQuotaYear());
            m.put("farmlandId", q.getFarmlandId());
            m.put("farmlandName", f == null ? "" : f.getName());
            m.put("farmlandCode", f == null ? "" : f.getCode());
            m.put("area", f == null ? BigDecimal.ZERO : f.getArea());
            m.put("farmerName", q.getFarmerName());
            m.put("quotaVolume", q.getQuotaVolume());
            m.put("usedVolume", q.getUsedVolume());
            m.put("remainingVolume", q.getRemainingVolume());
            m.put("usageRate", q.getQuotaVolume().compareTo(BigDecimal.ZERO) == 0
                    ? BigDecimal.ZERO
                    : q.getUsedVolume().multiply(BigDecimal.valueOf(100))
                        .divide(q.getQuotaVolume(), 1, java.math.RoundingMode.HALF_UP));
            m.put("status", q.getStatus());
            rows.add(m);
        }
        return PageResult.of(p.getTotal(), page, size, rows);
    }

    /** 取地块当年定额，供申请审核与用水建议复用 */
    public WaterQuota quotaOf(Long farmlandId) {
        return quotaMapper.selectOne(new LambdaQueryWrapper<WaterQuota>()
                .eq(WaterQuota::getFarmlandId, farmlandId)
                .eq(WaterQuota::getQuotaYear, 2026).last("limit 1"));
    }

    /** 按实际用水量重算剩余与状态，任务确认后调用 */
    @Transactional
    public void refreshQuota(Long farmlandId, BigDecimal addVolume) {
        WaterQuota q = quotaMapper.selectOne(new LambdaQueryWrapper<WaterQuota>()
                .eq(WaterQuota::getFarmlandId, farmlandId).eq(WaterQuota::getQuotaYear, 2026).last("limit 1"));
        if (q == null) {
            return;
        }
        BigDecimal used = q.getUsedVolume().add(addVolume);
        BigDecimal remain = q.getQuotaVolume().subtract(used);
        WaterQuota upd = new WaterQuota();
        upd.setId(q.getId());
        upd.setUsedVolume(used);
        upd.setRemainingVolume(remain);
        if (remain.compareTo(BigDecimal.ZERO) < 0) {
            upd.setStatus("OVER");
        } else if (remain.compareTo(q.getQuotaVolume().multiply(BigDecimal.valueOf(0.1))) < 0) {
            upd.setStatus("SHORT");
        } else {
            upd.setStatus("NORMAL");
        }
        upd.setUpdateTime(LocalDateTime.now());
        quotaMapper.updateById(upd);
    }

    @Transactional
    public void assignQuota(Map<String, Object> body) {
        Long farmlandId = body.get("farmlandId") == null ? null : Long.valueOf(body.get("farmlandId").toString());
        BigDecimal volume = dec(body.get("quotaVolume"));
        Integer year = body.get("year") == null ? 2026 : Integer.valueOf(body.get("year").toString());
        if (farmlandId == null || volume == null || volume.compareTo(BigDecimal.ZERO) < 0) {
            throw new BizException(400, "地块与定额水量必填，且水量不得为负");
        }
        Farmland f = farmlandMapper.selectById(farmlandId);
        if (f == null) {
            throw new BizException(404, "地块不存在");
        }
        WaterQuota exists = quotaMapper.selectOne(new LambdaQueryWrapper<WaterQuota>()
                .eq(WaterQuota::getFarmlandId, farmlandId).eq(WaterQuota::getQuotaYear, year).last("limit 1"));
        if (exists == null) {
            WaterQuota q = new WaterQuota();
            q.setQuotaYear(year);
            q.setFarmlandId(farmlandId);
            q.setFarmerId(f.getOwnerId());
            q.setFarmerName(f.getOwnerName());
            q.setQuotaVolume(volume);
            q.setUsedVolume(BigDecimal.ZERO);
            q.setRemainingVolume(volume);
            q.setStatus("NORMAL");
            q.setVersion(0);
            q.setCreateTime(LocalDateTime.now());
            q.setUpdateTime(LocalDateTime.now());
            quotaMapper.insert(q);
        } else {
            WaterQuota upd = new WaterQuota();
            upd.setId(exists.getId());
            upd.setQuotaVolume(volume);
            upd.setRemainingVolume(volume.subtract(exists.getUsedVolume()));
            upd.setStatus(volume.subtract(exists.getUsedVolume()).compareTo(BigDecimal.ZERO) < 0 ? "OVER" : "NORMAL");
            upd.setUpdateTime(LocalDateTime.now());
            quotaMapper.updateById(upd);
        }
        logService.write("QUOTA", farmlandId, f.getCode(), "分配定额", null, String.valueOf(volume), null);
    }

    private String str(Object o) {
        return o == null ? null : o.toString();
    }

    private BigDecimal dec(Object o) {
        if (o == null || o.toString().isBlank()) {
            return null;
        }
        try {
            return new BigDecimal(o.toString());
        } catch (NumberFormatException e) {
            throw new BizException(400, "数值格式不正确：" + o);
        }
    }
}
