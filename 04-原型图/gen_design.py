import pathlib

OUT = pathlib.Path("/Users/xiaoxin/showcase/build/NEW-017/design")
OUT.joinpath("pages").mkdir(parents=True, exist_ok=True)

MENU = [
    ("概览", [("dashboard", "农业用水分析", "chart"), ("farmland", "地块用水地图", "map")]),
    ("业务办理", [("application", "用水申请", "doc"), ("plan", "灌溉计划", "cal"),
                  ("task", "执行任务", "drop"), ("fee", "费用台账", "coin")]),
    ("台账配置", [("quota", "水权定额", "scale"), ("source", "水源与渠道", "wave"),
                  ("advice", "用水建议", "spark")]),
    ("系统", [("system", "系统管理", "gear")]),
]
ICON = {
    "chart": '<path d="M3 3v18h18" stroke="currentColor" fill="none" stroke-width="1.6"/><rect x="6" y="11" width="3" height="7" fill="currentColor"/><rect x="11" y="8" width="3" height="10" fill="currentColor"/><rect x="16" y="5" width="3" height="13" fill="currentColor"/>',
    "map": '<path d="M3 6l5-2 5 2 5-2v14l-5 2-5-2-5 2V6z" stroke="currentColor" fill="none" stroke-width="1.5"/><path d="M8 4v14M13 6v14" stroke="currentColor" stroke-width="1.2"/>',
    "doc": '<rect x="4" y="3" width="16" height="18" rx="2" stroke="currentColor" fill="none" stroke-width="1.5"/><path d="M8 8h8M8 12h8M8 16h5" stroke="currentColor" stroke-width="1.4"/>',
    "cal": '<rect x="3" y="5" width="18" height="16" rx="2" stroke="currentColor" fill="none" stroke-width="1.5"/><path d="M3 10h18M8 3v4M16 3v4" stroke="currentColor" stroke-width="1.4"/>',
    "drop": '<path d="M12 3s6 6.5 6 11a6 6 0 11-12 0c0-4.5 6-11 6-11z" stroke="currentColor" fill="none" stroke-width="1.5"/>',
    "coin": '<circle cx="12" cy="12" r="9" stroke="currentColor" fill="none" stroke-width="1.5"/><path d="M12 7v10M9 9.5h4.5a2 2 0 010 4H9" stroke="currentColor" fill="none" stroke-width="1.4"/>',
    "scale": '<path d="M12 4v16M6 8h12" stroke="currentColor" stroke-width="1.5"/><path d="M6 8l-3 6h6l-3-6zM18 8l-3 6h6l-3-6z" stroke="currentColor" fill="none" stroke-width="1.4"/>',
    "wave": '<path d="M3 9c3-3 6 3 9 0s6-3 9 0M3 15c3-3 6 3 9 0s6-3 9 0" stroke="currentColor" fill="none" stroke-width="1.5"/>',
    "spark": '<path d="M12 3l2.2 5.8L20 11l-5.8 2.2L12 19l-2.2-5.8L4 11l5.8-2.2L12 3z" stroke="currentColor" fill="none" stroke-width="1.4"/>',
    "gear": '<circle cx="12" cy="12" r="3" stroke="currentColor" fill="none" stroke-width="1.5"/><path d="M12 3v3M12 18v3M4.2 7.5l2.6 1.5M17.2 15l2.6 1.5M4.2 16.5l2.6-1.5M17.2 9l2.6-1.5" stroke="currentColor" stroke-width="1.4"/>',
}


def shell(title, crumb, active, body, who="灌区管理员 · 张建民", role="admin"):
    groups = []
    for gname, items in MENU:
        lis = []
        for key, label, icon in items:
            cls = ' class="on"' if key == active else ""
            lis.append(
                f'<a href="{key}.html"{cls}><svg class="ico" viewBox="0 0 24 24">{ICON[icon]}</svg>{label}</a>'
            )
        groups.append(f'<div class="grp">{gname}</div>' + "".join(lis))
    side_class = "side" if role == "admin" else "side light"
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · 农田灌溉计划与用水统计系统</title>
<link rel="stylesheet" href="mock.css"></head>
<body class="{role}">
<aside class="{side_class}">
  <div class="brand"><svg width="20" height="20" viewBox="0 0 24 24"><path d="M12 3s6 6.5 6 11a6 6 0 11-12 0c0-4.5 6-11 6-11z" fill="#7FB3D5"/></svg>灌溉用水管理</div>
  <nav>{''.join(groups)}</nav>
</aside>
<div class="main">
  <header class="top">
    <div class="crumb">灌区管理 / <b>{crumb}</b></div>
    <div class="right"><span>消息 <b style="color:#B22B31">3</b></span><span>帮助</span>
      <div class="avatar">张</div><span>{who}</span></div>
  </header>
  <div class="content">{body}</div>
</div>
</body></html>"""


def tag(text, kind="blue"):
    return f'<span class="tag {kind}">{text}</span>'


farmland_rows = [
    ("FD-2026-0031", "北干渠一号地", "182.40", "水稻", "分蘖期", "壤土", "滴灌", "李国强", "正常", "ok"),
    ("FD-2026-0032", "北干渠二号地", "96.75", "小麦", "拔节期", "黏土", "喷灌", "王秀兰", "正常", "ok"),
    ("FD-2026-0033", "东支渠三号地", "240.00", "玉米", "苗期", "砂壤土", "渠道灌溉", "赵德海", "正常", "ok"),
    ("FD-2026-0034", "西支渠五号地", "58.20", "蔬菜", "结果期", "壤土", "滴灌", "陈志远", "休耕", "blue"),
    ("FD-2026-0035", "南干渠七号地", "315.60", "水稻", "孕穗期", "黏土", "渠道灌溉", "孙立平", "正常", "ok"),
    ("FD-2026-0036", "北干渠九号地", "124.30", "果树", "果实膨大期", "砂壤土", "滴灌", "周敏", "缺水", "warn"),
]


def farmland_body():
    rows = "".join(
        f"<tr><td>{a}</td><td>{b}</td><td class='num'>{c}</td><td>{d}</td><td>{e}</td>"
        f"<td>{f}</td><td>{g}</td><td>{h}</td><td>{tag(i, k)}</td>"
        f"<td><a href='advice.html'>查看</a> <a href='plan.html'>编排</a></td></tr>"
        for a, b, c, d, e, f, g, h, i, k in farmland_rows
    )
    return f"""<h1 class="title">地块用水地图</h1>
