package com.grad.irrig.common;

import lombok.Data;

import java.util.UUID;

/** 统一响应体：code=200 业务成功，其余为业务异常码；requestId 用于前后端对账。 */
@Data
public class R<T> {
    private int code;
    private String message;
    private T data;
    private String requestId;

    public static <T> R<T> ok(T data) {
        R<T> r = new R<>();
        r.code = 200; r.message = "success"; r.data = data;
        r.requestId = UUID.randomUUID().toString().substring(0, 8);
        return r;
    }

    public static <T> R<T> ok() { return ok(null); }

    public static <T> R<T> fail(int code, String message) {
        R<T> r = new R<>();
        r.code = code; r.message = message;
        r.requestId = UUID.randomUUID().toString().substring(0, 8);
        return r;
    }
}
