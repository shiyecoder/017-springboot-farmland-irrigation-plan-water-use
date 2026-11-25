package com.grad.irrig.controller;

import com.grad.irrig.common.R;
import com.grad.irrig.entity.SysFile;
import com.grad.irrig.service.FileService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

/** 文件上传：返回相对路径，前端直接用于 img/src 与表单字段。 */
@RestController
@RequestMapping("/api/file")
@RequiredArgsConstructor
public class FileController {

    private final FileService fileService;

    @PostMapping("/upload")
    public R<String> upload(@RequestParam("file") MultipartFile file,
                            @RequestParam(required = false) String bizType,
                            @RequestParam(required = false) Long bizId) {
        return R.ok(fileService.upload(file, bizType, bizId));
    }

    @GetMapping("/list")
    public R<List<SysFile>> list(@RequestParam String bizType, @RequestParam Long bizId) {
        return R.ok(fileService.listByBiz(bizType, bizId));
    }
}