<p class="sub">按区域、作物、种植阶段与执行状态筛选地块，查看定额余量与最近一次灌溉</p>
<div class="card"><div class="card-bd" style="padding-bottom:6px">
  <div class="filters">
    <div class="field"><label>区域</label><select><option>全部区域</option><option>北干渠片区</option><option>东支渠片区</option></select></div>
    <div class="field"><label>作物</label><select><option>全部作物</option><option>水稻</option><option>小麦</option><option>玉米</option></select></div>
    <div class="field"><label>种植阶段</label><select><option>全部阶段</option><option>苗期</option><option>分蘖期</option><option>拔节期</option></select></div>
    <div class="field"><label>灌溉方式</label><select><option>全部方式</option><option>滴灌</option><option>喷灌</option><option>渠道灌溉</option></select></div>
    <div class="field"><label>计划日期</label><input type="date" value="2026-10-01"></div>
    <button class="btn">查询</button><button class="btn ghost">重置</button>
    <button class="btn ghost" style="margin-left:auto">高级筛选</button>
  </div>
  <div class="kpis" style="grid-template-columns:repeat(4,1fr);margin-bottom:14px">
    <div class="kpi"><div class="lb">在册地块</div><div class="vl">126<small>块</small></div></div>
    <div class="kpi"><div class="lb">灌溉面积</div><div class="vl">1,842<small>亩</small></div></div>
    <div class="kpi"><div class="lb">本月已用</div><div class="vl">63,420<small>m³</small></div><div class="dt">较上月 +8.2%</div></div>
    <div class="kpi"><div class="lb">定额余量不足</div><div class="vl" style="color:#B4761E">7<small>块</small></div><div class="dt warn">需优先排程</div></div>
  </div>
</div></div>
<div class="card"><div class="card-hd"><span>地块清单</span>
  <span style="font-weight:400;font-size:13px"><button class="btn sm ghost">导出当前筛选</button>
  <button class="btn sm">新建地块</button></span></div>
<div class="card-bd" style="padding-top:0">
<div class="tw"><table>
<thead><tr><th>地块编号</th><th>地块名称</th><th>面积(亩)</th><th>作物</th><th>种植阶段</th>
<th>土壤类型</th><th>灌溉方式</th><th>责任人</th><th>状态</th><th>操作</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<div class="pager"><span>共 126 条 · 每页 10 条</span>
  <div class="pages"><span>‹</span><span class="on">1</span><span>2</span><span>3</span><span>4</span><span>›</span></div></div>
</div></div>"""


def dashboard_body():
    return """<h1 class="title">农业用水分析</h1>
<p class="sub">统计区间 2026-10-01 至 2026-10-31 · 数据来源：水表抄表与任务执行记录</p>
<div class="kpis">
  <div class="kpi"><div class="lb">计划用水量</div><div class="vl">84,560<small>m³</small></div><div class="dt">完成率 98.4%</div></div>
  <div class="kpi"><div class="lb">实际用水量</div><div class="vl">86,120<small>m³</small></div><div class="dt warn">超计划 1.8%</div></div>
  <div class="kpi"><div class="lb">定额偏差</div><div class="vl">-3.2<small>%</small></div><div class="dt">较上月收窄</div></div>
  <div class="kpi"><div class="lb">计划完成率</div><div class="vl">92.6<small>%</small></div></div>
  <div class="kpi"><div class="lb">亩均用水</div><div class="vl">46.8<small>m³/亩</small></div></div>
  <div class="kpi"><div class="lb">异常损失</div><div class="vl" style="color:#B22B31">1,240<small>m³</small></div><div class="dt warn">3 起待处理</div></div>
</div>
<div class="dash">
  <div class="chart span2"><h4>近 30 天用水趋势 <em>计划 vs 实际</em></h4>
    <div class="bars"><i style="height:42%"></i><i style="height:56%"></i><i style="height:48%"></i>
    <i style="height:72%"></i><i style="height:64%"></i><i style="height:86%"></i><i style="height:70%"></i>
    <i style="height:58%"></i><i style="height:78%"></i><i style="height:92%"></i><i style="height:66%"></i>
    <i style="height:54%"></i></div></div>
  <div class="chart"><h4>任务状态分布</h4><div class="donut"></div>
    <div style="font-size:12.5px;color:#5A6B78;text-align:center">已完成 42% · 进行中 26% · 待执行 18% · 异常 14%</div></div>
  <div class="chart"><h4>作物用水占比</h4>
    <div class="hbar">
      <div class="row"><span>水稻</span><div class="tr"><i style="width:92%"></i></div><b>39.2%</b></div>
      <div class="row"><span>小麦</span><div class="tr"><i style="width:64%"></i></div><b>26.8%</b></div>
      <div class="row"><span>玉米</span><div class="tr"><i style="width:44%"></i></div><b>18.4%</b></div>
      <div class="row"><span>蔬菜</span><div class="tr"><i style="width:26%"></i></div><b>11.0%</b></div>
      <div class="row"><span>果树</span><div class="tr"><i style="width:12%"></i></div><b>4.6%</b></div>
    </div></div>
  <div class="chart"><h4>渠道时段负荷</h4>
    <div class="bars"><i style="height:30%;background:#8FB3C7"></i><i style="height:62%;background:#2878B5"></i>
    <i style="height:88%;background:#0F3B5D"></i><i style="height:54%;background:#5C8FAE"></i>
    <i style="height:34%;background:#8FB3C7"></i><i style="height:20%;background:#8FB3C7"></i></div>
    <div style="font-size:12px;color:#5A6B78;margin-top:6px">08:00 · 12:00 · 16:00 · 20:00 · 00:00</div></div>
  <div class="chart"><h4>地块单耗排行</h4>
    <div class="hbar">
      <div class="row"><span>南干七号</span><div class="tr"><i style="width:96%"></i></div><b>62.4</b></div>
      <div class="row"><span>北干一号</span><div class="tr"><i style="width:82%"></i></div><b>54.1</b></div>
      <div class="row"><span>东支三号</span><div class="tr"><i style="width:66%"></i></div><b>44.7</b></div>
      <div class="row"><span>西支五号</span><div class="tr"><i style="width:48%"></i></div><b>32.8</b></div>
    </div></div>
  <div class="chart"><h4>用水建议结果分布 <em>创新模块</em></h4>
    <div class="bars"><i style="height:78%;background:#1F7653"></i><i style="height:52%;background:#2878B5"></i>
    <i style="height:34%;background:#B4761E"></i><i style="height:16%;background:#B22B31"></i></div>
    <div style="font-size:12px;color:#5A6B78;margin-top:6px">采纳 78% · 调整 52% · 偏差 34% · 拒绝 16%</div></div>
