package com.grad.irrig.controller;

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
