package com.grad.irrig.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.grad.irrig.common.BizException;
import com.grad.irrig.common.PageResult;
import com.grad.irrig.common.UserContext;
import com.grad.irrig.entity.*;
import com.grad.irrig.mapper.*;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;

/**
 * 系统管理：用户、角色、菜单授权、操作日志。
 * 「菜单管理」菜单本身不在导航中展示（隐藏项），仅管理员可通过接口维护。
 */
@Service
@RequiredArgsConstructor
public class SystemService {

    private final SysUserMapper userMapper;
    private final SysRoleMapper roleMapper;
    private final SysMenuMapper menuMapper;
    private final SysRoleMenuMapper roleMenuMapper;
    private final SysOrgMapper orgMapper;
    private final SysOperationLogMapper logMapper;
    private final PasswordEncoder passwordEncoder;

    public PageResult<Map<String, Object>> userPage(String keyword, Long roleId, long page, long size) {
        LambdaQueryWrapper<SysUser> w = new LambdaQueryWrapper<>();
        if (keyword != null && !keyword.isBlank()) {
            w.and(q -> q.like(SysUser::getRealName, keyword.trim()).or().like(SysUser::getUsername, keyword.trim()));
        }
        w.eq(roleId != null, SysUser::getRoleId, roleId).orderByAsc(SysUser::getId);
        Page<SysUser> p = userMapper.selectPage(new Page<>(page, size), w);
        List<Map<String, Object>> rows = new ArrayList<>();
        for (SysUser u : p.getRecords()) {
            SysRole r = roleMapper.selectById(u.getRoleId());
            SysOrg o = orgMapper.selectById(u.getOrgId());
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", u.getId());
            m.put("username", u.getUsername());
            m.put("realName", u.getRealName());
            m.put("phone", u.getPhone());
            m.put("email", u.getEmail());
            m.put("avatar", u.getAvatar());
            m.put("roleId", u.getRoleId());
            m.put("roleName", r == null ? "" : r.getName());
            m.put("orgName", o == null ? "" : o.getName());
            m.put("dataScope", r == null ? "" : r.getDataScope());
            m.put("status", u.getStatus());
            m.put("lastLoginTime", u.getLastLoginTime());
            m.put("createTime", u.getCreateTime());
            rows.add(m);
        }
        return PageResult.of(p.getTotal(), page, size, rows);
    }

    @Transactional
    public void saveUser(Map<String, Object> b) {
        String username = b.get("username") == null ? null : b.get("username").toString().trim();
        String realName = b.get("realName") == null ? null : b.get("realName").toString().trim();
        if (username == null || username.isBlank() || realName == null || realName.isBlank()) {
            throw new BizException(400, "账号与姓名必填");
        }
        SysUser user;
        if (b.get("id") == null) {
            Long dup = userMapper.selectCount(new LambdaQueryWrapper<SysUser>().eq(SysUser::getUsername, username));
            if (dup != null && dup > 0) {
                throw new BizException(400, "账号已存在");
            }
            user = new SysUser();
            user.setUsername(username);
            String pwd = b.get("password") == null ? "123456" : b.get("password").toString();
            user.setPassword(passwordEncoder.encode(pwd));
            user.setLoginFailCount(0);
            user.setCreateTime(LocalDateTime.now());
        } else {
            user = userMapper.selectById(Long.valueOf(b.get("id").toString()));
            if (user == null) {
                throw new BizException(404, "用户不存在");
            }
            user.setPassword(null);
        }
        user.setRealName(realName);
        user.setPhone(b.get("phone") == null ? null : b.get("phone").toString());
        user.setEmail(b.get("email") == null ? null : b.get("email").toString());
        user.setRoleId(b.get("roleId") == null ? 4L : Long.valueOf(b.get("roleId").toString()));
        user.setOrgId(b.get("orgId") == null ? 3L : Long.valueOf(b.get("orgId").toString()));
        user.setStatus(b.get("status") == null ? 1 : Integer.valueOf(b.get("status").toString()));
        user.setUpdateTime(LocalDateTime.now());
        if (user.getId() == null) {
            userMapper.insert(user);
        } else {
            userMapper.updateById(user);
        }
    }

