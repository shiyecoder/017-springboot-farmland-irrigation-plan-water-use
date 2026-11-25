package com.grad.irrig.controller;

import com.grad.irrig.common.PageResult;
import com.grad.irrig.common.R;
import com.grad.irrig.service.FeeService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/** 费用台账：分段计费结果查询、缴费、月度汇总。 */
@RestController
@RequestMapping("/api/fee")
@RequiredArgsConstructor
public class FeeController {

    private final FeeService feeService;

    @GetMapping("/page")
    public R<PageResult<Map<String, Object>>> page(@RequestParam(required = false) String month,
                                                   @RequestParam(required = false) String status,
                                                   @RequestParam(required = false) String keyword,
                                                   @RequestParam(defaultValue = "1") long page,
                                                   @RequestParam(defaultValue = "10") long size) {
        return R.ok(feeService.page(month, status, keyword, page, size));
    }

    @GetMapping("/summary")
    public R<Map<String, Object>> summary(@RequestParam(required = false) String month) {
        return R.ok(feeService.summary(month));
    }

    @PostMapping("/{id}/pay")
    public R<Void> pay(@PathVariable Long id) {
        feeService.pay(id);
        return R.ok();
    }
}
