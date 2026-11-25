package com.grad.irrig.controller;

import com.grad.irrig.common.PageResult;
import com.grad.irrig.common.R;
import com.grad.irrig.entity.WaterAdvice;
import com.grad.irrig.service.AdviceService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.Map;

/** 创新点：作物阶段用水建议的计算、留痕、人工修正与效果统计。 */
@RestController
@RequestMapping("/api/advice")
@RequiredArgsConstructor
public class AdviceController {

    private final AdviceService adviceService;

    @GetMapping("/page")
    public R<PageResult<WaterAdvice>> page(@RequestParam(required = false) String grade,
                                           @RequestParam(required = false) Long farmlandId,
                                           @RequestParam(defaultValue = "1") long page,
                                           @RequestParam(defaultValue = "10") long size) {
        return R.ok(adviceService.page(grade, farmlandId, page, size));
    }

    @GetMapping("/{id}")
    public R<Map<String, Object>> detail(@PathVariable Long id) {
        return R.ok(adviceService.detail(id));
    }

    /** rainMm 为人工录入的近 7 天降雨量；未传则结果标记为数据不足 */
    @PostMapping("/evaluate")
    public R<WaterAdvice> evaluate(@RequestBody Map<String, Object> body) {
        Long farmlandId = Long.valueOf(body.get("farmlandId").toString());
        Long taskId = body.get("taskId") == null ? null : Long.valueOf(body.get("taskId").toString());
        BigDecimal rain = body.get("rainMm") == null || body.get("rainMm").toString().isBlank()
                ? null : new BigDecimal(body.get("rainMm").toString());
        return R.ok(adviceService.evaluate(farmlandId, taskId, rain));
    }

    @PostMapping("/{id}/adjust")
    public R<Void> adjust(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        adviceService.adjust(id, new BigDecimal(body.get("volume").toString()),
                body.get("reason") == null ? null : body.get("reason").toString());
        return R.ok();
    }

    @GetMapping("/stats")
    public R<Map<String, Object>> stats() {
        return R.ok(adviceService.stats());
    }
}
