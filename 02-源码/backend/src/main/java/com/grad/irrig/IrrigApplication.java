package com.grad.irrig;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * 农田灌溉计划与用水统计系统启动类。
 * 端口 8086、库 new_017 由 application.yml 固定，属于通道 7 的隔离配置。
 */
@SpringBootApplication
@MapperScan("com.grad.irrig.mapper")
@EnableScheduling
public class IrrigApplication {

    public static void main(String[] args) {
        SpringApplication.run(IrrigApplication.class, args);
    }
}
