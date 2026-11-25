package com.grad.irrig.common;

import lombok.Getter;

/** 业务异常，交给 GlobalExceptionHandler 转统一响应体。 */
@Getter
public class BizException extends RuntimeException {
    private final int code;

    public BizException(String message) { this(400, message); }

    public BizException(int code, String message) {
        super(message);
        this.code = code;
    }
}
