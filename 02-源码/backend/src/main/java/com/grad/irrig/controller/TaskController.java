package com.grad.irrig.controller;

import com.grad.irrig.common.PageResult;
import com.grad.irrig.common.R;
import com.grad.irrig.entity.ExceptionRecord;
import com.grad.irrig.service.FlowService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.Map;

/** 执行任务：开始、完成、中断、异常上报，以及抄表记录。 */
@RestController
@RequestMapping("/api/task")
@RequiredArgsConstructor
public class TaskController {

    private final FlowService flowService;

    @GetMapping("/page")
    public R<PageResult<Map<String, Object>>> page(@RequestParam(required = false) String status,
                                                   @RequestParam(required = false) String keyword,
                                                   @RequestParam(defaultValue = "1") long page,
                                                   @RequestParam(defaultValue = "10") long size) {
        return R.ok(flowService.taskPage(status, keyword, page, size));
    }

    @GetMapping("/{id}")
    public R<Map<String, Object>> detail(@PathVariable Long id) {
        return R.ok(flowService.taskDetail(id));
    }

    @PostMapping("/{id}/start")
    public R<Void> start(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        flowService.startTask(id, new BigDecimal(body.get("startReading").toString()));
        return R.ok();
    }

    @PostMapping("/{id}/finish")
    public R<Map<String, Object>> finish(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        return R.ok(flowService.finishTask(id, new BigDecimal(body.get("endReading").toString()),
                body.get("photo") == null ? null : body.get("photo").toString(),
                body.get("receiverName") == null ? null : body.get("receiverName").toString(),
                body.get("remark") == null ? null : body.get("remark").toString()));
    }

    @PostMapping("/{id}/interrupt")
    public R<Void> interrupt(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        flowService.interruptTask(id, new BigDecimal(body.get("endReading").toString()),
                body.get("reason") == null ? null : body.get("reason").toString(),
                body.get("photo") == null ? null : body.get("photo").toString());
        return R.ok();
    }

    @PostMapping("/{id}/exception")
    public R<Long> exception(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        return R.ok(flowService.reportException(id,
                body.get("excType") == null ? "BLOCK" : body.get("excType").toString(),
                body.get("description") == null ? null : body.get("description").toString(),
                body.get("lossVolume") == null ? BigDecimal.ZERO : new BigDecimal(body.get("lossVolume").toString()),
                body.get("photo") == null ? null : body.get("photo").toString()));
    }

    @GetMapping("/exception/page")
    public R<PageResult<ExceptionRecord>> exceptionPage(@RequestParam(required = false) String status,
                                                        @RequestParam(defaultValue = "1") long page,
                                                        @RequestParam(defaultValue = "10") long size) {
        return R.ok(flowService.exceptionPage(status, page, size));
    }

    @PostMapping("/exception/{id}/handle")
    public R<Void> handle(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        flowService.handleException(id, body.get("handleResult") == null ? null
                : body.get("handleResult").toString());
        return R.ok();
    }
}
