# -*- coding: utf-8 -*-
"""批量生成 Controller：统一返回 R<T>，分页返回 PageResult，业务校验全部下沉到 Service。"""
import pathlib

DIR = pathlib.Path("/Users/xiaoxin/showcase/build/NEW-017/backend/src/main/java/com/grad/irrig/controller")
DIR.mkdir(parents=True, exist_ok=True)

FILES = {}

FILES["AuthController.java"] = '''package com.grad.irrig.controller;

import com.grad.irrig.common.R;
import com.grad.irrig.entity.SysMessage;
import com.grad.irrig.service.AuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/** 登录、注册、当前用户、个人中心与站内消息。 */
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/login")
    public R<Map<String, Object>> login(@RequestBody Map<String, String> body) {
        return R.ok(authService.login(body.get("username"), body.get("password")));
    }

    @PostMapping("/register")
    public R<Void> register(@RequestBody Map<String, String> body) {
        authService.register(body.get("username"), body.get("password"),
                body.get("realName"), body.get("phone"));
        return R.ok();
    }

    @GetMapping("/me")
    public R<Map<String, Object>> me() {
        return R.ok(authService.me());
    }

    @GetMapping("/perms")
    public R<List<String>> perms() {
        return R.ok(authService.perms());
    }

    @PutMapping("/profile")
    public R<Void> profile(@RequestBody Map<String, String> body) {
        authService.updateProfile(body.get("realName"), body.get("phone"), body.get("email"));
        return R.ok();
    }

    @PutMapping("/avatar")
    public R<Void> avatar(@RequestBody Map<String, String> body) {
        authService.updateAvatar(body.get("avatar"));
        return R.ok();
    }

    @PutMapping("/password")
    public R<Void> password(@RequestBody Map<String, String> body) {
        authService.changePassword(body.get("oldPassword"), body.get("newPassword"));
        return R.ok();
    }

    @GetMapping("/messages")
    public R<List<SysMessage>> messages() {
        return R.ok(authService.messages());
    }

    @GetMapping("/messages/unread")
    public R<Long> unread() {
        return R.ok(authService.unreadCount());
    }

    @PutMapping("/messages/{id}/read")
    public R<Void> read(@PathVariable Long id) {
        authService.readMessage(id);
        return R.ok();
    }
}
'''

FILES["FarmlandController.java"] = '''package com.grad.irrig.controller;

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
'''

FILES["QuotaController.java"] = '''package com.grad.irrig.controller;

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
'''

FILES["ApplicationController.java"] = '''package com.grad.irrig.controller;

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
'''

FILES["PlanController.java"] = '''package com.grad.irrig.controller;

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
'''

FILES["TaskController.java"] = '''package com.grad.irrig.controller;

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
'''

FILES["FeeController.java"] = '''package com.grad.irrig.controller;

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
'''

FILES["AdviceController.java"] = '''package com.grad.irrig.controller;

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
'''

FILES["RuleController.java"] = '''package com.grad.irrig.controller;

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
'''

FILES["DashboardController.java"] = '''package com.grad.irrig.controller;

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
'''

FILES["BaseDataController.java"] = '''package com.grad.irrig.controller;

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
'''

FILES["SystemController.java"] = '''package com.grad.irrig.controller;

import com.grad.irrig.common.PageResult;
import com.grad.irrig.common.R;
import com.grad.irrig.entity.SysOperationLog;
import com.grad.irrig.entity.SysOrg;
import com.grad.irrig.entity.SysRole;
import com.grad.irrig.service.SystemService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/** 用户、角色、菜单授权、操作日志。 */
@RestController
@RequestMapping("/api/system")
@RequiredArgsConstructor
public class SystemController {

    private final SystemService systemService;

    @GetMapping("/user/page")
    public R<PageResult<Map<String, Object>>> userPage(@RequestParam(required = false) String keyword,
                                                       @RequestParam(required = false) Long roleId,
                                                       @RequestParam(defaultValue = "1") long page,
                                                       @RequestParam(defaultValue = "10") long size) {
        return R.ok(systemService.userPage(keyword, roleId, page, size));
    }

    @PostMapping("/user")
    public R<Void> saveUser(@RequestBody Map<String, Object> body) {
        systemService.saveUser(body);
        return R.ok();
    }

    @PutMapping("/user/{id}/status")
    public R<Void> toggle(@PathVariable Long id, @RequestParam Integer status) {
        systemService.toggleUser(id, status);
        return R.ok();
    }

    @PutMapping("/user/{id}/password")
    public R<Void> reset(@PathVariable Long id, @RequestBody Map<String, String> body) {
        systemService.resetPassword(id, body.get("password"));
        return R.ok();
    }

    @GetMapping("/roles")
    public R<List<SysRole>> roles() {
        return R.ok(systemService.roles());
    }

    @GetMapping("/orgs")
    public R<List<SysOrg>> orgs() {
        return R.ok(systemService.orgs());
    }

    @GetMapping("/menus")
    public R<List<Map<String, Object>>> menus() {
        return R.ok(systemService.menuTree());
    }

    @GetMapping("/role/{roleId}/menus")
    public R<List<Long>> roleMenus(@PathVariable Long roleId) {
        return R.ok(systemService.roleMenus(roleId));
    }

    @PostMapping("/role/{roleId}/menus")
    public R<Void> assign(@PathVariable Long roleId, @RequestBody Map<String, List<Long>> body) {
        systemService.assignMenus(roleId, body.get("menuIds"));
        return R.ok();
    }

    @GetMapping("/log/page")
    public R<PageResult<SysOperationLog>> logs(@RequestParam(required = false) String bizType,
                                               @RequestParam(defaultValue = "1") long page,
                                               @RequestParam(defaultValue = "10") long size) {
        return R.ok(systemService.logPage(bizType, page, size));
    }
}
'''

FILES["FileController.java"] = '''package com.grad.irrig.controller;

import com.grad.irrig.common.R;
import com.grad.irrig.entity.SysFile;
import com.grad.irrig.service.FileService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

/** 文件上传：返回相对路径，前端直接用于 img/src 与表单字段。 */
@RestController
@RequestMapping("/api/file")
@RequiredArgsConstructor
public class FileController {

    private final FileService fileService;

    @PostMapping("/upload")
    public R<String> upload(@RequestParam("file") MultipartFile file,
                            @RequestParam(required = false) String bizType,
                            @RequestParam(required = false) Long bizId) {
        return R.ok(fileService.upload(file, bizType, bizId));
    }

    @GetMapping("/list")
    public R<List<SysFile>> list(@RequestParam String bizType, @RequestParam Long bizId) {
        return R.ok(fileService.listByBiz(bizType, bizId));
    }
}
'''

for name, content in FILES.items():
    (DIR / name).write_text(content)
print("生成 controller", len(FILES))