</div>"""


def plan_body():
    rows = [
        ("PL-20261031-012", "北干渠一号地", "水稻 / 分蘖期", "北干渠 · 2# 闸", "10-31 08:00 ~ 12:00", "1,860", "高", "待审核", "blue"),
        ("PL-20261031-013", "东支渠三号地", "玉米 / 苗期", "东支渠 · 1# 闸", "10-31 13:00 ~ 16:30", "1,240", "中", "已安排", "sky"),
        ("PL-20261031-014", "南干渠七号地", "水稻 / 孕穗期", "南干渠 · 4# 闸", "10-31 16:00 ~ 21:00", "2,460", "高", "冲突", "bad"),
        ("PL-20261030-009", "西支渠五号地", "蔬菜 / 结果期", "西支渠 · 3# 闸", "10-30 09:00 ~ 11:00", "480", "低", "已完成", "ok"),
        ("PL-20261030-008", "北干渠二号地", "小麦 / 拔节期", "北干渠 · 1# 闸", "10-30 14:00 ~ 17:00", "960", "中", "待执行", "blue"),
    ]
    tr = "".join(
        f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td><td>{e}</td><td class='num'>{f}</td>"
        f"<td>{g}</td><td>{tag(h, k)}</td><td><a href='task.html'>详情</a> · <a href='#〰'>审批</a></td></tr>"
        for a, b, c, d, e, f, g, h, k in rows
    )
    return f"""<h1 class="title">灌溉计划编制</h1>
<p class="sub">按水源可用量、渠道容量与作物阶段编排时段；同一闸口重叠任务由后端容量校验拦截</p>
<div class="card"><div class="card-bd">
  <div class="filters">
    <div class="field"><label>快捷标签</label>
      <div style="display:flex;gap:8px"><button class="btn sm">全部</button><button class="btn sm ghost">待我处理</button>
      <button class="btn sm ghost">处理中</button><button class="btn sm ghost">已完成</button><button class="btn sm ghost">异常</button></div></div>
    <div class="field"><label>渠道</label><select><option>全部渠道</option><option>北干渠</option><option>东支渠</option></select></div>
    <div class="field"><label>日期</label><input type="date" value="2026-10-31"></div>
    <button class="btn">查询</button>
    <button class="btn sec" style="margin-left:auto">新建计划</button>
  </div>
  <div style="background:#FBF0DF;border:1px solid #E9CFA6;border-radius:6px;padding:10px 14px;font-size:13px;color:#8A5A12;margin-bottom:14px">
    ⚠ 1 条计划存在闸口容量冲突：PL-20261031-014 与 PL-20261031-011 在 16:00–18:00 共用南干渠 4# 闸，合计流量 0.42 m³/s 超过设计值 0.35 m³/s。
  </div>
  <div class="tw"><table>
  <thead><tr><th>计划编号</th><th>地块</th><th>作物/阶段</th><th>渠道·闸口</th><th>计划时段</th>
  <th>计划水量(m³)</th><th>优先级</th><th>状态</th><th>操作</th></tr></thead>
  <tbody>{tr}</tbody></table></div>
  <div class="pager"><span>共 34 条</span><div class="pages"><span>‹</span><span class="on">1</span><span>2</span><span>3</span><span>4</span><span>›</span></div></div>
</div></div>
<div class="card"><div class="card-hd"><span>日历排程 · 2026 年 10 月第 5 周</span><span style="font-weight:400;font-size:12.5px;color:#5A6B78">点击时段可查看当日任务</span></div>
<div class="card-bd"><div class="tw"><table>
<thead><tr><th>时段</th><th>北干渠</th><th>东支渠</th><th>南干渠</th><th>西支渠</th></tr></thead><tbody>
<tr><td>08:00–12:00</td><td>{tag('一号地 1,860 m³','sky')}</td><td>—</td><td>{tag('七号地 2,460 m³','bad')}</td><td>—</td></tr>
<tr><td>12:00–16:00</td><td>{tag('二号地 960 m³','blue')}</td><td>{tag('三号地 1,240 m³','sky')}</td><td>—</td><td>—</td></tr>
<tr><td>16:00–20:00</td><td>—</td><td>—</td><td>{tag('容量冲突','bad')}</td><td>{tag('五号地 480 m³','ok')}</td></tr>
</tbody></table></div></div></div>"""


def task_body():
    return """<h1 class="title">执行任务</h1>
<p class="sub">放水员现场录入开始/结束表数、实际水量与照片；结束表数不得小于开始表数</p>
<div style="display:flex;gap:24px;align-items:flex-start">
<div class="phone">
  <div class="ph"><span>任务 TK-20261031-021</span><span style="font-size:12px">放水员 · 刘卫东</span></div>
  <div class="pb">
    <div class="mcard">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
        <b style="font-size:15px">北干渠一号地</b><span class="tag sky">进行中</span></div>
      <div style="font-size:13px;color:#5A6B78;line-height:1.9">
        计划时段：10-31 08:00 ~ 12:00<br>计划水量：1,860 m³ · 渠道：北干渠 2# 闸<br>作物：水稻 / 分蘖期 · 责任人：李国强</div>
    </div>
    <div class="mcard">
      <div style="font-weight:600;margin-bottom:12px;font-size:14px">表数录入</div>
      <div style="display:flex;flex-direction:column;gap:10px">
        <div><label style="font-size:12.5px;color:#5A6B78">开始表数 (m³)</label>
          <input value="12480.5" style="width:100%;margin-top:4px"></div>
        <div><label style="font-size:12.5px;color:#5A6B78">结束表数 (m³)</label>
          <input value="14210.0" style="width:100%;margin-top:4px"></div>
        <div style="background:#EAF2F8;border-radius:6px;padding:10px;font-size:13px">
          实际水量 <b style="font-variant-numeric:tabular-nums">1,729.5 m³</b>
          <span style="color:#B4761E">（低于计划 7.0%）</span></div>
        <div><label style="font-size:12.5px;color:#5A6B78">现场照片</label>
          <div style="display:flex;gap:8px;margin-top:6px">
            <div style="width:68px;height:52px;border:1px dashed #C9D8E4;border-radius:6px;display:grid;place-items:center;color:#8FA5B5;font-size:11px">已上传</div>
            <div style="width:68px;height:52px;border:1px dashed #C9D8E4;border-radius:6px;display:grid;place-items:center;color:#8FA5B5;font-size:11px">+ 拍照</div>
          </div></div>
      </div>
    </div>
    <div class="mcard" style="margin-bottom:0">
      <div style="font-weight:600;margin-bottom:10px;font-size:14px">异常上报</div>
      <select style="width:100%"><option>无异常</option><option>渠道堵塞</option><option>漏水</option><option>设备故障</option><option>水量不足</option></select>
      <textarea placeholder="中断需填写原因，不少于 5 个字" style="width:100%;height:60px;margin-top:8px;border:1px solid #DCE6EE;border-radius:6px;padding:8px;font-family:inherit;font-size:13px"></textarea>
    </div>
  </div>
  <div class="pfoot"><button class="btn ghost" style="flex:0 0 96px">中断</button><button class="btn">提交完成</button></div>
