# -*- coding: utf-8 -*-
"""从字段清单批量生成 MyBatis-Plus 实体与 Mapper，保证 Java 侧与 DDL 一一对应。"""
import pathlib

BASE = pathlib.Path("/Users/xiaoxin/showcase/build/NEW-017/backend/src/main/java/com/grad/irrig")
PKG_E = "com.grad.irrig.entity"
PKG_M = "com.grad.irrig.mapper"

T = {
    "L": "Long", "I": "Integer", "S": "String", "B": "BigDecimal",
    "DT": "LocalDateTime", "LD": "LocalDate",
}

# (类名, 表名, 表注释, 主键类型, [(字段, 类型, 注释)], 是否有 version/deleted)
ENTITIES = [
    ("SysOrg", "sys_org", "组织架构", "L", [
        ("code", "S", "组织编码"), ("name", "S", "组织名称"), ("parentId", "L", "上级组织"),
        ("orgType", "S", "组织类型"), ("sortNo", "I", "排序"), ("status", "I", "状态：1 启用 0 停用"),
        ("createTime", "DT", "创建时间")], False),
    ("SysRole", "sys_role", "角色", "L", [
        ("code", "S", "角色编码"), ("name", "S", "角色名称"), ("dataScope", "S", "数据范围 ALL/DEPT/SELF"),
        ("remark", "S", "说明"), ("createTime", "DT", "创建时间")], False),
    ("SysUser", "sys_user", "用户", "L", [
        ("username", "S", "登录账号"), ("password", "S", "BCrypt 密码"), ("realName", "S", "姓名"),
        ("phone", "S", "联系电话"), ("email", "S", "邮箱"), ("avatar", "S", "头像相对路径"),
        ("roleId", "L", "角色"), ("orgId", "L", "所属组织"), ("status", "I", "状态"),
        ("loginFailCount", "I", "连续登录失败次数"), ("lockUntil", "DT", "锁定截止时间"),
        ("lastLoginTime", "DT", "最近登录时间"), ("createTime", "DT", "创建时间"),
        ("updateTime", "DT", "更新时间")], False),
    ("SysMenu", "sys_menu", "菜单", "L", [
        ("parentId", "L", "上级菜单"), ("name", "S", "菜单名称"), ("path", "S", "前端路由"),
        ("icon", "S", "图标"), ("menuType", "S", "M 目录 C 菜单 F 按钮"), ("perm", "S", "权限标识"),
        ("sortNo", "I", "排序"), ("visible", "I", "是否显示")], False),
    ("SysRoleMenu", "sys_role_menu", "角色菜单", "L", [
        ("roleId", "L", "角色"), ("menuId", "L", "菜单")], False),
    ("SysDictItem", "sys_dict_item", "字典项", "L", [
        ("dictType", "S", "字典类型"), ("label", "S", "显示文本"), ("value", "S", "存储值"),
        ("sortNo", "I", "排序"), ("status", "I", "状态")], False),
    ("SysFile", "sys_file", "附件", "L", [
        ("bizType", "S", "业务类型"), ("bizId", "L", "业务主键"), ("originName", "S", "原始文件名"),
        ("filePath", "S", "相对路径"), ("fileSize", "L", "字节数"), ("uploaderId", "L", "上传人"),
        ("uploadTime", "DT", "上传时间")], False),
    ("SysMessage", "sys_message", "站内消息", "L", [
        ("title", "S", "标题"), ("content", "S", "内容"), ("bizNo", "S", "业务编号"),
        ("bizType", "S", "业务类型"), ("receiverId", "L", "接收人"), ("readFlag", "I", "是否已读"),
        ("createTime", "DT", "创建时间")], False),
    ("SysOperationLog", "sys_operation_log", "操作日志", "L", [
        ("bizType", "S", "业务类型"), ("bizId", "L", "业务主键"), ("bizNo", "S", "业务编号"),
        ("action", "S", "动作"), ("beforeStatus", "S", "变更前状态"), ("afterStatus", "S", "变更后状态"),
        ("reason", "S", "原因"), ("operatorId", "L", "操作人"), ("operatorName", "S", "操作人姓名"),
        ("createTime", "DT", "操作时间")], False),
    ("WaterSource", "water_source", "水源", "L", [
        ("code", "S", "水源编号"), ("name", "S", "水源名称"), ("sourceType", "S", "水库/机井/河道/塘坝"),
        ("designSupply", "B", "设计日供水"), ("availableVolume", "B", "当前可用水量"),
        ("manager", "S", "负责人"), ("phone", "S", "联系电话"), ("photo", "S", "现场照片"),
        ("status", "S", "状态"), ("remark", "S", "备注"), ("createTime", "DT", "创建时间")], False),
    ("Canal", "canal", "渠道", "L", [
        ("code", "S", "渠道编号"), ("name", "S", "渠道名称"), ("sourceId", "L", "所属水源"),
        ("canalLevel", "S", "干渠/支渠"), ("designFlow", "B", "设计流量"), ("lengthKm", "B", "长度 km"),
        ("status", "S", "状态"), ("remark", "S", "备注"), ("createTime", "DT", "创建时间")], False),
    ("Gate", "gate", "闸口", "L", [
        ("code", "S", "闸口编号"), ("name", "S", "闸口名称"), ("canalId", "L", "所属渠道"),
        ("designFlow", "B", "设计流量"), ("openDegree", "I", "开度百分比"), ("status", "S", "状态"),
        ("remark", "S", "备注")], False),
    ("WaterMeter", "water_meter", "水表", "L", [
        ("code", "S", "水表编号"), ("name", "S", "水表名称"), ("gateId", "L", "安装闸口"),
        ("farmlandId", "L", "关联地块"), ("initReading", "B", "初始读数"),
        ("currentReading", "B", "当前读数"), ("installDate", "LD", "安装日期"),
        ("photo", "S", "表具照片"), ("status", "S", "状态")], False),
    ("Farmland", "farmland", "农田地块", "L", [
        ("code", "S", "地块编号"), ("name", "S", "地块名称"), ("area", "B", "面积（亩）"),
        ("crop", "S", "作物"), ("growthStage", "S", "种植阶段"), ("soilType", "S", "土壤类型"),
        ("irrigationType", "S", "灌溉方式"), ("region", "S", "所属片区"), ("address", "S", "位置描述"),
        ("ownerId", "L", "承包种植户"), ("ownerName", "S", "种植户姓名"), ("orgId", "L", "所属组织"),
        ("photo", "S", "地块照片"), ("status", "S", "状态"), ("deleted", "I", "逻辑删除"),
        ("version", "I", "乐观锁版本号"), ("createTime", "DT", "创建时间"), ("updateTime", "DT", "更新时间")], True),
    ("WaterQuota", "water_quota", "水权定额", "L", [
        ("quotaYear", "I", "年度"), ("farmlandId", "L", "地块"), ("farmerId", "L", "种植户"),
        ("farmerName", "S", "种植户姓名"), ("quotaVolume", "B", "定额水量"),
        ("usedVolume", "B", "已用水量"), ("remainingVolume", "B", "剩余水量"), ("status", "S", "状态"),
        ("version", "I", "乐观锁版本号"), ("createTime", "DT", "创建时间"), ("updateTime", "DT", "更新时间")], True),
    ("WaterApplication", "water_application", "用水申请", "L", [
        ("code", "S", "申请编号"), ("farmlandId", "L", "地块"), ("crop", "S", "作物"),
        ("growthStage", "S", "种植阶段"), ("expectDate", "LD", "期望用水日期"),
        ("applyVolume", "B", "申请水量"), ("urgency", "S", "紧急程度"),
        ("applicantId", "L", "申请人"), ("applicantName", "S", "申请人姓名"),
        ("status", "S", "状态"), ("auditOpinion", "S", "审核意见"), ("auditBy", "S", "审核人"),
        ("auditTime", "DT", "审核时间"), ("version", "I", "乐观锁版本号"),
        ("createTime", "DT", "创建时间"), ("updateTime", "DT", "更新时间")], True),
    ("IrrigationPlan", "irrigation_plan", "灌溉计划", "L", [
        ("code", "S", "计划编号"), ("applicationId", "L", "来源申请"), ("farmlandId", "L", "地块"),
        ("canalId", "L", "渠道"), ("gateId", "L", "闸口"), ("planStart", "DT", "计划开始"),
        ("planEnd", "DT", "计划结束"), ("planVolume", "B", "计划水量"), ("priority", "S", "优先级"),
        ("status", "S", "状态"), ("dispatcherId", "L", "调度员"), ("dispatcherName", "S", "调度员姓名"),
        ("rejectReason", "S", "驳回原因"), ("remark", "S", "备注"), ("version", "I", "乐观锁版本号"),
        ("createTime", "DT", "创建时间"), ("updateTime", "DT", "更新时间")], True),
    ("IrrigationTask", "irrigation_task", "灌溉任务", "L", [
        ("code", "S", "任务编号"), ("planId", "L", "灌溉计划"), ("farmlandId", "L", "地块"),
        ("operatorId", "L", "放水员"), ("operatorName", "S", "放水员姓名"),
        ("planVolume", "B", "计划水量"), ("startReading", "B", "开始表数"),
        ("endReading", "B", "结束表数"), ("actualVolume", "B", "实际水量"),
        ("startTime", "DT", "实际开始"), ("endTime", "DT", "实际结束"), ("status", "S", "状态"),
        ("photo", "S", "现场照片"), ("receiverName", "S", "受水人确认"),
        ("confirmTime", "DT", "确认时间"), ("interruptReason", "S", "中断原因"),
        ("version", "I", "乐观锁版本号"), ("createTime", "DT", "创建时间"),
        ("updateTime", "DT", "更新时间")], True),
    ("WaterMeterRecord", "water_meter_record", "水表记录", "L", [
        ("taskId", "L", "任务"), ("meterId", "L", "水表"), ("startReading", "B", "开始表数"),
        ("endReading", "B", "结束表数"), ("volume", "B", "本段水量"), ("recordTime", "DT", "抄表时间"),
        ("recorderId", "L", "抄表人"), ("recorderName", "S", "抄表人姓名"),
        ("photo", "S", "表盘照片"), ("remark", "S", "备注")], False),
    ("FeeLedger", "fee_ledger", "费用台账", "L", [
        ("code", "S", "费用单号"), ("taskId", "L", "任务"), ("farmlandId", "L", "地块"),
        ("farmerName", "S", "种植户"), ("actualVolume", "B", "实际水量"), ("baseVolume", "B", "定额内水量"),
        ("excessVolume", "B", "超额水量"), ("basePrice", "B", "基础单价"),
        ("excessPrice", "B", "超额单价"), ("amount", "B", "金额"), ("billMonth", "S", "计费月份"),
        ("status", "S", "状态"), ("payTime", "DT", "缴费时间"), ("createTime", "DT", "创建时间")], False),
    ("ExceptionRecord", "exception_record", "异常处置", "L", [
        ("taskId", "L", "任务"), ("excType", "S", "异常类型"), ("description", "S", "异常描述"),
        ("lossVolume", "B", "损失水量"), ("handleResult", "S", "处理结果"), ("photo", "S", "现场照片"),
        ("reporterId", "L", "上报人"), ("reporterName", "S", "上报人姓名"), ("status", "S", "状态"),
        ("createTime", "DT", "上报时间")], False),
    ("RuleConfig", "rule_config", "用水建议规则", "L", [
        ("name", "S", "规则名称"), ("version", "S", "版本号"), ("cropWeight", "I", "作物权重"),
        ("stageWeight", "I", "阶段权重"), ("areaWeight", "I", "面积权重"), ("soilWeight", "I", "土壤权重"),
        ("rainWeight", "I", "降雨权重"), ("historyWeight", "I", "历史权重"), ("status", "S", "状态"),
        ("effectiveTime", "DT", "生效时间"), ("createBy", "S", "创建人"), ("createTime", "DT", "创建时间")], False),
    ("WaterAdvice", "water_advice", "用水建议留痕", "L", [
        ("taskId", "L", "关联任务"), ("farmlandId", "L", "地块"), ("ruleId", "L", "规则版本"),
        ("ruleVersion", "S", "规则版本号"), ("snapshot", "S", "输入快照"),
        ("cropScore", "B", "作物得分"), ("stageScore", "B", "阶段得分"), ("areaScore", "B", "面积得分"),
        ("soilScore", "B", "土壤得分"), ("rainScore", "B", "降雨得分"), ("historyScore", "B", "历史得分"),
        ("totalScore", "B", "加权总分"), ("suggestVolume", "B", "建议水量"),
        ("quotaVolume", "B", "对比定额"), ("deviation", "B", "偏差百分比"), ("grade", "S", "结果等级"),
        ("explainMain", "S", "主要影响因素"), ("explainMissing", "S", "未满足条件"),
        ("explainImprove", "S", "可改进项"), ("adjustVolume", "B", "人工修正水量"),
        ("adjustReason", "S", "修正原因"), ("adjustBy", "S", "修正人"),
        ("adjustTime", "DT", "修正时间"), ("createTime", "DT", "计算时间")], False),
    ("FeeRule", "fee_rule", "计费规则", "L", [
        ("name", "S", "规则名称"), ("basePrice", "B", "定额内单价"), ("excessPrice", "B", "超额单价"),
        ("freeQuotaPerMu", "B", "每亩免费定额"), ("status", "S", "状态"),
        ("effectiveTime", "DT", "生效时间")], False),
]


