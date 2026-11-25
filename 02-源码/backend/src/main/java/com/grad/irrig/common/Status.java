package com.grad.irrig.common;

import java.util.List;

/**
 * 业务状态机常量与流转规则。
 *
 * 留样主流程：待复核 → 保留中 → 待销毁 → 已销毁；复核不通过 → 已驳回（需重新留样）。
 * 检测主流程：待检测 → 检测中 → 待复核 → 已合格 / 已不合格；待复检需新增检测记录。
 *
 * 后端强制校验（不依赖前端按钮隐藏）：
 *  1. 实际重量低于标准、仓位被占用、入柜超时，禁止复核通过；
 *  2. 被不合格事件锁定的留样禁止销毁；
 *  3. 已销毁数据不可删除、不可修改；
 *  4. 不合格事件未关闭不得解锁样品。
 */
public final class Status {

    /* ---------- 留样 ---------- */
    public static final String PENDING = "PENDING";                 // 待执行（任务态）
    public static final String PENDING_REVIEW = "PENDING_REVIEW";   // 待复核
    public static final String RETAINING = "RETAINING";             // 保留中（已入柜）
    public static final String PENDING_DISPOSE = "PENDING_DISPOSE"; // 待销毁
    public static final String DISPOSED = "DISPOSED";               // 已销毁
    public static final String REJECTED = "REJECTED";               // 已驳回
    public static final String OVERDUE = "OVERDUE";                 // 任务逾期

    /* ---------- 检测 ---------- */
    public static final String INS_PENDING = "PENDING";             // 待检测
    public static final String INS_TESTING = "TESTING";             // 检测中
    public static final String INS_REVIEW = "PENDING_REVIEW";       // 待复核
    public static final String INS_PASSED = "QUALIFIED";            // 已合格
    public static final String INS_FAILED = "UNQUALIFIED";          // 已不合格
    public static final String INS_RECHECK = "RECHECK";             // 待复检

    /* ---------- 事件 ---------- */
    public static final String INC_HANDLING = "HANDLING";
    public static final String INC_FOLLOWING = "FOLLOWING";
    public static final String INC_CLOSED = "CLOSED";

    private Status() {
    }

    public static String sampleLabel(String code) {
        return switch (code == null ? "" : code) {
            case PENDING -> "待执行";
            case PENDING_REVIEW -> "待复核";
            case RETAINING -> "保留中";
            case PENDING_DISPOSE -> "待销毁";
            case DISPOSED -> "已销毁";
            case REJECTED -> "已驳回";
            case OVERDUE -> "已逾期";
            default -> code;
        };
    }

    public static String inspectLabel(String code) {
        return switch (code == null ? "" : code) {
            case INS_PENDING -> "待检测";
            case INS_TESTING -> "检测中";
            case INS_REVIEW -> "待复核";
            case INS_PASSED -> "已合格";
            case INS_FAILED -> "已不合格";
            case INS_RECHECK -> "待复检";
            default -> code;
        };
    }

    /** 终态：已销毁/已驳回的历史记录不可再接变更 */
    public static boolean isSampleFinal(String status) {
        return DISPOSED.equals(status) || REJECTED.equals(status);
    }

    /** 留样允许的写操作（前端按钮 + 后端接口双重校验） */
    public static boolean canReview(String status) {
        return PENDING_REVIEW.equals(status);
    }

    public static boolean canDispose(String status, Integer locked) {
        return PENDING_DISPOSE.equals(status) && (locked == null || locked == 0);
    }

    public static List<String> sampleStatuses() {
        return List.of(PENDING_REVIEW, RETAINING, PENDING_DISPOSE, DISPOSED, REJECTED);
    }
}
