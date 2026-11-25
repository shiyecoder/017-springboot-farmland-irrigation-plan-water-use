package com.grad.irrig.controller;

import com.grad.irrig.common.R;
import com.grad.irrig.service.DashboardService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/** 农业用水分析看板：6 指标 + 6 图表，后端聚合后一次返回。 */
@RestController
@RequestMapping("/api/dashboard")
@RequiredArgsConstructor
public class DashboardController {

    private final DashboardService dashboardService;

    @GetMapping
    public R<Map<String, Object>> overview(@RequestParam(required = false) Integer days,
                                           @RequestParam(required = false) String range) {
        return R.ok(dashboardService.overview(days, range));
    }
}
