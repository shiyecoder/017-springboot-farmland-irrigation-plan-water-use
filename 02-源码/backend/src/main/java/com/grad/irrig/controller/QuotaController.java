package com.grad.irrig.controller;

import com.grad.irrig.common.PageResult;
import com.grad.irrig.common.R;
import com.grad.irrig.service.FarmlandService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/** 水权定额：按年度/地块分配，已用与剩余由任务回写。 */
@RestController
@RequestMapping("/api/quota")
@RequiredArgsConstructor
public class QuotaController {

    private final FarmlandService farmlandService;

    @GetMapping("/page")
    public R<PageResult<Map<String, Object>>> page(@RequestParam(required = false) Integer year,
                                                   @RequestParam(required = false) String status,
                                                   @RequestParam(required = false) String keyword,
                                                   @RequestParam(defaultValue = "1") long page,
                                                   @RequestParam(defaultValue = "10") long size) {
        return R.ok(farmlandService.quotaPage(year, status, keyword, page, size));
    }

    @PostMapping("/assign")
    public R<Void> assign(@RequestBody Map<String, Object> body) {
        farmlandService.assignQuota(body);
        return R.ok();
    }
}
