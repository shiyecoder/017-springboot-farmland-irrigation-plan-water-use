package com.grad.irrig.controller;

import com.grad.irrig.common.PageResult;
import com.grad.irrig.common.R;
import com.grad.irrig.entity.Farmland;
import com.grad.irrig.service.FarmlandService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/** 农田地块：分页、详情、新增、编辑、删除、筛选选项。 */
@RestController
@RequestMapping("/api/farmland")
@RequiredArgsConstructor
public class FarmlandController {

    private final FarmlandService farmlandService;

    @GetMapping("/page")
    public R<PageResult<Farmland>> page(@RequestParam(required = false) String keyword,
                                        @RequestParam(required = false) String region,
                                        @RequestParam(required = false) String crop,
                                        @RequestParam(required = false) String growthStage,
                                        @RequestParam(required = false) String irrigationType,
                                        @RequestParam(required = false) String status,
                                        @RequestParam(defaultValue = "1") long page,
                                        @RequestParam(defaultValue = "10") long size) {
        return R.ok(farmlandService.page(keyword, region, crop, growthStage, irrigationType, status, page, size));
    }

    @GetMapping("/{id}")
    public R<Map<String, Object>> detail(@PathVariable Long id) {
        return R.ok(farmlandService.detail(id));
    }

    @PostMapping
    public R<Long> save(@RequestBody Map<String, Object> body) {
        return R.ok(farmlandService.save(body));
    }

    @PutMapping("/{id}")
    public R<Void> update(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        farmlandService.update(id, body);
        return R.ok();
    }

    @DeleteMapping("/{id}")
    public R<Void> delete(@PathVariable Long id) {
        farmlandService.delete(id);
        return R.ok();
    }

    @GetMapping("/options")
    public R<Map<String, Object>> options() {
        return R.ok(farmlandService.options());
    }
}
