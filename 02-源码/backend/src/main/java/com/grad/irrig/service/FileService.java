package com.grad.irrig.service;

import com.grad.irrig.common.BizException;
import com.grad.irrig.common.UserContext;
import com.grad.irrig.entity.SysFile;
import com.grad.irrig.mapper.SysFileMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Set;
import java.util.UUID;

/**
 * 文件上传：只接受图片与 PDF，落盘到项目根 uploads/日期/ 下，
 * 返回相对路径 /uploads/...，数据库只存相对路径，不存外部 URL。
 */
@Service
@RequiredArgsConstructor
public class FileService {

    private final SysFileMapper fileMapper;

    @Value("${app.upload-dir:./uploads}")
    private String uploadDir;

    private static final Set<String> ALLOW = Set.of("jpg", "jpeg", "png", "webp", "pdf");
    private static final long MAX_SIZE = 20L * 1024 * 1024;

    public String upload(MultipartFile file, String bizType, Long bizId) {
        if (file == null || file.isEmpty()) {
            throw new BizException(400, "请选择要上传的文件");
        }
        String origin = file.getOriginalFilename() == null ? "file" : file.getOriginalFilename();
        String ext = origin.contains(".")
                ? origin.substring(origin.lastIndexOf('.') + 1).toLowerCase() : "";
        if (!ALLOW.contains(ext)) {
            throw new BizException(400, "仅支持 jpg/png/webp/pdf，当前为 " + (ext.isEmpty() ? "未知" : ext));
        }
        if (file.getSize() > MAX_SIZE) {
            throw new BizException(400, "单个文件不超过 20MB");
        }
        String day = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
        String name = UUID.randomUUID().toString().replace("-", "").substring(0, 16) + "." + ext;
        try {
            Path dir = Paths.get(uploadDir, day).toAbsolutePath().normalize();
            Files.createDirectories(dir);
            file.transferTo(dir.resolve(name).toFile());
        } catch (IOException e) {
            throw new BizException(500, "文件保存失败：" + e.getMessage());
        }
        String relative = "/uploads/" + day + "/" + name;
        SysFile record = new SysFile();
        record.setBizType(bizType == null ? "COMMON" : bizType);
        record.setBizId(bizId);
        record.setOriginName(origin);
        record.setFilePath(relative);
        record.setFileSize(file.getSize());
        record.setUploaderId(UserContext.userId());
        record.setUploadTime(LocalDateTime.now());
        fileMapper.insert(record);
        return relative;
    }

    public List<SysFile> listByBiz(String bizType, Long bizId) {
        return fileMapper.selectList(new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<SysFile>()
                .eq(SysFile::getBizType, bizType).eq(SysFile::getBizId, bizId)
                .orderByDesc(SysFile::getId));
    }
}
