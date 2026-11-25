package com.grad.irrig.controller;

import com.grad.irrig.common.PageResult;
import com.grad.irrig.common.R;
import com.grad.irrig.service.FlowService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.Map;

/** 灌溉计划：编制（含闸口容量校验）、审批流转、详情与时间轴。 */
@RestController
@RequestMapping("/api/plan")
@RequiredArgsConstructor
public class PlanController {

    private final FlowService flowService;

    @GetMapping("/page")
    public R<PageResult<Map<String, Object>>> page(@RequestParam(required = false) String status,
                                                   @RequestParam(required = false) Long canalId,
                                                   @RequestParam(required = false) String date,
                                                   @RequestParam(required = false) String keyword,
                                                   @RequestParam(defaultValue = "1") long page,
                                                   @RequestParam(defaultValue = "10") long size) {
        return R.ok(flowService.planPage(status, canalId, date, keyword, page, size));
    }

    @GetMapping("/{id}")
    public R<Map<String, Object>> detail(@PathVariable Long id) {
        return R.ok(flowService.planDetail(id));
    }

    @PostMapping
    public R<Long> create(@RequestBody Map<String, Object> body) {
        Long appId = body.get("applicationId") == null ? null : Long.valueOf(body.get("applicationId").toString());
        Long farmlandId = Long.valueOf(body.get("farmlandId").toString());
        Long canalId = body.get("canalId") == null ? null : Long.valueOf(body.get("canalId").toString());
        Long gateId = Long.valueOf(body.get("gateId").toString());
        BigDecimal volume = new BigDecimal(body.get("planVolume").toString());
        return R.ok(flowService.createPlan(appId, farmlandId, canalId, gateId,
                body.get("planStart").toString(), body.get("planEnd").toString(), volume,
                body.get("priority") == null ? "NORMAL" : body.get("priority").toString()));
    }

    /** 状态流转，target 取 AUDITING/ISSUED/EXECUTING/CONFIRMING/ARCHIVED/REJECTED */
    @PostMapping("/{id}/transition")
    public R<Void> transition(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        flowService.transitionPlan(id, String.valueOf(body.get("target")),
                body.get("reason") == null ? null : body.get("reason").toString());
        return R.ok();
    }
}