</div>
<div style="flex:1;min-width:0">
  <div class="card"><div class="card-hd"><span>任务时间轴</span></div><div class="card-bd">
    <ul class="tl">
      <li><b>任务下达</b><span>10-31 07:40 · 调度员 王海涛 · 计划 PL-20261031-012</span></li>
      <li><b>开始执行</b><span>10-31 08:06 · 放水员 刘卫东 · 开始表数 12,480.5</span></li>
      <li><b>现场签到</b><span>10-31 08:09 · 定位偏差 12 m · 已附照片 1 张</span></li>
      <li><b>用量复核</b><span>待提交后由灌区管理员确认</span></li>
    </ul></div></div>
  <div class="card"><div class="card-hd"><span>今日待执行</span></div><div class="card-bd">
    <table><thead><tr><th>任务号</th><th>地块</th><th>时段</th><th>状态</th></tr></thead><tbody>
    <tr><td>TK-20261031-021</td><td>北干渠一号地</td><td>08:00–12:00</td><td><span class="tag sky">进行中</span></td></tr>
    <tr><td>TK-20261031-022</td><td>东支渠三号地</td><td>13:00–16:30</td><td><span class="tag blue">待执行</span></td></tr>
    <tr><td>TK-20261031-023</td><td>南干渠七号地</td><td>16:00–21:00</td><td><span class="tag bad">已中断</span></td></tr>
    </tbody></table></div></div>
</div></div>"""


def advice_body():
    return """<h1 class="title">用量确认单 · 作物阶段用水建议</h1>
<p class="sub">任务 TK-20261031-021 · 北干渠一号地 · 规则版本 v3（2026-09-15 生效）</p>
<div style="display:grid;grid-template-columns:1.15fr 1fr;gap:16px;align-items:start">
<div>
  <div class="card"><div class="card-hd"><span>输入依据</span><span class="tag blue">6 项因素</span></div><div class="card-bd">
    <table><thead><tr><th>因素</th><th>取值</th><th>来源</th><th>权重</th></tr></thead><tbody>
    <tr><td>作物类型</td><td>水稻</td><td>地块档案</td><td class="num">24%</td></tr>
    <tr><td>生育阶段</td><td>分蘖期</td><td>地块档案</td><td class="num">22%</td></tr>
    <tr><td>地块面积</td><td>182.40 亩</td><td>地块档案</td><td class="num">18%</td></tr>
    <tr><td>土壤等级</td><td>壤土 · 保水二级</td><td>土壤字典</td><td class="num">14%</td></tr>
    <tr><td>近期降雨</td><td>18.6 mm / 7 天</td><td>手工录入</td><td class="num">12%</td></tr>
    <tr><td>历史单耗</td><td>46.2 m³/亩</td><td>近 3 年记录</td><td class="num">10%</td></tr>
    </tbody></table>
    <div style="font-size:12.5px;color:#5A6B78;margin-top:10px">权重合计 100% · 计算时间 2026-10-31 08:02:14 · 快照 ID SNAP-4471</div>
  </div></div>
  <div class="card"><div class="card-hd"><span>计算明细</span></div><div class="card-bd">
    <div class="hbar">
      <div class="row"><span>作物需水</span><div class="tr"><i style="width:88%"></i></div><b>88.0</b></div>
      <div class="row"><span>阶段系数</span><div class="tr"><i style="width:76%"></i></div><b>76.0</b></div>
      <div class="row"><span>面积修正</span><div class="tr"><i style="width:64%"></i></div><b>64.0</b></div>
      <div class="row"><span>土壤保水</span><div class="tr"><i style="width:52%"></i></div><b>52.0</b></div>
      <div class="row"><span>降雨折减</span><div class="tr"><i style="width:41%"></i></div><b>41.0</b></div>
      <div class="row"><span>历史校准</span><div class="tr"><i style="width:70%"></i></div><b>70.0</b></div>
    </div>
  </div></div>
</div>
<div>
  <div class="card"><div class="card-hd"><span>推荐结果</span><span class="tag warn">需复核</span></div><div class="card-bd">
    <div style="display:flex;gap:24px;align-items:flex-end;margin-bottom:14px">
      <div><div style="font-size:12.5px;color:#5A6B78">建议用水量</div>
        <div style="font-size:32px;font-weight:600;font-variant-numeric:tabular-nums;color:#0F3B5D">1,782<small style="font-size:13px;font-weight:400"> m³</small></div></div>
      <div><div style="font-size:12.5px;color:#5A6B78">定额水量</div>
        <div style="font-size:22px;font-weight:600;font-variant-numeric:tabular-nums">1,860 m³</div></div>
      <div><div style="font-size:12.5px;color:#5A6B78">偏差</div>
        <div style="font-size:22px;font-weight:600;color:#B4761E">-4.2%</div></div>
    </div>
    <div class="kv"><dt>主要影响因素</dt><dd>分蘖期需水系数偏高；近 7 天降雨 18.6 mm 已折减</dd></div>
    <div class="kv"><dt>未满足条件</dt><dd>土壤保水等级为二级，蒸发损失高于一级地块</dd></div>
    <div class="kv"><dt>可改进项</dt><dd>建议改为傍晚时段灌溉，可减少约 6% 蒸发损失</dd></div>
    <div class="kv" style="border:0"><dt>结果等级</dt><dd><span class="tag warn">需复核</span> 偏差介于 -5% ~ +5% 区间外沿</dd></div>
  </div></div>
  <div class="card"><div class="card-hd"><span>人工修正</span></div><div class="card-bd">
    <div style="font-size:13px;color:#5A6B78;margin-bottom:10px">原始计算结果不可覆盖，修正需填写原因并留痕</div>
    <div class="grid2">
      <div class="field"><label>修正后水量 (m³)</label><input class="wide" value="1800"></div>
      <div class="field"><label>修正原因</label><input class="wide" placeholder="不少于 5 个字"></div>
    </div>
    <div style="margin-top:14px"><button class="btn">提交修正</button> <button class="btn ghost">重新计算</button></div>
    <div style="margin-top:14px;font-size:12.5px;color:#5A6B78">历史修正：10-30 由王海涛调整为 1,800 m³，原因「渠道末段水头不足需补量」</div>
  </div></div>
