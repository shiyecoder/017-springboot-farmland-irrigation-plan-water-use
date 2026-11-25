package com.grad.irrig.controller;

import com.grad.irrig.common.PageResult;
import com.grad.irrig.common.R;
import com.grad.irrig.service.FlowService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.Map;

/** 用水申请：提交、审核（通过/驳回）、列表。 */
@RestController
@RequestMapping("/api/application")
@RequiredArgsConstructor
public class ApplicationController {

    private final FlowService flowService;

    @GetMapping("/page")
    public R<PageResult<Map<String, Object>>> page(@RequestParam(required = false) String status,
                                                   @RequestParam(required = false) Long farmlandId,
                                                   @RequestParam(required = false) String keyword,
                                                   @RequestParam(defaultValue = "1") long page,
                                                   @RequestParam(defaultValue = "10") long size) {
        return R.ok(flowService.appPage(status, farmlandId, keyword, page, size));
    }

    @PostMapping
    public R<Long> create(@RequestBody Map<String, Object> body) {
        Long farmlandId = Long.valueOf(body.get("farmlandId").toString());
        BigDecimal volume = new BigDecimal(body.get("applyVolume").toString());
        LocalDate expect = body.get("expectDate") == null || body.get("expectDate").toString().isBlank()
                ? null : LocalDate.parse(body.get("expectDate").toString());
        return R.ok(flowService.createApplication(farmlandId, volume, expect,
                body.get("urgency") == null ? "NORMAL" : body.get("urgency").toString(),
                body.get("remark") == null ? null : body.get("remark").toString()));
    }

    /** 审核：pass=false 时 opinion 为驳回原因，后端强制不少于 5 个字 */
    @PostMapping("/{id}/audit")
    public R<Void> audit(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        boolean pass = Boolean.parseBoolean(String.valueOf(body.getOrDefault("pass", false)));
        boolean over = Boolean.parseBoolean(String.valueOf(body.getOrDefault("approveOverQuota", false)));
        flowService.auditApplication(id, pass,
                body.get("opinion") == null ? null : body.get("opinion").toString(), over);
        return R.ok();
    }
}
