package com.grad.irrig.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.grad.irrig.common.BizException;
import com.grad.irrig.common.JwtUtil;
import com.grad.irrig.common.UserContext;
import com.grad.irrig.entity.*;
import com.grad.irrig.mapper.*;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * 认证与个人中心。
 * 安全要点：密码只以 BCrypt 存储与比对；连续 5 次失败锁定 10 分钟；任何返回值都不含 password 字段。
 */
@Service
@RequiredArgsConstructor
public class AuthService {

    private final SysUserMapper userMapper;
    private final SysRoleMapper roleMapper;
    private final SysMenuMapper menuMapper;
    private final SysRoleMenuMapper roleMenuMapper;
    private final SysOrgMapper orgMapper;
    private final SysMessageMapper messageMapper;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    private static final int MAX_FAIL = 5;
    private static final int LOCK_MINUTES = 10;

    /**
     * 登录：校验状态 → 校验锁定 → 比对密码 → 记录失败次数 → 签发 JWT。
     * 令牌内固化角色与数据范围，角色调整后需重新登录才生效。
     */
    public Map<String, Object> login(String username, String rawPassword) {
        if (username == null || username.isBlank() || rawPassword == null || rawPassword.isBlank()) {
            throw new BizException(400, "请输入账号与密码");
        }
        SysUser user = userMapper.selectOne(new LambdaQueryWrapper<SysUser>()
                .eq(SysUser::getUsername, username.trim()));
        if (user == null) {
            throw new BizException(400, "账号或密码错误");
        }
        if (user.getStatus() != null && user.getStatus() == 0) {
            throw new BizException(403, "账号已停用，请联系管理员");
        }
        if (user.getLockUntil() != null && user.getLockUntil().isAfter(LocalDateTime.now())) {
            throw new BizException(423, "连续登录失败次数过多，账号已锁定至 " + user.getLockUntil());
        }
        if (!passwordEncoder.matches(rawPassword, user.getPassword())) {
            int fail = (user.getLoginFailCount() == null ? 0 : user.getLoginFailCount()) + 1;
            SysUser upd = new SysUser();
            upd.setId(user.getId());
            upd.setLoginFailCount(fail);
            if (fail >= MAX_FAIL) {
                upd.setLockUntil(LocalDateTime.now().plusMinutes(LOCK_MINUTES));
                upd.setLoginFailCount(0);
            }
            userMapper.updateById(upd);
            throw new BizException(400, fail >= MAX_FAIL
                    ? "连续失败 " + MAX_FAIL + " 次，账号锁定 " + LOCK_MINUTES + " 分钟"
                    : "账号或密码错误，还可尝试 " + (MAX_FAIL - fail) + " 次");
        }

        SysUser ok = new SysUser();
        ok.setId(user.getId());
        ok.setLoginFailCount(0);
        ok.setLockUntil(null);
        ok.setLastLoginTime(LocalDateTime.now());
        userMapper.updateById(ok);

        SysRole role = roleMapper.selectById(user.getRoleId());
        user.setPassword(null);

        UserContext.CurrentUser cu = new UserContext.CurrentUser(
                user.getId(), user.getUsername(), user.getRealName(),
                role == null ? "farmer" : role.getCode(), user.getOrgId(),
                role == null ? "SELF" : role.getDataScope());

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("token", jwtUtil.create(cu));
        result.put("user", profileOf(user));
        result.put("roleName", role == null ? "" : role.getName());
        result.put("menus", menuTree(role == null ? 4L : role.getId()));
        return result;
    }

    /** 种植户自助注册，默认绑定 farmer 角色与北干渠站，数据范围由角色决定 */
    @Transactional
    public void register(String username, String rawPassword, String realName, String phone) {
        if (username == null || username.trim().length() < 3) {
            throw new BizException(400, "账号至少 3 个字符");
        }
        if (rawPassword == null || rawPassword.length() < 6) {
            throw new BizException(400, "密码至少 6 位");
        }
        Long exists = userMapper.selectCount(new LambdaQueryWrapper<SysUser>()
                .eq(SysUser::getUsername, username.trim()));
        if (exists != null && exists > 0) {
            throw new BizException(400, "该账号已被注册");
        }
        SysUser u = new SysUser();
        u.setUsername(username.trim());
        u.setPassword(passwordEncoder.encode(rawPassword));
        u.setRealName(realName == null || realName.isBlank() ? username.trim() : realName.trim());
        u.setPhone(phone);
        u.setAvatar("/uploads/seed/avatar/01.jpg");
        u.setRoleId(4L);
        u.setOrgId(3L);
        u.setStatus(1);
        u.setLoginFailCount(0);
        u.setCreateTime(LocalDateTime.now());
        u.setUpdateTime(LocalDateTime.now());
        userMapper.insert(u);
    }

    public Map<String, Object> me() {
        SysUser user = userMapper.selectById(UserContext.userId());
        if (user == null) {
            throw new BizException(401, "登录状态已失效，请重新登录");
        }
        user.setPassword(null);
        SysRole role = roleMapper.selectById(user.getRoleId());
        SysOrg org = orgMapper.selectById(user.getOrgId());
        Map<String, Object> m = profileOf(user);
        m.put("roleName", role == null ? "" : role.getName());
        m.put("roleCode", role == null ? "" : role.getCode());
        m.put("orgName", org == null ? "" : org.getName());
        m.put("dataScope", role == null ? "SELF" : role.getDataScope());
        m.put("menus", menuTree(user.getRoleId()));
        return m;
    }

