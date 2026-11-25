package com.grad.irrig.controller;

import com.grad.irrig.common.PageResult;
import com.grad.irrig.common.R;
import com.grad.irrig.entity.SysDictItem;
import com.grad.irrig.entity.WaterMeter;
import com.grad.irrig.entity.WaterSource;
import com.grad.irrig.service.BaseDataService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/** 水源、渠道、闸口、水表与字典。 */
@RestController
@RequestMapping("/api/base")
@RequiredArgsConstructor
public class BaseDataController {

    private final BaseDataService baseDataService;

    @GetMapping("/source/page")
    public R<PageResult<WaterSource>> sourcePage(@RequestParam(required = false) String keyword,
                                                 @RequestParam(defaultValue = "1") long page,
                                                 @RequestParam(defaultValue = "10") long size) {
        return R.ok(baseDataService.sourcePage(keyword, page, size));
    }

    @PostMapping("/source")
    public R<Void> saveSource(@RequestBody Map<String, Object> body) {
        baseDataService.saveSource(body);
        return R.ok();
    }

    @GetMapping("/canals")
    public R<List<Map<String, Object>>> canals() {
        return R.ok(baseDataService.canals());
    }

    @GetMapping("/gates")
    public R<List<Map<String, Object>>> gates(@RequestParam(required = false) Long canalId) {
        return R.ok(baseDataService.gates(canalId));
    }

    @DeleteMapping("/gate/{id}")
    public R<Void> deleteGate(@PathVariable Long id) {
        baseDataService.deleteGate(id);
        return R.ok();
    }

    @GetMapping("/meter/page")
    public R<PageResult<WaterMeter>> meterPage(@RequestParam(required = false) String keyword,
                                               @RequestParam(defaultValue = "1") long page,
                                               @RequestParam(defaultValue = "10") long size) {
        return R.ok(baseDataService.meterPage(keyword, page, size));
    }

    @GetMapping("/dicts")
    public R<Map<String, List<SysDictItem>>> dicts() {
        return R.ok(baseDataService.dicts());
    }
}