</div></div>"""


def application_body():
    rows = [
        ("AP-20261031-021", "北干渠一号地", "水稻 / 分蘖期", "10-31", "1,900", "紧急", "待审核", "blue"),
        ("AP-20261031-020", "东支渠三号地", "玉米 / 苗期", "11-01", "1,200", "普通", "待排程", "sky"),
        ("AP-20261030-018", "南干渠七号地", "水稻 / 孕穗期", "10-30", "2,500", "紧急", "已安排", "ok"),
        ("AP-20261030-017", "西支渠五号地", "蔬菜 / 结果期", "10-30", "  460", "普通", "已驳回", "bad"),
    ]
    tr = "".join(
        f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td><td class='num'>{e}</td><td>{f}</td>"
        f"<td>{tag(g, k)}</td><td><a href='#〰'>详情</a> · <a href='#〰'>审核</a></td></tr>"
        for a, b, c, d, e, f, g, k in rows
    )
    return f"""<h1 class="title">用水申请</h1>
<p class="sub">种植户提交申请 → 灌区管理员审核 → 调度员排程；紧急申请优先占用当日剩余容量</p>
<div class="card"><div class="card-bd">
  <div class="filters">
    <div class="field"><label>状态</label><select><option>全部状态</option><option>待审核</option><option>待排程</option><option>已安排</option><option>已驳回</option></select></div>
    <div class="field"><label>地块</label><select><option>全部地块</option><option>北干渠一号地</option></select></div>
    <div class="field"><label>期望日期</label><input type="date" value="2026-10-31"></div>
    <button class="btn">查询</button><button class="btn ghost">重置</button>
    <button class="btn" style="margin-left:auto">提交申请</button>
  </div>
  <div class="tw"><table><thead><tr><th>申请编号</th><th>地块</th><th>作物/阶段</th><th>期望日期</th>
  <th>申请水量(m³)</th><th>紧急程度</th><th>状态</th><th>操作</th></tr></thead><tbody>{tr}</tbody></table></div>
  <div class="pager"><span>共 48 条</span><div class="pages"><span>‹</span><span class="on">1</span><span>2</span><span>3</span><span>›</span></div></div>
</div></div>
<div class="drawer" style="position:static;width:auto;box-shadow:none;border:1px solid #DCE6EE;border-radius:8px;margin-top:16px">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
    <b style="font-size:15px">审核 · AP-20261031-021</b><span class="tag blue">待审核</span></div>
  <dl style="margin-bottom:14px">
    <div class="kv"><dt>地块</dt><dd>北干渠一号地 · 182.40 亩</dd></div>
    <div class="kv"><dt>作物阶段</dt><dd>水稻 / 分蘖期</dd></div>
    <div class="kv"><dt>申请水量</dt><dd>1,900 m³（定额余量 2,240 m³）</dd></div>
    <div class="kv"><dt>期望日期</dt><dd>2026-10-31 · 紧急</dd></div>
  </dl>
  <div class="field"><label>审核意见</label><input class="wide" placeholder="驳回时必填，不少于 5 个字"></div>
  <div style="margin-top:14px;display:flex;gap:10px">
    <button class="btn">通过并转排程</button><button class="btn danger">驳回</button><button class="btn ghost">取消</button></div>
</div>"""


def quota_body():
    return """<h1 class="title">水权定额</h1>
<p class="sub">按年度、地块或种植户分配用水定额，系统按已确认用水量计算已用与剩余</p>
<div class="kpis" style="grid-template-columns:repeat(4,1fr)">
  <div class="kpi"><div class="lb">2026 年度定额总量</div><div class="vl">486,200<small>m³</small></div></div>
  <div class="kpi"><div class="lb">已用水量</div><div class="vl">318,640<small>m³</small></div><div class="dt">使用率 65.5%</div></div>
  <div class="kpi"><div class="lb">剩余可用</div><div class="vl">167,560<small>m³</small></div></div>
  <div class="kpi"><div class="lb">超额地块</div><div class="vl" style="color:#B22B31">4<small>块</small></div><div class="dt warn">已触发加价计费</div></div>
</div>
<div class="card"><div class="card-hd"><span>定额分配表</span><span style="font-weight:400;font-size:13px">
  <select style="height:28px;font-size:12.5px"><option>2026 年度</option><option>2025 年度</option></select>
  <button class="btn sm" style="margin-left:8px">分配定额</button></span></div>
<div class="card-bd" style="padding-top:0"><div class="tw"><table>
<thead><tr><th>地块</th><th>种植户</th><th>年度</th><th>定额(m³)</th><th>已用(m³)</th><th>剩余(m³)</th><th>使用率</th><th>状态</th></tr></thead><tbody>
<tr><td>北干渠一号地</td><td>李国强</td><td>2026</td><td class="num">4,200</td><td class="num">1,960</td><td class="num">2,240</td><td class="num">46.7%</td><td><span class="tag ok">正常</span></td></tr>
<tr><td>北干渠二号地</td><td>王秀兰</td><td>2026</td><td class="num">2,400</td><td class="num">2,310</td><td class="num">90</td><td class="num">96.3%</td><td><span class="tag warn">余量不足</span></td></tr>
<tr><td>东支渠三号地</td><td>赵德海</td><td>2026</td><td class="num">5,600</td><td class="num">3,180</td><td class="num">2,420</td><td class="num">56.8%</td><td><span class="tag ok">正常</span></td></tr>
<tr><td>南干渠七号地</td><td>孙立平</td><td>2026</td><td class="num">6,800</td><td class="num">7,120</td><td class="num" style="color:#B22B31">-320</td><td class="num">104.7%</td><td><span class="tag bad">已超额</span></td></tr>
<tr><td>西支渠五号地</td><td>陈志远</td><td>2026</td><td class="num">1,800</td><td class="num">760</td><td class="num">1,040</td><td class="num">42.2%</td><td><span class="tag ok">正常</span></td></tr>
</tbody></table></div>
<div class="pager"><span>共 126 条 · 每页 10 条</span><div class="pages"><span>‹</span><span class="on">1</span><span>2</span><span>›</span></div></div>
</div></div>"""


def fee_body():
    return """<h1 class="title">费用台账</h1>
