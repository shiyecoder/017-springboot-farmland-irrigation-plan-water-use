package com.grad.irrig.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.grad.irrig.common.BizException;
import com.grad.irrig.common.PageResult;
import com.grad.irrig.entity.*;
import com.grad.irrig.mapper.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.*;

/**
 * 基础台账：水源、干支渠、闸口、水表、字典。
 * 台账是计划编制的前置数据，删除前必须检查是否被渠道/计划引用。
 */
@Service
@RequiredArgsConstructor
public class BaseDataService {

    private final WaterSourceMapper sourceMapper;
    private final CanalMapper canalMapper;
    private final GateMapper gateMapper;
    private final WaterMeterMapper meterMapper;
    private final SysDictItemMapper dictMapper;
    private final IrrigationPlanMapper planMapper;
    private final LogService logService;

    public PageResult<WaterSource> sourcePage(String keyword, long page, long size) {
        LambdaQueryWrapper<WaterSource> w = new LambdaQueryWrapper<>();
        if (keyword != null && !keyword.isBlank()) {
            w.like(WaterSource::getName, keyword.trim()).or().like(WaterSource::getCode, keyword.trim());
        }
        w.orderByAsc(WaterSource::getId);
        Page<WaterSource> p = sourceMapper.selectPage(new Page<>(page, size), w);
        return PageResult.of(p.getTotal(), page, size, p.getRecords());
    }

    @Transactional
    public void saveSource(Map<String, Object> b) {
        WaterSource s = b.get("id") == null ? new WaterSource() : sourceMapper.selectById(Long.valueOf(b.get("id").toString()));
        if (s == null) {
            throw new BizException(404, "水源不存在");
        }
        if (b.get("name") != null) s.setName(b.get("name").toString());
        if (b.get("code") != null) s.setCode(b.get("code").toString());
        if (b.get("sourceType") != null) s.setSourceType(b.get("sourceType").toString());
        if (b.get("designSupply") != null) s.setDesignSupply(new BigDecimal(b.get("designSupply").toString()));
        if (b.get("availableVolume") != null) s.setAvailableVolume(new BigDecimal(b.get("availableVolume").toString()));
        if (b.get("manager") != null) s.setManager(b.get("manager").toString());
        if (b.get("phone") != null) s.setPhone(b.get("phone").toString());
        if (b.get("photo") != null) s.setPhoto(b.get("photo").toString());
        if (b.get("status") != null) s.setStatus(b.get("status").toString());
        if (b.get("remark") != null) s.setRemark(b.get("remark").toString());
        if (s.getId() == null) {
            if (s.getCode() == null || s.getName() == null) {
                throw new BizException(400, "水源编号与名称必填");
            }
            s.setCreateTime(LocalDateTime.now());
            sourceMapper.insert(s);
        } else {
            sourceMapper.updateById(s);
        }
        logService.write("SOURCE", s.getId(), s.getCode(), "维护水源", null, s.getStatus(), null);
    }

    public List<Map<String, Object>> canals() {
        List<Map<String, Object>> out = new ArrayList<>();
        for (Canal c : canalMapper.selectList(new LambdaQueryWrapper<Canal>().orderByAsc(Canal::getId))) {
            WaterSource s = sourceMapper.selectById(c.getSourceId());
            List<Gate> gates = gateMapper.selectList(new LambdaQueryWrapper<Gate>().eq(Gate::getCanalId, c.getId()));
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", c.getId());
            m.put("code", c.getCode());
            m.put("name", c.getName());
            m.put("level", c.getCanalLevel());
            m.put("sourceName", s == null ? "" : s.getName());
            m.put("designFlow", c.getDesignFlow());
            m.put("lengthKm", c.getLengthKm());
            m.put("status", c.getStatus());
            m.put("gateCount", gates.size());
            m.put("gates", gates);
            out.add(m);
        }
        return out;
    }

    public List<Map<String, Object>> gates(Long canalId) {
        LambdaQueryWrapper<Gate> w = new LambdaQueryWrapper<>();
        w.eq(canalId != null, Gate::getCanalId, canalId).orderByAsc(Gate::getId);
        List<Map<String, Object>> out = new ArrayList<>();
        for (Gate g : gateMapper.selectList(w)) {
            Canal c = canalMapper.selectById(g.getCanalId());
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", g.getId());
            m.put("code", g.getCode());
            m.put("name", g.getName());
            m.put("canalId", g.getCanalId());
            m.put("canalName", c == null ? "" : c.getName());
            m.put("designFlow", g.getDesignFlow());
            m.put("openDegree", g.getOpenDegree());
            m.put("status", g.getStatus());
            out.add(m);
        }
        return out;
    }

    public PageResult<WaterMeter> meterPage(String keyword, long page, long size) {
        LambdaQueryWrapper<WaterMeter> w = new LambdaQueryWrapper<>();
        if (keyword != null && !keyword.isBlank()) {
            w.like(WaterMeter::getCode, keyword.trim()).or().like(WaterMeter::getName, keyword.trim());
        }
        w.orderByAsc(WaterMeter::getId);
        Page<WaterMeter> p = meterMapper.selectPage(new Page<>(page, size), w);
        return PageResult.of(p.getTotal(), page, size, p.getRecords());
    }

    @Transactional
    public void deleteGate(Long id) {
        Long used = planMapper.selectCount(new LambdaQueryWrapper<IrrigationPlan>().eq(IrrigationPlan::getGateId, id));
        if (used != null && used > 0) {
            throw new BizException(400, "该闸口已被 " + used + " 条计划使用，不能删除");
        }
        gateMapper.deleteById(id);
    }

    /** 字典项：前端下拉统一从这里取，禁止硬编码未定义值 */
    public Map<String, List<SysDictItem>> dicts() {
        Map<String, List<SysDictItem>> m = new LinkedHashMap<>();
        for (SysDictItem d : dictMapper.selectList(new LambdaQueryWrapper<SysDictItem>()
                .eq(SysDictItem::getStatus, 1).orderByAsc(SysDictItem::getSortNo))) {
            m.computeIfAbsent(d.getDictType(), k -> new ArrayList<>()).add(d);
        }
        return m;
    }
}