def gen_entity(cls, table, comment, pk, fields, has_version):
    imports = {"java.math.BigDecimal", "java.time.LocalDate", "java.time.LocalDateTime"}
    body = []
    for f, t, c in fields:
        imports.add("com.baomidou.mybatisplus.annotation.TableField")
        extra = ""
        if f == "deleted":
            extra = '\n    @TableLogic'
        if f == "version":
            extra = '\n    @Version'
        body.append(f'    /** {c} */{extra}\n    private {T[t]} {f};')
    imp = "\n".join(f"import {i};" for i in sorted(imports))
    return f'''package {PKG_E};

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
{imp}
import lombok.Data;

/** {comment}。字段与 sql/init.sql 中 `{table}` 一一对应。 */
@Data
@TableName("{table}")
public class {cls} {{

    @TableId(type = IdType.AUTO)
    private Long id;

{chr(10).join(body)}
}}
'''


def gen_mapper(cls):
    return f'''package {PKG_M};

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import {PKG_E}.{cls};
import org.apache.ibatis.annotations.Mapper;

/** {cls} 基础 CRUD，复杂统计在 Service 层用 QueryWrapper 或 XML 完成。 */
@Mapper
public interface {cls}Mapper extends BaseMapper<{cls}> {{
}}
'''


for cls, table, comment, pk, fields, hv in ENTITIES:
    (BASE / "entity" / f"{cls}.java").write_text(gen_entity(cls, table, comment, pk, fields, hv))
    (BASE / "mapper" / f"{cls}Mapper.java").write_text(gen_mapper(cls))

print("实体", len(ENTITIES), "Mapper", len(ENTITIES))