<p class="sub">按实际用水量与分段单价核算；定额内执行基础价，超额部分加价 30%</p>
<div class="card"><div class="card-bd">
  <div class="filters">
    <div class="field"><label>计费月份</label><input type="month" value="2026-10"></div>
    <div class="field"><label>缴费状态</label><select><option>全部</option><option>待缴费</option><option>已缴费</option><option>已减免</option></select></div>
    <button class="btn">查询</button><button class="btn ghost">导出</button>
  </div>
  <div style="background:#EAF2F8;border-radius:6px;padding:10px 14px;font-size:12.5px;margin-bottom:14px;color:#245A7A">
    计费规则：基础水价 0.42 元/m³（定额内）· 超额水价 0.55 元/m³ · 免费定额 30 m³/亩/年
  </div>
  <div class="tw"><table><thead><tr><th>费用单号</th><th>地块</th><th>任务号</th><th>实际水量(m³)</th>
  <th>定额内(m³)</th><th>超额(m³)</th><th>金额(元)</th><th>状态</th><th>操作</th></tr></thead><tbody>
  <tr><td>FE-20261031-018</td><td>北干渠一号地</td><td>TK-20261031-021</td><td class="num">1,729.5</td><td class="num">1,729.5</td><td class="num">0</td><td class="num">726.39</td><td><span class="tag blue">待缴费</span></td><td><a href="#〰">详情</a></td></tr>
  <tr><td>FE-20261030-016</td><td>南干渠七号地</td><td>TK-20261030-018</td><td class="num">2,860.0</td><td class="num">2,400.0</td><td class="num" style="color:#B22B31">460.0</td><td class="num">1,261.00</td><td><span class="tag warn">超额加价</span></td><td><a href="#〰">详情</a></td></tr>
  <tr><td>FE-20261030-015</td><td>西支渠五号地</td><td>TK-20261030-015</td><td class="num">468.0</td><td class="num">468.0</td><td class="num">0</td><td class="num">196.56</td><td><span class="tag ok">已缴费</span></td><td><a href="#〰">详情</a></td></tr>
  <tr><td>FE-20261029-012</td><td>北干渠二号地</td><td>TK-20261029-011</td><td class="num">942.0</td><td class="num">942.0</td><td class="num">0</td><td class="num">395.64</td><td><span class="tag ok">已缴费</span></td><td><a href="#〰">详情</a></td></tr>
  </tbody></table></div>
  <div class="pager"><span>合计 1,2xx 条 · 本月应收 38,420.60 元</span><div class="pages"><span>‹</span><span class="on">1</span><span>2</span><span>3</span><span>›</span></div></div>
</div></div>"""


def source_body():
    return """<h1 class="title">水源与渠道</h1>
<p class="sub">维护水源可用量、干支渠设计流量与闸口启闭状态，供计划编制时做容量校验</p>
<div class="card"><div class="card-hd"><span>水源台账</span><button class="btn sm">新增水源</button></div>
<div class="card-bd" style="padding-top:0"><div class="tw"><table>
<thead><tr><th>水源编号</th><th>水源名称</th><th>类型</th><th>设计供水(m³/日)</th><th>当前可用(m³)</th><th>负责人</th><th>状态</th></tr></thead><tbody>
<tr><td>WS-01</td><td>北干渠水库</td><td>水库</td><td class="num">12,000</td><td class="num">8,640</td><td>王海涛</td><td><span class="tag ok">正常</span></td></tr>
<tr><td>WS-02</td><td>东支渠机井群</td><td>机井</td><td class="num">3,600</td><td class="num">2,140</td><td>赵德海</td><td><span class="tag ok">正常</span></td></tr>
<tr><td>WS-03</td><td>南干渠引水口</td><td>河道</td><td class="num">9,000</td><td class="num">3,200</td><td>孙立平</td><td><span class="tag warn">来水偏少</span></td></tr>
<tr><td>WS-04</td><td>西支渠塘坝</td><td>塘坝</td><td class="num">1,800</td><td class="num">0</td><td>陈志远</td><td><span class="tag bad">停用检修</span></td></tr>
</tbody></table></div></div></div>
<div class="card"><div class="card-hd"><span>干支渠与闸口</span></div><div class="card-bd" style="padding-top:0">
<div class="tw"><table><thead><tr><th>渠道编号</th><th>渠道名称</th><th>所属水源</th><th>渠段</th><th>设计流量(m³/s)</th><th>闸口</th><th>闸口状态</th></tr></thead><tbody>
<tr><td>CN-01</td><td>北干渠</td><td>北干渠水库</td><td>干渠</td><td class="num">1.20</td><td>1# / 2# / 3#</td><td><span class="tag ok">正常</span></td></tr>
<tr><td>CN-02</td><td>东支渠</td><td>东支渠机井群</td><td>支渠</td><td class="num">0.45</td><td>1# / 2#</td><td><span class="tag ok">正常</span></td></tr>
<tr><td>CN-03</td><td>南干渠</td><td>南干渠引水口</td><td>干渠</td><td class="num">0.35</td><td>4# / 5#</td><td><span class="tag warn">限流</span></td></tr>
<tr><td>CN-04</td><td>西支渠</td><td>西支渠塘坝</td><td>支渠</td><td class="num">0.20</td><td>3#</td><td><span class="tag bad">关闭</span></td></tr>
</tbody></table></div></div></div>"""


def system_body():
    return """<h1 class="title">系统管理</h1>
