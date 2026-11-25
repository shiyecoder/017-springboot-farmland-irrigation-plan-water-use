package com.grad.irrig.common;

/**
 * 当前登录用户上下文，由 JwtFilter 写入，Controller/Service 只读。
 * dataScope：ALL 全部 / DEPT 本部门 / SELF 仅本人，用于数据范围过滤。
 */
public class UserContext {

    public record CurrentUser(Long userId, String username, String realName, String roleCode,
                              Long orgId, String dataScope) {
    }

    private static final ThreadLocal<CurrentUser> HOLDER = new ThreadLocal<>();

    public static void set(CurrentUser u) { HOLDER.set(u); }

    public static CurrentUser get() { return HOLDER.get(); }

    public static Long userId() {
        CurrentUser u = HOLDER.get();
        return u == null ? null : u.userId();
    }

    public static String realName() {
        CurrentUser u = HOLDER.get();
        return u == null ? "" : u.realName();
    }

    public static String roleCode() {
        CurrentUser u = HOLDER.get();
        return u == null ? "" : u.roleCode();
    }

    public static Long orgId() {
        CurrentUser u = HOLDER.get();
        return u == null ? null : u.orgId();
    }

    public static String dataScope() {
        CurrentUser u = HOLDER.get();
        return u == null ? "SELF" : u.dataScope();
    }

    /** 是否拥有任一指定角色，用于后端接口的粗粒度鉴权 */
    public static boolean hasRole(String... roles) {
        String cur = roleCode();
        for (String r : roles) {
            if (r.equalsIgnoreCase(cur)) return true;
        }
        return false;
    }

    public static void clear() { HOLDER.remove(); }
}
