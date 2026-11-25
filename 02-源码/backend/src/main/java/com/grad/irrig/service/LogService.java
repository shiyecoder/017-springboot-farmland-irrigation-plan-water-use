package com.grad.irrig.service;

import com.grad.irrig.common.UserContext;
import com.grad.irrig.entity.SysOperationLog;
import com.grad.irrig.mapper.SysOperationLogMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

/**
 * 状态流转留痕。所有改变业务状态的操作都必须调用本服务，
 * 记录操作人、时间、前后状态与原因，普通用户不得修改日志。
 */
@Service
@RequiredArgsConstructor
public class LogService {

    private final SysOperationLogMapper logMapper;

    public void write(String bizType, Long bizId, String bizNo, String action,
                      String before, String after, String reason) {
        SysOperationLog log = new SysOperationLog();
        log.setBizType(bizType);
        log.setBizId(bizId);
        log.setBizNo(bizNo);
        log.setAction(action);
        log.setBeforeStatus(before);
        log.setAfterStatus(after);
        log.setReason(reason);
        log.setOperatorId(UserContext.userId());
        log.setOperatorName(UserContext.realName());
        log.setCreateTime(LocalDateTime.now());
        logMapper.insert(log);
    }
}