<p class="sub">用户、角色、菜单与数据范围分离控制；只有菜单权限不能直接调用写接口</p>
<div class="card"><div class="card-hd"><span>用户与角色</span><span style="font-weight:400;font-size:13px">
  <input placeholder="搜索姓名 / 账号" style="height:28px;width:180px"><button class="btn sm" style="margin-left:8px">新增用户</button></span></div>
<div class="card-bd" style="padding-top:0"><div class="tw"><table>
<thead><tr><th>账号</th><th>姓名</th><th>角色</th><th>所属部门</th><th>数据范围</th><th>状态</th><th>操作</th></tr></thead><tbody>
<tr><td>admin</td><td>张建民</td><td>灌区管理员</td><td>灌区管理所</td><td>全部</td><td><span class="tag ok">启用</span></td><td><a href="#〰">编辑</a> · <a href="#〰">重置密码</a></td></tr>
<tr><td>dispatcher01</td><td>王海涛</td><td>调度员</td><td>调度中心</td><td>本部门</td><td><span class="tag ok">启用</span></td><td><a href="#〰">编辑</a></td></tr>
<tr><td>operator01</td><td>刘卫东</td><td>放水员</td><td>北干渠站</td><td>仅本人</td><td><span class="tag ok">启用</span></td><td><a href="#〰">编辑</a></td></tr>
<tr><td>farmer01</td><td>李国强</td><td>种植户</td><td>北干渠片区</td><td>仅本人</td><td><span class="tag ok">启用</span></td><td><a href="#〰">编辑</a></td></tr>
</tbody></table></div></div></div>
<div class="card"><div class="card-hd"><span>角色菜单授权</span></div><div class="card-bd">
<div style="display:flex;gap:20px">
  <div style="width:180px;border-right:1px solid #DCE6EE">
    <div style="font-size:13px;color:#5A6B78;margin-bottom:8px">角色</div>
    <div class="tag blue" style="display:block;margin-bottom:6px">灌区管理员</div>
    <div style="padding:6px 8px;font-size:13px">调度员</div>
    <div style="padding:6px 8px;font-size:13px">放水员</div>
    <div style="padding:6px 8px;font-size:13px">种植户</div>
  </div>
  <div style="flex:1">
    <table><thead><tr><th>菜单</th><th>查看</th><th>新增</th><th>编辑</th><th>删除</th><th>审批</th></tr></thead><tbody>
    <tr><td>农业用水分析</td><td>✓</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
    <tr><td>地块用水地图</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>—</td></tr>
    <tr><td>灌溉计划</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td></tr>
    <tr><td>费用台账</td><td>✓</td><td>—</td><td>✓</td><td>—</td><td>✓</td></tr>
    </tbody></table>
    <div style="margin-top:12px"><button class="btn">保存授权</button></div>
  </div>
</div></div></div>"""


def farmer_body():
    return f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>我的农田 · 种植户门户</title><link rel="stylesheet" href="mock.css">
<style>body{{display:block;background:#F4F8FB}}</style></head><body>
<header class="portal-top"><div style="display:flex;align-items:center;gap:32px">
  <b style="font-size:17px;color:#0F3B5D">灌溉用水 · 种植户</b>
  <nav class="nav"><a class="on" href="farmer.html">我的地块</a><a href="application.html">用水申请</a>
  <a href="fee.html">我的费用</a><a href="advice.html">用水建议</a></nav></div>
  <div style="display:flex;align-items:center;gap:14px;font-size:13px;color:#5A6B78">
    <span>消息</span><div class="avatar">李</div><span>李国强</span></div></header>
<div class="portal-body">
  <div class="hero"><h2>北干渠片区 · 李国强</h2>
    <p>2026 年度定额 4,200 m³，已使用 1,960 m³，剩余 2,240 m³（使用率 46.7%）</p>
    <div class="stat"><div><b>2</b><span>承包地块</span></div><div><b>274.4</b><span>灌溉面积（亩）</span></div>
    <div><b>3</b><span>本年灌溉次数</span></div><div><b>1,268.4</b><span>本年费用（元）</span></div></div></div>
  <div class="cards3" style="margin-bottom:16px">
    <div class="mini"><h3>北干渠一号地</h3><p>水稻 · 分蘖期 · 182.40 亩<br>定额余量 2,240 m³ · 土壤：壤土</p><a class="go" href="application.html">申请用水 →</a></div>
    <div class="mini"><h3>北干渠二号地</h3><p>小麦 · 拔节期 · 92.00 亩<br>定额余量 90 m³ · <span style="color:#B4761E">余量不足</span></p><a class="go" href="application.html">申请用水 →</a></div>
    <div class="mini"><h3>待办提醒</h3><p>1 条用水申请待审核<br>1 条费用待缴纳（726.39 元）</p><a class="go" href="fee.html">查看费用 →</a></div>
  </div>
  <div class="card"><div class="card-hd"><span>最近灌溉记录</span><a href="#" style="font-weight:400;font-size:13px">全部记录</a></div>
  <div class="card-bd" style="padding-top:0"><div class="tw"><table>
  <thead><tr><th>任务号</th><th>地块</th><th>执行时段</th><th>实际水量(m³)</th><th>费用(元)</th><th>状态</th></tr></thead><tbody>
  <tr><td>TK-20261031-021</td><td>北干渠一号地</td><td>10-31 08:00–12:00</td><td class="num">1,729.5</td><td class="num">726.39</td><td>{tag('已完成','ok')}</td></tr>
  <tr><td>TK-20261018-014</td><td>北干渠一号地</td><td>10-18 07:30–11:00</td><td class="num">1,486.0</td><td class="num">624.12</td><td>{tag('已完成','ok')}</td></tr>
  <tr><td>TK-20261005-007</td><td>北干渠二号地</td><td>10-05 14:00–17:00</td><td class="num">942.0</td><td class="num">395.64</td><td>{tag('已完成','ok')}</td></tr>
  </tbody></table></div></div></div>
</div></body></html>"""


