package com.grad.irrig.controller;

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