    @Transactional
    public void toggleUser(Long id, Integer status) {
        if (Objects.equals(id, UserContext.userId())) {
            throw new BizException(400, "不能停用当前登录账号");
        }
        SysUser u = new SysUser();
        u.setId(id);
        u.setStatus(status);
        u.setUpdateTime(LocalDateTime.now());
        userMapper.updateById(u);
    }

    @Transactional
    public void resetPassword(Long id, String pwd) {
        if (pwd == null || pwd.length() < 6) {
            throw new BizException(400, "新密码至少 6 位");
        }
        SysUser u = new SysUser();
        u.setId(id);
        u.setPassword(passwordEncoder.encode(pwd));
        u.setLoginFailCount(0);
        u.setLockUntil(null);
        u.setUpdateTime(LocalDateTime.now());
        userMapper.updateById(u);
    }

    public List<SysRole> roles() {
        return roleMapper.selectList(new LambdaQueryWrapper<SysRole>().orderByAsc(SysRole::getId));
    }

    public List<SysOrg> orgs() {
        return orgMapper.selectList(new LambdaQueryWrapper<SysOrg>().orderByAsc(SysOrg::getId));
    }

    /** 全量菜单（含按钮），供角色授权树使用；菜单管理项对非管理员隐藏 */
    public List<Map<String, Object>> menuTree() {
        List<SysMenu> all = menuMapper.selectList(new LambdaQueryWrapper<SysMenu>().orderByAsc(SysMenu::getSortNo));
        Map<Long, List<SysMenu>> byParent = new HashMap<>();
        for (SysMenu m : all) {
            byParent.computeIfAbsent(m.getParentId() == null ? 0L : m.getParentId(), k -> new ArrayList<>()).add(m);
        }
        return build(byParent, 0L);
    }

    private List<Map<String, Object>> build(Map<Long, List<SysMenu>> byParent, Long pid) {
        List<Map<String, Object>> list = new ArrayList<>();
        for (SysMenu m : byParent.getOrDefault(pid, List.of())) {
            Map<String, Object> node = new LinkedHashMap<>();
            node.put("id", m.getId());
            node.put("name", m.getName());
            node.put("menuType", m.getMenuType());
            node.put("perm", m.getPerm());
            List<Map<String, Object>> children = build(byParent, m.getId());
            if (!children.isEmpty()) {
                node.put("children", children);
            }
            list.add(node);
        }
        return list;
    }

    public List<Long> roleMenus(Long roleId) {
        return roleMenuMapper.selectList(new LambdaQueryWrapper<SysRoleMenu>()
                        .eq(SysRoleMenu::getRoleId, roleId))
                .stream().map(SysRoleMenu::getMenuId).toList();
    }

    /** 为角色分配菜单：先清后插，保证与提交结果完全一致 */
    @Transactional
    public void assignMenus(Long roleId, List<Long> menuIds) {
        if (roleId == null) {
            throw new BizException(400, "请选择角色");
        }
        roleMenuMapper.delete(new LambdaQueryWrapper<SysRoleMenu>().eq(SysRoleMenu::getRoleId, roleId));
        if (menuIds != null) {
            for (Long mid : menuIds) {
                SysRoleMenu rm = new SysRoleMenu();
                rm.setRoleId(roleId);
                rm.setMenuId(mid);
                roleMenuMapper.insert(rm);
            }
        }
    }

    public PageResult<SysOperationLog> logPage(String bizType, long page, long size) {
        LambdaQueryWrapper<SysOperationLog> w = new LambdaQueryWrapper<>();
        w.eq(bizType != null && !bizType.isBlank(), SysOperationLog::getBizType, bizType)
         .orderByDesc(SysOperationLog::getCreateTime);
        Page<SysOperationLog> p = logMapper.selectPage(new Page<>(page, size), w);
        return PageResult.of(p.getTotal(), page, size, p.getRecords());
    }
}