def login_body():
    return """<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>登录 · 农田灌溉计划与用水统计系统</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;min-height:100vh;display:grid;
  grid-template-columns:1.05fr .95fr;background:#F4F8FB;color:#1D2A33}
.left{background:linear-gradient(150deg,#0F3B5D 0%,#1B4F73 55%,#245A7A 100%);color:#fff;
  padding:56px;display:flex;flex-direction:column;justify-content:space-between;position:relative;overflow:hidden}
.left::after{content:"";position:absolute;right:-90px;bottom:-110px;width:380px;height:380px;
  border:1px solid rgba(255,255,255,.13);border-radius:50%}
.brand{display:flex;align-items:center;gap:10px;font-size:16px;font-weight:600;letter-spacing:.5px}
.left h1{font-size:34px;line-height:1.35;font-weight:600;margin:0 0 16px}
.left p{font-size:14px;color:rgba(255,255,255,.72);line-height:1.9;max-width:400px}
.facts{display:flex;gap:36px}
.facts div b{display:block;font-size:26px;font-weight:600;font-variant-numeric:tabular-nums}
.facts div span{font-size:12.5px;color:rgba(255,255,255,.6)}
.right{display:grid;place-items:center;padding:40px}
.card{width:380px}
.card h2{font-size:22px;font-weight:600;margin-bottom:6px}
.card .tip{font-size:13px;color:#5A6B78;margin-bottom:26px}
label{font-size:13px;color:#5A6B78;display:block;margin-bottom:6px}
input{width:100%;height:42px;border:1px solid #DCE6EE;border-radius:6px;padding:0 12px;font-size:14px;
  margin-bottom:16px;font-family:inherit}
input:focus{outline:2px solid #2878B5;outline-offset:-1px;border-color:#2878B5}
.btn{width:100%;height:42px;border:0;border-radius:6px;background:#0F3B5D;color:#fff;font-size:14.5px;
  font-weight:500;cursor:pointer;font-family:inherit}
.row{display:flex;justify-content:space-between;font-size:13px;color:#5A6B78;margin-bottom:20px}
a{color:#245A7A;text-decoration:none}
.roles{display:flex;gap:8px;margin-top:22px;font-size:12px;color:#5A6B78}
.roles span{padding:3px 9px;border:1px solid #DCE6EE;border-radius:4px;background:#fff}
</style></head><body>
<div class="left">
  <div class="brand"><svg width="22" height="22" viewBox="0 0 24 24"><path d="M12 3s6 6.5 6 11a6 6 0 11-12 0c0-4.5 6-11 6-11z" fill="#7FB3D5"/></svg>
    灌区用水管理平台</div>
  <div><h1>把每一方水<br>都算到地块上</h1>
    <p>水源、渠道、闸口、水表一体化台账；计划排程自动校验闸口容量；抄表数据驱动定额扣减与分段计费。</p></div>
  <div class="facts"><div><b>1.2 万亩</b><span>覆盖灌溉面积</span></div>
    <div><b>126</b><span>在册地块</span></div><div><b>98.4%</b><span>计划完成率</span></div></div>
</div>
<div class="right"><div class="card">
  <h2>登录</h2><div class="tip">使用灌区分配的账号登录，连续 5 次失败将锁定 10 分钟</div>
  <label>账号</label><input value="admin" placeholder="请输入账号">
  <label>密码</label><input type="password" value="admin123" placeholder="请输入密码">
  <div class="row"><span><input type="checkbox" style="width:auto;height:auto;margin-right:6px">记住账号</span><a href="#">忘记密码</a></div>
  <button class="btn">登录</button>
  <div class="roles"><span>管理员 admin</span><span>调度员 dispatcher01</span><span>放水员 operator01</span><span>种植户 farmer01</span></div>
</div></div></body></html>"""


def index_page():
    cards = [
        ("dashboard.html", "农业用水分析", "管理员 · 6 指标 + 6 图表，一屏内"),
        ("farmland.html", "地块用水地图", "管理员 · 条件区 + 摘要 + 表格"),
        ("application.html", "用水申请", "种植户/管理员 · 审核抽屉"),
        ("plan.html", "灌溉计划编制", "调度员 · 状态标签 + 日历排程"),
        ("task.html", "执行任务", "放水员 · 移动端执行页"),
        ("advice.html", "用量确认单", "创新点 · 建议 + 计算明细 + 人工修正"),
        ("quota.html", "水权定额", "管理员 · 已用/剩余实时计算"),
        ("fee.html", "费用台账", "管理员 · 分段计费"),
        ("source.html", "水源与渠道", "管理员 · 台账维护"),
        ("system.html", "系统管理", "管理员 · 用户/角色/菜单"),
        ("farmer.html", "种植户门户", "种植户 · 前台门户"),
        ("login.html", "登录页", "全角色 · 主题化登录"),
    ]
    lis = "".join(
        f'<a class="mini" href="{u}" style="display:block"><h3>{t}</h3><p>{d}</p></a>' for u, t, d in cards
    )
    return f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<title>原型索引 · 农田灌溉计划与用水统计系统</title><link rel="stylesheet" href="mock.css">
<style>body{{display:block}}.wrap{{max-width:1100px;margin:0 auto;padding:36px 24px}}
h1{{font-size:24px;margin-bottom:6px}}p.lead{{color:#5A6B78;margin-bottom:24px}}</style></head><body><div class="wrap">
<h1>农田灌溉计划与用水统计系统 · 原型索引</h1>
<p class="lead">编号 NEW-017 · 四角色（灌区管理员 / 调度员 / 放水员 / 种植户）· 共 12 个可点击页面</p>
<div class="cards3">{lis}</div></div></body></html>"""


pages = {
    "index.html": index_page(),
    "login.html": login_body(),
    "farmer.html": farmer_body(),
    "dashboard.html": shell("农业用水分析", "农业用水分析", "dashboard", dashboard_body()),
    "farmland.html": shell("地块用水地图", "地块用水地图", "farmland", farmland_body()),
    "application.html": shell("用水申请", "用水申请", "application", application_body()),
    "plan.html": shell("灌溉计划编制", "灌溉计划", "plan", plan_body()),
    "task.html": shell("执行任务", "执行任务", "task", task_body()),
    "advice.html": shell("用量确认单", "用量确认单", "advice", advice_body()),
    "quota.html": shell("水权定额", "水权定额", "quota", quota_body()),
    "fee.html": shell("费用台账", "费用台账", "fee", fee_body()),
    "source.html": shell("水源与渠道", "水源与渠道", "source", source_body()),
    "system.html": shell("系统管理", "系统管理", "system", system_body()),
}

for name, html in pages.items():
    (OUT / name).write_text(html)

# 每页一份独立设计稿（等效 HTML 稿）
for name, html in pages.items():
    (OUT / "pages" / name).write_text(html)

print("生成页面数：", len(pages))
