package com.grad.irrig.config;

import com.fasterxml.jackson.databind.module.SimpleModule;
import com.fasterxml.jackson.datatype.jsr310.deser.LocalDateDeserializer;
import com.fasterxml.jackson.datatype.jsr310.deser.LocalDateTimeDeserializer;
import com.fasterxml.jackson.datatype.jsr310.ser.LocalDateSerializer;
import com.fasterxml.jackson.datatype.jsr310.ser.LocalDateTimeSerializer;
import org.springframework.boot.autoconfigure.jackson.Jackson2ObjectMapperBuilderCustomizer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * 全系统时间统一格式：日期时间 yyyy-MM-dd HH:mm:ss，日期 yyyy-MM-dd。
 * 前端 utils/format.js 的 formatTime 与之保持一致，避免时区与格式错乱。
 */
@Configuration
public class JacksonConfig {

    public static final String DATE_TIME_PATTERN = "yyyy-MM-dd HH:mm:ss";
    public static final String DATE_PATTERN = "yyyy-MM-dd";

    @Bean
    public Jackson2ObjectMapperBuilderCustomizer jacksonCustomizer() {
        DateTimeFormatter dtf = DateTimeFormatter.ofPattern(DATE_TIME_PATTERN);
        DateTimeFormatter df = DateTimeFormatter.ofPattern(DATE_PATTERN);
        return builder -> {
            SimpleModule module = new SimpleModule();
            module.addSerializer(LocalDateTime.class, new LocalDateTimeSerializer(dtf));
            module.addDeserializer(LocalDateTime.class, new LocalDateTimeDeserializer(dtf));
            module.addSerializer(LocalDate.class, new LocalDateSerializer(df));
            module.addDeserializer(LocalDate.class, new LocalDateDeserializer(df));
            builder.modules(module);
        };
    }
}
