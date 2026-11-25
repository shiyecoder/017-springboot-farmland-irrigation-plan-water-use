package com.grad.irrig.controller;

import com.grad.irrig.common.R;
import com.grad.irrig.entity.RuleConfig;
import com.grad.irrig.service.AdviceService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/** 用水建议规则配置：权重必须合计 100%，保存即生成新版本。 */
@RestController
@RequestMapping("/api/rule")
@RequiredArgsConstructor
public class RuleController {

    private final AdviceService adviceService;

    @GetMapping("/list")
    public R<List<RuleConfig>> list() {
        return R.ok(adviceService.rules());
    }

    @PostMapping
    public R<RuleConfig> save(@RequestBody Map<String, Object> body) {
        return R.ok(adviceService.saveRule(
                body.get("name") == null ? null : body.get("name").toString(),
                Integer.parseInt(body.getOrDefault("cropWeight", "0").toString()),
                Integer.parseInt(body.getOrDefault("stageWeight", "0").toString()),
                Integer.parseInt(body.getOrDefault("areaWeight", "0").toString()),
                Integer.parseInt(body.getOrDefault("soilWeight", "0").toString()),
                Integer.parseInt(body.getOrDefault("rainWeight", "0").toString()),
                Integer.parseInt(body.getOrDefault("historyWeight", "0").toString())));
    }
}
