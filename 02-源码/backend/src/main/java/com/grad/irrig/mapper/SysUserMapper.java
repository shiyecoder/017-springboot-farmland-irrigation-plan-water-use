package com.grad.irrig.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.irrig.entity.SysUser;
import org.apache.ibatis.annotations.Mapper;

/** SysUser 基础 CRUD，复杂统计在 Service 层用 QueryWrapper 或 XML 完成。 */
@Mapper
public interface SysUserMapper extends BaseMapper<SysUser> {
}