    private Map<String, Object> profileOf(SysUser u) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("id", u.getId());
        m.put("username", u.getUsername());
        m.put("realName", u.getRealName());
        m.put("phone", u.getPhone());
        m.put("email", u.getEmail());
        m.put("avatar", u.getAvatar());
        m.put("roleId", u.getRoleId());
        m.put("orgId", u.getOrgId());
        return m;
    }

    /** 按角色查菜单，按钮类（F）不进导航，但保留给前端做按钮级权限判断 */
    public List<Map<String, Object>> menuTree(Long roleId) {
        List<SysRoleMenu> rels = roleMenuMapper.selectList(new LambdaQueryWrapper<SysRoleMenu>()
                .eq(SysRoleMenu::getRoleId, roleId));
        if (rels.isEmpty()) {
            return List.of();
        }
        List<Long> ids = rels.stream().map(SysRoleMenu::getMenuId).toList();
        List<SysMenu> all = menuMapper.selectList(new LambdaQueryWrapper<SysMenu>()
                .in(SysMenu::getId, ids).orderByAsc(SysMenu::getSortNo));
        Map<Long, List<SysMenu>> byParent = all.stream()
                .collect(Collectors.groupingBy(m -> m.getParentId() == null ? 0L : m.getParentId()));
        return build(byParent, 0L);
    }

    private List<Map<String, Object>> build(Map<Long, List<SysMenu>> byParent, Long parentId) {
        List<Map<String, Object>> list = new ArrayList<>();
        for (SysMenu m : byParent.getOrDefault(parentId, List.of())) {
            if ("F".equals(m.getMenuType())) {
                continue;
            }
            Map<String, Object> node = new LinkedHashMap<>();
            node.put("id", m.getId());
            node.put("name", m.getName());
            node.put("path", m.getPath());
            node.put("icon", m.getIcon());
            List<Map<String, Object>> children = build(byParent, m.getId());
            if (!children.isEmpty()) {
                node.put("children", children);
            }
            list.add(node);
        }
        return list;
    }

    /** 当前角色拥有的按钮权限标识，前端据此控制按钮显隐 */
    public List<String> perms() {
        SysUser user = userMapper.selectById(UserContext.userId());
        if (user == null) {
            return List.of();
        }
        List<SysRoleMenu> rels = roleMenuMapper.selectList(new LambdaQueryWrapper<SysRoleMenu>()
                .eq(SysRoleMenu::getRoleId, user.getRoleId()));
        if (rels.isEmpty()) {
            return List.of();
        }
        List<Long> ids = rels.stream().map(SysRoleMenu::getMenuId).toList();
        return menuMapper.selectList(new LambdaQueryWrapper<SysMenu>().in(SysMenu::getId, ids))
                .stream().map(SysMenu::getPerm).filter(Objects::nonNull).toList();
    }

    @Transactional
    public void updateProfile(String realName, String phone, String email) {
        SysUser u = new SysUser();
        u.setId(UserContext.userId());
        u.setRealName(realName);
        u.setPhone(phone);
        u.setEmail(email);
        u.setUpdateTime(LocalDateTime.now());
        userMapper.updateById(u);
    }

    @Transactional
    public void updateAvatar(String avatar) {
        if (avatar == null || avatar.isBlank()) {
            throw new BizException(400, "头像路径不能为空");
        }
        SysUser u = new SysUser();
        u.setId(UserContext.userId());
        u.setAvatar(avatar);
        u.setUpdateTime(LocalDateTime.now());
        userMapper.updateById(u);
    }

    @Transactional
    public void changePassword(String oldPwd, String newPwd) {
        SysUser user = userMapper.selectById(UserContext.userId());
        if (user == null || !passwordEncoder.matches(oldPwd, user.getPassword())) {
            throw new BizException(400, "原密码不正确");
        }
        if (newPwd == null || newPwd.length() < 6) {
            throw new BizException(400, "新密码至少 6 位");
        }
        SysUser u = new SysUser();
        u.setId(user.getId());
        u.setPassword(passwordEncoder.encode(newPwd));
        u.setUpdateTime(LocalDateTime.now());
        userMapper.updateById(u);
    }

    /** 站内消息：只返回本人消息，按时间倒序 */
    public List<SysMessage> messages() {
        return messageMapper.selectList(new LambdaQueryWrapper<SysMessage>()
                .eq(SysMessage::getReceiverId, UserContext.userId())
                .orderByDesc(SysMessage::getCreateTime).last("limit 30"));
    }

    @Transactional
    public void readMessage(Long id) {
        SysMessage m = new SysMessage();
        m.setId(id);
        m.setReadFlag(1);
        messageMapper.updateById(m);
    }

    public long unreadCount() {
        return messageMapper.selectCount(new LambdaQueryWrapper<SysMessage>()
                .eq(SysMessage::getReceiverId, UserContext.userId()).eq(SysMessage::getReadFlag, 0));
    }

    /** 供其他 Service 复用：按角色名查角色 ID */
    public Long roleIdByCode(String code) {
        SysRole r = roleMapper.selectOne(new QueryWrapper<SysRole>().eq("code", code).last("limit 1"));
        return r == null ? null : r.getId();
    }
}
