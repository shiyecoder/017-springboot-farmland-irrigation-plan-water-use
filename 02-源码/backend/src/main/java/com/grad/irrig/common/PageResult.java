package com.grad.irrig.common;

import lombok.Data;

import java.util.List;

/** 服务端分页结构：总数、页码、每页条数、列表。 */
@Data
public class PageResult<T> {
    private long total;
    private long page;
    private long size;
    private List<T> records;

    public static <T> PageResult<T> of(long total, long page, long size, List<T> records) {
        PageResult<T> p = new PageResult<>();
        p.total = total; p.page = page; p.size = size; p.records = records;
        return p;
    }
}
