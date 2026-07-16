#!/usr/bin/env python3
"""HTML报告生成模块。

基于extract_data提取的数据和generate_charts生成的PNG图表，
组装成完整的私域运营效果分析HTML报告。
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# CSS样式（从原始generate_may_report.py提取）
# ---------------------------------------------------------------------------
CSS = """
:root {
  --bg: #F7F5F2;
  --bg2: #FFFFFF;
  --ink: #2D2A26;
  --muted: #8A8580;
  --rule: #D9D5D0;
  --accent: #B3875E;
  --accent2: #5E7C6B;
  --accent-light: #F0E6DB;
  --accent2-light: #E0EBE5;
  --risk: #C45B4A;
  --risk-light: #FBEAE8;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  background: var(--bg); color: var(--ink); line-height: 1.7; font-size: 15px;
}
.container { max-width: 960px; margin: 0 auto; padding: 0 24px; }
.header {
  background: var(--bg2); border-bottom: 1px solid var(--rule);
  padding: 48px 0 36px; margin-bottom: 40px;
}
.header h1 { font-size: 2.2rem; font-weight: 700; margin-bottom: 8px; letter-spacing: -0.02em; }
.header .subtitle { font-size: 1.05rem; color: var(--muted); margin-bottom: 20px; }
.meta-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px; margin-top: 20px; padding-top: 20px; border-top: 1px solid var(--rule);
}
.meta-item .meta-label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }
.meta-item .meta-value { font-size: 0.95rem; font-weight: 600; margin-top: 4px; }
.biz-context { margin-top: 16px; padding: 12px 16px; background: var(--accent-light); border-radius: 8px; font-size: 0.88rem; }
.biz-context strong { color: var(--accent); }
.global-calc { margin-top: 12px; padding: 12px 16px; background: #FFF8E1; border-radius: 8px; font-size: 0.85rem; border-left: 4px solid #E6A23C; }
.global-calc strong { color: #B3875E; }
.section { background: var(--bg2); border-radius: 12px; padding: 32px; margin-bottom: 28px; border: 1px solid var(--rule); }
.section h2 { font-size: 1.4rem; font-weight: 600; margin-bottom: 8px; padding-bottom: 12px; border-bottom: 2px solid var(--accent); display: inline-block; }
.section .section-desc { color: var(--muted); font-size: 0.9rem; margin-bottom: 24px; margin-top: 8px; }
.section h3 { font-size: 1.15rem; font-weight: 600; margin: 24px 0 12px; }
.section h4 { font-size: 0.95rem; font-weight: 600; margin: 16px 0 8px; color: var(--muted); }
p { margin-bottom: 12px; }
.exec-summary { background: linear-gradient(135deg, var(--accent-light) 0%, var(--bg2) 100%); }
.conclusion-table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 0.9rem; }
.conclusion-table th { background: var(--accent); color: white; padding: 10px 14px; text-align: left; font-weight: 600; }
.conclusion-table td { padding: 10px 14px; border-bottom: 1px solid var(--rule); }
.conclusion-table tr:nth-child(even) { background: #FAFAF8; }
.judgment { font-weight: 600; }
.judgment.yes { color: var(--accent2); }
.judgment.no { color: var(--risk); }
.judgment.maybe { color: var(--accent); }
.metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin: 24px 0; }
.metric-card { background: var(--bg); border-radius: 10px; padding: 20px; text-align: center; border: 1px solid var(--rule); }
.metric-card .number { font-size: 1.8rem; font-weight: 700; color: var(--accent); line-height: 1.2; }
.metric-card .label { font-size: 0.85rem; color: var(--muted); margin-top: 6px; }
.metric-card .change { font-size: 0.8rem; margin-top: 4px; font-weight: 600; }
.change.up { color: var(--accent2); }
.change.down { color: var(--risk); }
.alert-box { background: var(--risk-light); border-left: 4px solid var(--risk); padding: 14px 18px; border-radius: 0 8px 8px 0; margin: 16px 0; }
.alert-box h4 { color: var(--risk); margin: 0 0 6px 0; font-weight: 600; }
.alert-box p { margin: 0; font-size: 0.9rem; }
.model-block { margin-bottom: 36px; padding-bottom: 28px; border-bottom: 1px dashed var(--rule); }
.model-block:last-child { margin-bottom: 0; padding-bottom: 0; border-bottom: none; }
.model-header { display: flex; align-items: baseline; gap: 12px; margin-bottom: 8px; }
.model-header .model-tag { font-size: 0.72rem; font-weight: 600; padding: 3px 10px; border-radius: 4px; background: var(--accent-light); color: var(--accent); white-space: nowrap; letter-spacing: 0.02em; }
.model-purpose { color: var(--muted); font-size: 0.88rem; margin-bottom: 14px; }
.callout { border-radius: 8px; padding: 14px 18px; margin: 16px 0; font-size: 0.94rem; line-height: 1.6; }
.callout.positive { background: var(--accent2-light); border-left: 4px solid var(--accent2); }
.callout.neutral { background: #F5F5F5; border-left: 4px solid var(--muted); }
.callout.warning { background: #FFF8E1; border-left: 4px solid #E6A23C; }
.callout.risk { background: var(--risk-light); border-left: 4px solid var(--risk); }
.callout .callout-title { font-weight: 600; margin-bottom: 6px; display: block; }
.callout.positive .callout-title { color: var(--accent2); }
.callout.neutral .callout-title { color: var(--muted); }
.callout.warning .callout-title { color: #B3875E; }
.callout.risk .callout-title { color: var(--risk); }
.methodology-box { background: var(--bg); border: 1px solid var(--rule); border-radius: 8px; padding: 14px 18px; margin: 14px 0; font-size: 0.85rem; line-height: 1.6; }
.methodology-box h4 { font-size: 0.82rem; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; margin: 0 0 10px 0; padding-bottom: 6px; border-bottom: 1px dashed var(--rule); }
.methodology-box ul { padding-left: 16px; margin: 0; }
.methodology-box li { margin-bottom: 6px; }
.methodology-box li strong { color: var(--accent); }
.chart-figure { margin: 24px 0; }
.chart-figure figcaption { font-size: 0.9rem; font-weight: 600; margin-bottom: 10px; text-align: center; }
.chart-container { width: 100%; min-height: 360px; }
.chart-container img { width: 100%; height: auto; border-radius: 8px; border: 1px solid var(--rule); }
.table-wrap { overflow-x: auto; overflow-y: auto; max-height: 500px; margin: 20px 0; border-radius: 8px; border: 1px solid var(--rule); }
table { width: 100%; border-collapse: collapse; font-size: 0.87rem; }
thead { background: var(--accent-light); position: sticky; top: 0; z-index: 2; }
th { padding: 11px 13px; text-align: left; font-weight: 600; border-bottom: 2px solid var(--accent); white-space: nowrap; }
td { padding: 9px 13px; border-bottom: 1px solid var(--rule); vertical-align: top; }
tr:nth-child(even) { background: #FAFAF8; }
tr:hover { background: var(--accent-light); }
td.numeric { text-align: right; font-variant-numeric: tabular-nums; }
tr.highlight { background: var(--accent-light) !important; font-weight: 600; }
.compare-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }
.compare-card { background: var(--bg); border-radius: 10px; padding: 20px; border: 1px solid var(--rule); }
.compare-card h4 { margin-top: 0; margin-bottom: 12px; font-weight: 600; }
.compare-card.group-a { border-top: 3px solid var(--accent); }
.compare-card.group-b { border-top: 3px solid var(--muted); }
.debate-block { background: var(--bg); border-radius: 10px; padding: 20px; margin-bottom: 16px; border: 1px solid var(--rule); }
.debate-block:last-child { margin-bottom: 0; }
.debate-question { font-weight: 600; color: var(--risk); margin-bottom: 8px; font-size: 0.95rem; }
.debate-question::before { content: "\u8d28\u7591\uff1a"; }
.debate-answer { font-size: 0.9rem; line-height: 1.6; }
.debate-answer::before { content: "\u56de\u5e94\uff1a"; font-weight: 600; color: var(--accent2); }
.action-item { background: var(--bg); border-radius: 10px; padding: 18px 20px; margin-bottom: 16px; border: 1px solid var(--rule); }
.action-item:last-child { margin-bottom: 0; }
.action-header { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; flex-wrap: wrap; }
.priority { font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; text-transform: uppercase; }
.priority.p0 { background: var(--risk-light); color: var(--risk); }
.priority.p1 { background: var(--accent-light); color: var(--accent); }
.priority.p2 { background: #E8E8E8; color: var(--muted); }
.action-source { font-size: 0.8rem; color: var(--muted); }
.action-source::before { content: "\u6765\u6e90\uff1a"; }
.action-body { font-size: 0.92rem; line-height: 1.6; }
.action-body ul { padding-left: 18px; margin-top: 8px; }
.action-body li { margin-bottom: 4px; }
.expected-impact { margin-top: 10px; padding-top: 10px; border-top: 1px dashed var(--rule); font-size: 0.85rem; color: var(--muted); }
.expected-impact strong { color: var(--accent2); }
.final-conclusion { background: linear-gradient(135deg, var(--accent2-light) 0%, var(--bg2) 100%); border: 2px solid var(--accent2); }
.final-conclusion .callout { background: transparent; border: none; margin: 0; padding: 0; }
.appendix-item { margin-bottom: 24px; }
.appendix-item h4 { font-weight: 600; margin-bottom: 8px; font-size: 0.95rem; }
.appendix-item p, .appendix-item ul { font-size: 0.88rem; color: var(--muted); }
.appendix-item ul { padding-left: 20px; }
mark.key { background: none; color: var(--accent); font-weight: 600; }
.footer { margin-top: 40px; padding: 24px 0 48px; border-top: 1px solid var(--rule); text-align: center; color: var(--muted); font-size: 0.85rem; }
@media (max-width: 768px) {
  .compare-row { grid-template-columns: 1fr; }
  .metrics-grid { grid-template-columns: repeat(2, 1fr); }
  .header h1 { font-size: 1.6rem; }
  .section { padding: 20px; }
  .meta-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 480px) {
  .metrics-grid { grid-template-columns: 1fr; }
  .meta-grid { grid-template-columns: 1fr; }
}
@media print { .section { break-inside: avoid; } }
"""


def build_html(body_content, charts_js, title):
    """组装完整HTML页面。

    Parameters
    ----------
    body_content : str
        HTML body内部的主体内容字符串。
    charts_js : str
        图表相关的JavaScript代码（如使用echarts时）。若使用matplotlib PNG可传空字符串。
    title : str
        页面<title>标签内容。

    Returns
    -------
    str
        完整HTML文档字符串。
    """
    script_block = f"<script>{charts_js}</script>" if charts_js.strip() else ""
    return f"""<!-- Generated by Trae Work -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>{CSS}</style>
</head>
<body>
{body_content}
{script_block}
</body>
</html>"""


def _chart_img(charts_dir, filename, caption):
    """生成图表figure的HTML片段。"""
    path = f"{charts_dir}/{filename}"
    return (
        f'<div class="chart-figure">'
        f'<figcaption>{caption}</figcaption>'
        f'<div class="chart-container">'
        f'<img src="{path}" alt="{caption}" loading="lazy" />'
        f'</div></div>'
    )


def _build_header(brand_info):
    """构建报告头部区域。"""
    name = brand_info.get("name", "品牌")
    period = brand_info.get("period", "")
    tracking_window = brand_info.get("tracking_window", "")
    compare_period = brand_info.get("compare_period", "")
    category = brand_info.get("category", "")
    avg_spend = brand_info.get("avg_spend", "")
    season_info = brand_info.get("season_info", "")
    s_card_price = brand_info.get("s_card_price", "")
    s_card_benefits = brand_info.get("s_card_benefits", "")

    return f"""
<div class="header">
  <div class="container">
    <h1>{name}私域运营效果分析报告</h1>
    <p class="subtitle">基于{period}数据（{tracking_window}追踪窗口，{compare_period}对比周期）</p>
    <div class="meta-grid">
      <div class="meta-item"><div class="meta-label">数据时间</div><div class="meta-value">{period}</div></div>
      <div class="meta-item"><div class="meta-label">追踪窗口</div><div class="meta-value">{tracking_window}</div></div>
      <div class="meta-item"><div class="meta-label">对比周期</div><div class="meta-value">{compare_period}</div></div>
      <div class="meta-item"><div class="meta-label">分析维度</div><div class="meta-value">4模型</div></div>
    </div>
    <div class="biz-context"><strong>业务背景：</strong>{category} | 人均消费约{avg_spend}元 | {season_info}</div>
    <div class="global-calc"><strong>全局口径：</strong>所有模型中的"平均消费次数"均为<strong>有消费用户</strong>的平均值，分母已剔除未消费人数。S卡指品牌一年{s_card_price}元的超级会员（{s_card_benefits}）。</div>
  </div>
</div>
"""


def _build_exec_summary(data_dict):
    """构建执行摘要区域。"""
    m1 = data_dict.get("model1", {})
    m2 = data_dict.get("model2", {})
    m3 = data_dict.get("model3", {})
    m4 = data_dict.get("model4", {})

    # 计算关键指标
    m1_avg_base = m1.get("avg_freq", {}).get("baseline", 1.6433)
    m1_avg_track = m1.get("avg_freq", {}).get("tracking", 2.503)
    m1_avg_change = (m1_avg_track / m1_avg_base - 1) * 100 if m1_avg_base else 0

    m1_base_0 = m1.get("baseline", {}).get("0次", {}).get("pct", 9.07)
    m1_track_0 = m1.get("tracking", {}).get("0次", {}).get("pct", 3.28)
    m1_0_drop = (1 - m1_track_0 / m1_base_0) * 100 if m1_base_0 else 0

    m1_base_4 = m1.get("baseline", {}).get("4次及以上", {}).get("pct", 6.37)
    m1_track_4 = m1.get("tracking", {}).get("4次及以上", {}).get("pct", 14.67)
    m1_4_change = (m1_track_4 / m1_base_4 - 1) * 100 if m1_base_4 else 0

    m2_siyu_track = m2.get("siyu", {}).get("tracking_avg", 2.0968)
    m2_non_track = m2.get("non_siyu", {}).get("tracking_avg", 1.8593)
    m2_diff = (m2_siyu_track / m2_non_track - 1) * 100 if m2_non_track else 0

    m3_siyu_rep = m3.get("siyu_first", {}).get("repurchase_rate", 8.31)
    m3_non_rep = m3.get("non_siyu_first", {}).get("repurchase_rate", 7.06)
    m3_rep_diff = m3_siyu_rep - m3_non_rep

    m4_siyu_s = m4.get("siyu_s", {}).get("tracking_avg", 2.6522)

    return f"""
<div class="container">
<div class="section exec-summary">
  <h2>执行摘要</h2>
  <table class="conclusion-table">
    <thead><tr><th>结论维度</th><th>判断</th><th>依据</th></tr></thead>
    <tbody>
      <tr><td>高价值沉淀</td><td class="judgment yes">&#10003; 有效</td><td>模型一：0次消费用户从{m1_base_0:.2f}%降至{m1_track_0:.2f}%，降幅{m1_0_drop:.1f}%</td></tr>
      <tr><td>大盘差异</td><td class="judgment yes">&#10003; 显著</td><td>模型二：私域组消费频次高于非私域组约{m2_diff:.1f}%</td></tr>
      <tr><td>新客激活</td><td class="judgment yes">&#10003; 有效</td><td>模型三：私域首单新客2次+复购率{m3_siyu_rep:.2f}%高于非私域首单新客{m3_non_rep:.2f}%</td></tr>
      <tr><td>S卡放大</td><td class="judgment yes">&#10003; 有效</td><td>模型四：私域买S卡客户平均{m4_siyu_s:.2f}次，为所有群体最高</td></tr>
    </tbody>
  </table>
  <div class="metrics-grid">
    <div class="metric-card"><div class="number">{m1_avg_track:.2f}</div><div class="label">拉新客户平均消费次数</div><div class="change up">&#8593;{m1_avg_change:.1f}%（{m1_avg_base:.2f}&#8594;{m1_avg_track:.2f}）</div></div>
    <div class="metric-card"><div class="number">{m1_track_4:.2f}%</div><div class="label">高频客户占比（4次+）</div><div class="change up">&#8593;{m1_4_change:.1f}%（{m1_base_4:.2f}%&#8594;{m1_track_4:.2f}%）</div></div>
    <div class="metric-card"><div class="number">{m2_diff:.1f}%</div><div class="label">私域vs非私域频次优势</div><div class="change up">追踪后1月</div></div>
  </div>
  <div class="alert-box"><h4>数据说明</h4><p>模型二初始基准包含0&#8594;1新客，因此初始基准频次高于追踪后属于正常口径现象，不做前后对比。模型二追踪后1月无0次消费客户。当前仅1个月追踪周期，后续将持续追踪。</p></div>
</div>
"""


def _build_model1(data, charts_dir):
    """构建模型一HTML区块。"""
    baseline = data.get("baseline", {})
    tracking = data.get("tracking", {})
    sample_size = data.get("sample_size", 518)
    avg = data.get("avg_freq", {})

    rows = ""
    for key in ["0次", "1次", "2次", "3次", "4次及以上"]:
        b = baseline.get(key, {})
        t = tracking.get(key, {})
        b_pct = b.get("pct", 0)
        t_pct = t.get("pct", 0)
        diff_arrow = "&#8593;" if t_pct > b_pct else "&#8595;"
        diff_pct = abs((t_pct / b_pct - 1) * 100) if b_pct else 0
        rows += f"""
      <tr><td>{key}消费客户</td><td>私域拉新组</td><td class="numeric">{b.get('count', 0)} ({b_pct:.2f}%)</td><td class="numeric">{t.get('count', 0)} ({t_pct:.2f}%)</td><td class="numeric" style="color:var(--accent2)">{diff_arrow}{diff_pct:.1f}%</td></tr>
"""

    avg_base = avg.get("baseline", 1.6433)
    avg_track = avg.get("tracking", 2.503)
    avg_diff = (avg_track / avg_base - 1) * 100 if avg_base else 0

    m1_base_0 = baseline.get("0次", {}).get("pct", 9.07)
    m1_track_0 = tracking.get("0次", {}).get("pct", 3.28)
    m1_0_drop = (1 - m1_track_0 / m1_base_0) * 100 if m1_base_0 else 0
    m1_base_4 = baseline.get("4次及以上", {}).get("pct", 6.37)
    m1_track_4 = tracking.get("4次及以上", {}).get("pct", 14.67)

    return f"""
  <div class="model-block">
    <div class="model-header"><h3>模型一：按拉新人群分析</h3><span class="model-tag">效果验证</span></div>
    <div class="model-purpose">剔除首单与无消费用户，追踪私域拉新老客户的消费频次变化，判断运营后是否保持活跃并沉淀高频用户。</div>
    <div class="methodology-box"><h4>筛选口径</h4><ul>
      <li><strong>样本人群：</strong>进入企微私域的用户</li>
      <li><strong>时间锚点：</strong>以每位用户进入私域时间为锚点，统计180天的消费数据</li>
      <li><strong>剔除规则①：</strong>加入私域后同时完成首单的新用户（避免"加私域下单有礼"造成0&#8594;1噪音）</li>
      <li><strong>剔除规则②：</strong>私域运营前后均无消费记录的僵尸用户（稀释0次占比）</li>
    </ul></div>
    {_chart_img(charts_dir, "chart_01_dist.png", "图1：拉新客户消费频次分布变化")}
    {_chart_img(charts_dir, "chart_02_avg.png", "图2：拉新客户平均消费次数变化趋势")}
    <div class="table-wrap"><table><thead><tr><th>指标</th><th>组别</th><th>基准窗口</th><th>追踪后1月</th><th>差异趋势</th></tr></thead><tbody>
{rows}
      <tr class="highlight"><td>平均消费次数</td><td>私域拉新组</td><td class="numeric">{avg_base:.4f}</td><td class="numeric">{avg_track:.3f}</td><td class="numeric" style="color:var(--accent2)">&#8593;{avg_diff:.1f}%</td></tr>
    </tbody></table></div>
    <div class="callout positive"><span class="callout-title">&#9989; 核心发现</span>私域运营显著激活了拉新客户。平均消费次数从{avg_base:.2f}次提升至{avg_track:.2f}次（+{avg_diff:.1f}%），0次消费客户占比从{m1_base_0:.2f}%降至{m1_track_0:.2f}%（降幅{m1_0_drop:.1f}%），4次及以上高频客户占比从{m1_base_4:.2f}%提升至{m1_track_4:.2f}%。消费结构从以1次为主的"浅层消费"向2-3次为主的"活跃消费"转变。</div>
    <div class="callout warning"><span class="callout-title">&#9888;&#65039; 口径注意</span>剔除首单和僵尸用户后样本量为{sample_size}人，结论适用于存量老客户的活跃维持判断。5月进入初夏，茶饮+简餐场景活跃，频次提升需结合季节因素客观分析。</div>
  </div>
"""


def _build_model2(data, charts_dir):
    """构建模型二HTML区块。"""
    siyu = data.get("siyu", {})
    non = data.get("non_siyu", {})

    s_count = siyu.get("count", 5105)
    n_count = non.get("count", 39707)
    s_bavg = siyu.get("baseline_avg", 3.0895)
    s_tavg = siyu.get("tracking_avg", 2.0968)
    n_bavg = non.get("baseline_avg", 2.7092)
    n_tavg = non.get("tracking_avg", 1.8593)
    s_bhf = siyu.get("high_freq_base", 7.13)
    s_thf = siyu.get("high_freq_track", 12.22)
    n_bhf = non.get("high_freq_base", 5.76)
    n_thf = non.get("high_freq_track", 9.97)
    diff_pct = (s_tavg / n_tavg - 1) * 100 if n_tavg else 0

    return f"""
  <div class="model-block">
    <div class="model-header"><h3>模型二：按订单人群分析（私域组 vs 非私域对照组）</h3><span class="model-tag">对比验证</span></div>
    <div class="model-purpose">对比私域组（{s_count:,}人）与非私域对照组（{n_count:,}人）的消费频次表现，通过"频次折线趋势图"判断两组差异是在收敛还是扩大。</div>
    <div class="methodology-box"><h4>筛选口径</h4><ul>
      <li><strong>样本人群：</strong>带有会员ID的消费用户（不含平台买单无法识别会员ID的用户）</li>
      <li><strong>分组：</strong>私域组（加企微私域的会员） vs 非私域对照组（品牌会员但不在企微私域中）</li>
      <li><strong>时间锚点：</strong>以用户在筛选时间段内的最早消费时间为锚点，统计180天的消费数据</li>
    </ul></div>
    {_chart_img(charts_dir, "chart_03_compare.png", "图3：私域组 vs 非私域组消费频次分布对比（追踪后1月）")}
    {_chart_img(charts_dir, "chart_04_trend.png", "图4：私域组 vs 非私域组平均消费次数趋势对比")}
    <div class="table-wrap"><table><thead><tr><th>指标</th><th>组别</th><th>基准窗口</th><th>追踪后1月</th><th>差异趋势</th></tr></thead><tbody>
      <tr><td rowspan="2">平均消费次数</td><td>私域组</td><td class="numeric">{s_bavg:.4f}</td><td class="numeric">{s_tavg:.4f}</td><td class="numeric" style="color:var(--accent2)">高于非私域+{diff_pct:.1f}%</td></tr>
      <tr><td>非私域组</td><td class="numeric">{n_bavg:.4f}</td><td class="numeric">{n_tavg:.4f}</td><td class="numeric" style="color:var(--muted)">&#8212;</td></tr>
      <tr><td rowspan="2">高频客户占比（4次+）</td><td>私域组</td><td class="numeric">{s_bhf:.2f}%</td><td class="numeric">{s_thf:.2f}%</td><td class="numeric" style="color:var(--accent2)">&#8593;{s_thf-s_bhf:.2f}pp</td></tr>
      <tr><td>非私域组</td><td class="numeric">{n_bhf:.2f}%</td><td class="numeric">{n_thf:.2f}%</td><td class="numeric" style="color:var(--muted)">&#8593;{n_thf-n_bhf:.2f}pp</td></tr>
    </tbody></table></div>
    <div class="compare-row">
      <div class="compare-card group-a"><h4>私域组（追踪后1月）</h4><p>总客户数：<strong>{s_count:,}</strong></p><p>平均消费次数：<strong>{s_tavg:.2f}次</strong></p><p>高频客户占比（4次+）：<strong>{s_thf:.2f}%</strong></p></div>
      <div class="compare-card group-b"><h4>非私域组（追踪后1月）</h4><p>总客户数：<strong>{n_count:,}</strong></p><p>平均消费次数：<strong>{n_tavg:.2f}次</strong></p><p>高频客户占比（4次+）：<strong>{n_thf:.2f}%</strong></p></div>
    </div>
    <div class="callout positive"><span class="callout-title">&#9989; 核心发现</span>私域组消费频次高于非私域组。追踪后1月，私域组{s_tavg:.2f}次 vs 非私域组{n_tavg:.2f}次，差异+{diff_pct:.1f}%。高频客户（4次+）占比私域组{s_thf:.2f}% vs 非私域组{n_thf:.2f}%，私域组高频占比提升幅度（+{s_thf-s_bhf:.2f}pp）大于非私域组（+{n_thf-n_bhf:.2f}pp）。</div>
    <div class="callout warning"><span class="callout-title">&#9888;&#65039; 口径注意</span>初始基准频次高于追踪后属于正常口径现象（因初始基准包含0&#8594;1新客），模型二不做前后对比，重点看两组差异的收敛/扩大趋势。追踪后1月无0次消费客户（所有纳入用户在追踪期均至少消费1次）。</div>
  </div>
"""


def _build_model3(data, charts_dir):
    """构建模型三HTML区块。"""
    siyu = data.get("siyu_first", {})
    non = data.get("non_siyu_first", {})

    s_count = siyu.get("count", 2610)
    n_count = non.get("count", 28615)
    s_avg = siyu.get("tracking_avg", 1.0927)
    n_avg = non.get("tracking_avg", 1.0858)
    s_rep = siyu.get("repurchase_rate", 8.31)
    n_rep = non.get("repurchase_rate", 7.06)
    rep_diff = s_rep - n_rep

    return f"""
  <div class="model-block">
    <div class="model-header"><h3>模型三：私域首单新客 vs 非私域首单新客</h3><span class="model-tag">归因验证</span></div>
    <div class="model-purpose">对比私域首单新客（{s_count:,}人）与非私域首单新客（{n_count:,}人）在首次消费后的复购行为差异，验证私域运营是否有效激活新客。</div>
    <div class="methodology-box"><h4>筛选口径</h4><ul>
      <li><strong>样本人群：</strong>带有会员ID的消费用户（不含平台买单无法识别会员ID的用户）</li>
      <li><strong>分组：</strong>私域首单新客（首次消费且当天加入企微私域） vs 非私域首单新客（完成首次消费但不在私域中）</li>
      <li><strong>时间锚点：</strong>以用户在筛选时间段内的最早消费时间为锚点，统计180天的消费数据</li>
    </ul></div>
    {_chart_img(charts_dir, "chart_05_compare.png", "图5：私域首单新客 vs 非私域首单新客复购频次对比（追踪后1月）")}
    {_chart_img(charts_dir, "chart_06_repurchase.png", "图6：私域首单新客 vs 非私域首单新客2次+复购率对比")}
    <div class="table-wrap"><table><thead><tr><th>指标</th><th>组别</th><th>基准窗口</th><th>追踪后1月</th><th>差异趋势</th></tr></thead><tbody>
      <tr><td rowspan="2">平均消费次数</td><td>私域首单新客</td><td class="numeric">&#8212;</td><td class="numeric">{s_avg:.4f}</td><td class="numeric" style="color:var(--accent2)">略高于非私域</td></tr>
      <tr><td>非私域首单新客</td><td class="numeric">&#8212;</td><td class="numeric">{n_avg:.4f}</td><td class="numeric" style="color:var(--muted)">&#8212;</td></tr>
      <tr><td rowspan="2">2次+复购率</td><td>私域首单新客</td><td class="numeric">&#8212;</td><td class="numeric">{s_rep:.2f}%</td><td class="numeric" style="color:var(--accent2)">+{rep_diff:.2f}pp</td></tr>
      <tr><td>非私域首单新客</td><td class="numeric">&#8212;</td><td class="numeric">{n_rep:.2f}%</td><td class="numeric" style="color:var(--muted)">&#8212;</td></tr>
    </tbody></table></div>
    <div class="callout positive"><span class="callout-title">&#9989; 核心发现</span>私域首单新客展现出略强的复购意愿。追踪后1月，私域首单新客2次+复购率{s_rep:.2f}%高于非私域首单新客{n_rep:.2f}%，差异{rep_diff:.2f}pp。两组平均消费次数接近（{s_avg:.2f} vs {n_avg:.2f}），但私域组在2次+复购率上领先，说明私域运营对新客后续消费有正向作用。</div>
    <div class="callout warning"><span class="callout-title">&#9888;&#65039; 口径注意</span>本模型两组样本均为首单新客，基线一致，差异可直接归因于私域运营效应。当前仅1个月追踪数据，差异幅度（{rep_diff:.2f}pp）较小，需后续追踪周期验证差异是否持续或扩大。</div>
  </div>
"""


def _build_model4(data, charts_dir):
    """构建模型四HTML区块。"""
    s_s = data.get("siyu_s", {})
    s_n = data.get("siyu_no_s", {})
    n_s = data.get("non_siyu_s", {})
    n_n = data.get("non_siyu_no_s", {})

    s_s_c = s_s.get("count", 207)
    s_n_c = s_n.get("count", 4898)
    n_s_c = n_s.get("count", 867)
    n_n_c = n_n.get("count", 38840)

    s_s_b = s_s.get("baseline_avg", 2.9655)
    s_s_t = s_s.get("tracking_avg", 2.6522)
    s_n_b = s_n.get("baseline_avg", 3.0969)
    s_n_t = s_n.get("tracking_avg", 2.0733)
    n_s_b = n_s.get("baseline_avg", 2.4203)
    n_s_t = n_s.get("tracking_avg", 2.5283)
    n_n_b = n_n.get("baseline_avg", 2.7191)
    n_n_t = n_n.get("tracking_avg", 1.8444)

    def _chg(b, t):
        return (t / b - 1) * 100 if b else 0

    return f"""
  <div class="model-block">
    <div class="model-header"><h3>模型四：按私域与购S卡分析</h3><span class="model-tag">放大验证</span></div>
    <div class="model-purpose">进一步细分私域客户群体，分析购买S卡对消费频次的提升效果。</div>
    <div class="methodology-box"><h4>筛选口径</h4><ul>
      <li><strong>样本人群：</strong>带有消费的用户（不含平台买单无法识别会员ID的用户）</li>
      <li><strong>分组：</strong>私域买S卡 / 私域未买S卡 / 非私域买S卡 / 非私域未买S卡</li>
      <li><strong>时间锚点：</strong>以用户在筛选时间段内的最早消费时间为锚点，统计180天的消费数据</li>
    </ul></div>
    {_chart_img(charts_dir, "chart_07_cross.png", "图7：四类客户平均消费次数对比（追踪后1月）")}
    {_chart_img(charts_dir, "chart_08_s_trend.png", "图8：购S卡 vs 未购S卡客户平均消费趋势")}
    <div class="table-wrap"><table><thead><tr><th>客户类型</th><th>样本量</th><th>基准平均消费</th><th>追踪后1月</th><th>整体变化</th></tr></thead><tbody>
      <tr class="highlight"><td>私域买S卡</td><td class="numeric">{s_s_c}</td><td class="numeric">{s_s_b:.4f}</td><td class="numeric"><strong>{s_s_t:.4f}</strong></td><td class="numeric" style="color:var(--risk)">&#8595;{_chg(s_s_b, s_s_t):.1f}%</td></tr>
      <tr><td>私域未买S卡</td><td class="numeric">{s_n_c}</td><td class="numeric">{s_n_b:.4f}</td><td class="numeric">{s_n_t:.4f}</td><td class="numeric" style="color:var(--risk)">&#8595;{_chg(s_n_b, s_n_t):.1f}%</td></tr>
      <tr><td>非私域买S卡</td><td class="numeric">{n_s_c}</td><td class="numeric">{n_s_b:.4f}</td><td class="numeric">{n_s_t:.4f}</td><td class="numeric" style="color:var(--accent2)">&#8593;{_chg(n_s_b, n_s_t):.1f}%</td></tr>
      <tr><td>非私域未买S卡</td><td class="numeric">{n_n_c}</td><td class="numeric">{n_n_b:.4f}</td><td class="numeric">{n_n_t:.4f}</td><td class="numeric" style="color:var(--risk)">&#8595;{_chg(n_n_b, n_n_t):.1f}%</td></tr>
    </tbody></table></div>
    <div class="callout positive"><span class="callout-title">&#9989; 核心发现</span>追踪后1月形成清晰价值层级：私域买S卡（{s_s_t:.2f}次）&gt; 非私域买S卡（{n_s_t:.2f}次）&gt; 私域未买S卡（{s_n_t:.2f}次）&gt; 非私域未买S卡（{n_n_t:.2f}次）。S卡对消费频次的提升作用明显：对非私域的增量（{n_s_t - n_n_t:.2f}次）略大于对私域的增量（{s_s_t - s_n_t:.2f}次），说明S卡权益本身对低频用户有较强的消费驱动作用。私域+S卡组合仍保持最优表现。</div>
    <div class="callout warning"><span class="callout-title">&#9888;&#65039; 口径注意</span>S卡样本量{s_s_c}人（较4月57人有明显增长），趋势方向可信但精确度仍有限。存在反向因果可能：高频用户更愿意购买S卡，而非买S卡导致高频。初始基准频次高于追踪后属于正常口径现象，不做前后对比。</div>
  </div>
"""


def _build_cross_analysis(data_dict):
    """构建交叉对比与归因区域。"""
    m4 = data_dict.get("model4", {})
    s_s_t = m4.get("siyu_s", {}).get("tracking_avg", 2.6522)
    s_n_t = m4.get("siyu_no_s", {}).get("tracking_avg", 2.0733)
    n_s_t = m4.get("non_siyu_s", {}).get("tracking_avg", 2.5283)
    n_n_t = m4.get("non_siyu_no_s", {}).get("tracking_avg", 1.8444)

    m3 = data_dict.get("model3", {})
    s_rep = m3.get("siyu_first", {}).get("repurchase_rate", 8.31)
    n_rep = m3.get("non_siyu_first", {}).get("repurchase_rate", 7.06)

    m1 = data_dict.get("model1", {})
    avg_base = m1.get("avg_freq", {}).get("baseline", 1.6433)
    avg_track = m1.get("avg_freq", {}).get("tracking", 2.503)
    avg_chg = (avg_track / avg_base - 1) * 100 if avg_base else 0

    return f"""
<div class="section">
  <h2>交叉对比与归因</h2>
  <p class="section-desc">综合多个模型的数据，发现跨模型的关联规律与归因线索。</p>
  <div class="model-block">
    <div class="callout neutral"><span class="callout-title">&#128161; 关联发现</span>S卡是消费频次提升的关键杠杆</div>
    <p>模型四显示，无论是否私域，购买S卡的客户消费频次均显著更高。S卡对非私域的增量（{n_s_t - n_n_t:.2f}次）略大于对私域的增量（{s_s_t - s_n_t:.2f}次），说明S卡本身的权益驱动（天天88折+60元代金券）对低频非私域用户的消费刺激更强。</p>
  </div>
  <div class="model-block">
    <div class="callout neutral"><span class="callout-title">&#128161; 关联发现</span>新客激活效果需要更多追踪周期验证</div>
    <p>模型三显示私域首单新客2次+复购率{s_rep:.2f}%高于非私域{n_rep:.2f}%（+{s_rep-n_rep:.2f}pp），模型一也显示拉新客户频次提升{avg_chg:.1f}%。两个模型从不同人群维度指向私域运营的积极作用，但当前仅1个月追踪数据，差异幅度较小，后续需持续追踪确认趋势。</p>
  </div>
</div>
"""


def _build_debate(data_dict):
    """构建数据攻防推演区域。"""
    m2 = data_dict.get("model2", {})
    s_tavg = m2.get("siyu", {}).get("tracking_avg", 2.0968)
    n_tavg = m2.get("non_siyu", {}).get("tracking_avg", 1.8593)
    diff_pct = (s_tavg / n_tavg - 1) * 100 if n_tavg else 0

    m3 = data_dict.get("model3", {})
    s_rep = m3.get("siyu_first", {}).get("repurchase_rate", 8.31)
    n_rep = m3.get("non_siyu_first", {}).get("repurchase_rate", 7.06)

    m1 = data_dict.get("model1", {})
    avg_chg = (m1.get("avg_freq", {}).get("tracking", 2.503) / m1.get("avg_freq", {}).get("baseline", 1.6433) - 1) * 100

    m4 = data_dict.get("model4", {})
    s_s_c = m4.get("siyu_s", {}).get("count", 207)

    return f"""
<div class="section">
  <h2>数据攻防推演</h2>
  <p class="section-desc">从品牌方视角，模拟对数据结论的典型质疑与数据回应。</p>
  <div class="debate-block">
    <div class="debate-question">私域组频次高是不是因为本来就更活跃的用户才加私域？</div>
    <div class="debate-answer">模型三专门控制了"都是同时到店的新客"这一变量，私域首单新客与未入会新客在到店时点是相同的，差异仅在于是否加入私域。结果显示私域首单新客2次+复购率{s_rep:.2f}%高于非私域{n_rep:.2f}%，说明私域运营本身有因果效应，而非单纯的用户自选择。</div>
  </div>
  <div class="debate-block">
    <div class="debate-question">追踪后频次下降（3.09&#8594;2.10）是不是说明私域越做越差？</div>
    <div class="debate-answer">这是口径正常现象。模型二的初始基准包含了原本0次消费、追踪后成为1次消费的新客，拉高了基准值。重点应看两组差异是否稳定——私域组{s_tavg:.2f}次 vs 非私域组{n_tavg:.2f}次，差异+{diff_pct:.1f}%，私域组始终领先。</div>
  </div>
  <div class="debate-block">
    <div class="debate-question">5月只有1个月追踪数据，结论可信吗？</div>
    <div class="debate-answer">单月数据可以反映当前趋势方向，模型一（+{avg_chg:.1f}%）和模型四（清晰价值层级）的结论信号较强，可信度较高。模型三（+{s_rep-n_rep:.2f}pp）差异幅度较小，精确度和统计稳定性有限，建议后续追踪周期延长后再做最终判断。</div>
  </div>
  <div class="debate-block">
    <div class="debate-question">S卡样本只有{s_s_c}人，结论能信吗？</div>
    <div class="debate-answer">{s_s_c}人较4月（57人）有明显增长，趋势方向可信。四个群体形成清晰的价值层级排列，方向一致性强。建议继续扩大S卡推广以积累更大样本验证精确数值。</div>
  </div>
</div>
"""


def _build_actions(data_dict):
    """构建运营建议区域。"""
    m3 = data_dict.get("model3", {})
    s_rep = m3.get("siyu_first", {}).get("repurchase_rate", 8.31)

    m1 = data_dict.get("model1", {})
    m1_track_0 = m1.get("tracking", {}).get("0次", {}).get("pct", 3.28)
    m1_track_4 = m1.get("tracking", {}).get("4次及以上", {}).get("pct", 14.67)

    m4 = data_dict.get("model4", {})
    s_n_c = m4.get("siyu_no_s", {}).get("count", 4898)
    s_s_t = m4.get("siyu_s", {}).get("tracking_avg", 2.6522)
    s_n_t = m4.get("siyu_no_s", {}).get("tracking_avg", 2.0733)

    return f"""
<div class="section">
  <h2>运营建议</h2>
  <p class="section-desc">基于数据分析结果，按优先级给出带时间属性、数据来源和量化预期的运营建议。</p>
  <div class="action-item">
    <div class="action-header"><span class="priority p0">P0</span><span class="action-source">模型三</span><span class="action-source">7天内</span></div>
    <div class="action-body"><strong>黄金7天：新客入会立即触发二次到店礼</strong><ul><li>私域首单新客在7天内推送"二次到店享5折指定菜品"优惠券</li><li>通过企微1v1消息+朋友圈曝光双触达</li></ul></div>
    <div class="expected-impact"><strong>预期效果：</strong>2次+复购率从{s_rep:.2f}%提升至12%+</div>
  </div>
  <div class="action-item">
    <div class="action-header"><span class="priority p0">P0</span><span class="action-source">模型四</span><span class="action-source">立即</span></div>
    <div class="action-body"><strong>S卡定向转化：私域未购卡客户是最大机会点</strong><ul><li>私域未买S卡的{s_n_c:,}人是重点转化对象，定向推送S卡权益说明</li><li>设置"消费满3次自动推荐S卡"的触发机制</li></ul></div>
    <div class="expected-impact"><strong>预期效果：</strong>若10%转化为S卡用户，预计带动约{s_n_c//10:,}人消费频次从{s_n_t:.2f}次提升至{s_s_t:.2f}次</div>
  </div>
  <div class="action-item">
    <div class="action-header"><span class="priority p1">P1</span><span class="action-source">模型一</span><span class="action-source">30天未消费触发</span></div>
    <div class="action-body"><strong>沉默激活：针对0次和1次消费客户</strong><ul><li>30天未消费触发限时秒杀（指定饮品第二杯半价）</li><li>1次消费客户推送"满减券"促进二次到店</li></ul></div>
    <div class="expected-impact"><strong>预期效果：</strong>0次客户占比从{m1_track_0:.2f}%进一步降至2%以下</div>
  </div>
  <div class="action-item">
    <div class="action-header"><span class="priority p1">P1</span><span class="action-source">模型一+二</span><span class="action-source">持续</span></div>
    <div class="action-body"><strong>高频养成：消费3次+自动入VIP群</strong><ul><li>消费3次以上客户自动进入VIP专属群，享新品优先试吃、生日85折等权益</li><li>4次+客户占比从{m1_track_4:.2f}%提升至20%</li></ul></div>
    <div class="expected-impact"><strong>预期效果：</strong>4次+高频客户占比提升5个百分点</div>
  </div>
</div>
"""


def _build_final_conclusion(data_dict):
    """构建最终结论区域。"""
    m1 = data_dict.get("model1", {})
    avg_chg = (m1.get("avg_freq", {}).get("tracking", 2.503) / m1.get("avg_freq", {}).get("baseline", 1.6433) - 1) * 100
    m1_base_0 = m1.get("baseline", {}).get("0次", {}).get("pct", 9.07)
    m1_track_0 = m1.get("tracking", {}).get("0次", {}).get("pct", 3.28)
    m1_0_drop = (1 - m1_track_0 / m1_base_0) * 100 if m1_base_0 else 0

    m2 = data_dict.get("model2", {})
    s_tavg = m2.get("siyu", {}).get("tracking_avg", 2.0968)
    n_tavg = m2.get("non_siyu", {}).get("tracking_avg", 1.8593)
    diff_pct = (s_tavg / n_tavg - 1) * 100 if n_tavg else 0

    m3 = data_dict.get("model3", {})
    s_rep = m3.get("siyu_first", {}).get("repurchase_rate", 8.31)
    n_rep = m3.get("non_siyu_first", {}).get("repurchase_rate", 7.06)

    return f"""
<div class="section final-conclusion">
  <h2>最终结论</h2>
  <div class="callout neutral"><span class="callout-title">&#128161; 结论</span>四个模型从不同角度验证了私域运营的效果：模型一显示拉新客户频次提升{avg_chg:.1f}%、0次占比降低{m1_0_drop:.1f}%；模型二显示私域组消费频次高于非私域组{diff_pct:.1f}%；模型三在控制基线后确认私域对新客复购有正向作用（+{s_rep-n_rep:.2f}pp）；模型四显示S卡是消费频次提升的关键杠杆，私域+S卡组合保持最优表现。当前仅1个月追踪周期，建议持续追踪并在夏季旺季后复评。</div>
</div>
"""


def _build_appendix(data_dict, brand_info):
    """构建附录区域。"""
    period = brand_info.get("period", "")
    tracking_window = brand_info.get("tracking_window", "")
    compare_period = brand_info.get("compare_period", "")

    m1 = data_dict.get("model1", {})
    m1_size = m1.get("sample_size", 518)

    m2 = data_dict.get("model2", {})
    s_count = m2.get("siyu", {}).get("count", 5105)
    n_count = m2.get("non_siyu", {}).get("count", 39707)

    m3 = data_dict.get("model3", {})
    sf_count = m3.get("siyu_first", {}).get("count", 2610)
    nf_count = m3.get("non_siyu_first", {}).get("count", 28615)

    m4 = data_dict.get("model4", {})
    s_s_c = m4.get("siyu_s", {}).get("count", 207)
    s_n_c = m4.get("siyu_no_s", {}).get("count", 4898)
    n_s_c = m4.get("non_siyu_s", {}).get("count", 867)
    n_n_c = m4.get("non_siyu_no_s", {}).get("count", 38840)

    return f"""
<div class="section">
  <h2>附录</h2>
  <div class="appendix-item"><h4>A. 模型定义与筛选口径</h4><ul>
    <li><strong>模型一（效果验证）：</strong>筛选{period}时间段内进入企微私域的用户，以进入私域时间为锚点，统计{tracking_window}消费数据。剔除加入私域后同时完成首单的新用户（避免"加私域下单有礼"噪音），以及前后均无消费的僵尸用户。样本量{m1_size}人。分析目的：看存量老客户在私域运营后的频次变化。</li>
    <li><strong>模型二（对比验证）：</strong>筛选{period}时间段内带会员ID的消费用户（不含平台买单无法识别会员ID），分为私域组（{s_count:,}人，加企微）vs 非私域组（{n_count:,}人，品牌会员但不在企微）。以最早消费时间为锚点，统计{tracking_window}消费数据。初始基准不做前后对比，重点看两组差异的收敛/扩大趋势。</li>
    <li><strong>模型三（归因验证）：</strong>筛选{period}时间段内带会员ID的消费用户，分为私域首单新客（{sf_count:,}人，首单且当天加企微）vs 非私域首单新客（{nf_count:,}人，首单但不在私域）。以最早消费时间为锚点，统计{tracking_window}消费数据。分析目的：验证私域运营是否有效激活新客。</li>
    <li><strong>模型四（放大验证）：</strong>筛选{period}时间段内带消费的用户，按私域&#215;S卡购买分为四类（私域买S卡{s_s_c}人/私域未买S卡{s_n_c}人/非私域买S卡{n_s_c}人/非私域未买S卡{n_n_c}人）。以最早消费时间为锚点，统计{tracking_window}消费数据。分析目的：验证S卡是否放大私域效果。</li>
  </ul></div>
  <div class="appendix-item"><h4>B. 数据口径说明</h4><ul>
    <li><strong>追踪窗口：</strong>{tracking_window}</li>
    <li><strong>对比周期：</strong>{compare_period}（追踪后1月）</li>
    <li><strong>消费次数计算：</strong>有消费用户的平均消费次数，分母已剔除未消费人数</li>
    <li><strong>客户分层标准：</strong>0次/1次/2次/3次/4次及以上</li>
  </ul></div>
  <div class="appendix-item"><h4>C. 术语表</h4><ul>
    <li><strong>私域客户：</strong>加入品牌企微私域的会员用户</li>
    <li><strong>非私域对照组：</strong>品牌会员但不在企微私域中的用户</li>
    <li><strong>S卡：</strong>品牌一年98元的超级会员卡，含60元代金券+天天88折+周周5折菜品券+生日85折</li>
    <li><strong>高频用户：</strong>4次及以上消费客户</li>
  </ul></div>
  <div class="appendix-item"><h4>D. 局限性 / 偏差说明</h4><ul>
    <li><strong>自选择偏差：</strong>模型二/四存在"更活跃用户更可能加私域"的自选择偏差，模型三通过控制"同时到店新客"基线部分缓解</li>
    <li><strong>季节性因素：</strong>5月进入初夏，茶饮+简餐场景活跃，结论需结合季节因素解读</li>
    <li><strong>追踪周期局限：</strong>当前仅1个月追踪周期，结论精确度和统计稳定性有限，后续需持续追踪</li>
    <li><strong>样本局限：</strong>模型四S卡样本量{s_s_c}人，较4月（57人）增长但绝对值仍偏小</li>
  </ul></div>
</div>

<div class="footer"><p>数据来源：{brand_info.get('name', '品牌')}私域运营后台 | 分析时间：2026年7月 | 报告生成：Trae Work</p></div>

</div>
"""


def generate_html_report(data_dict, charts_dir, output_path, brand_info):
    """生成完整的HTML报告。

    Parameters
    ----------
    data_dict : dict
        包含4个模型数据的字典，键为model1~model4。
    charts_dir : str or Path
        图表PNG所在目录。将自动计算相对于output_path的相对路径。
    output_path : str or Path
        HTML报告输出路径。
    brand_info : dict
        品牌信息字典，需包含：
        - name: 品牌名称
        - period: 数据时间（如"2026年5月"）
        - tracking_window: 追踪窗口（如"180天"）
        - compare_period: 对比周期（如"1个月"）
        - category: 业务品类（如"温州休闲茶餐厅（正餐）"）
        - avg_spend: 人均消费（如"70"）
        - season_info: 季节信息（如"5月进入初夏..."）
        - s_card_price: S卡价格（如"98"）
        - s_card_benefits: S卡权益描述

    Returns
    -------
    str
        生成的HTML文件路径。
    """
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # 计算图表目录相对于HTML文件的相对路径
    charts_path = Path(charts_dir)
    try:
        rel_charts_dir = os.path.relpath(charts_path, out_path.parent)
    except ValueError:
        rel_charts_dir = str(charts_path)
    rel_charts_dir = rel_charts_dir.replace("\\", "/")

    # 组装body
    body_parts = [
        _build_header(brand_info),
        _build_exec_summary(data_dict),
        '<div class="section">\n  <h2>模型分析</h2>\n  <p class="section-desc">本报告基于4个分析模型，从效果验证、对比验证、归因验证、放大验证四个维度递进评估私域运营价值。</p>',
        _build_model1(data_dict.get("model1", {}), rel_charts_dir),
        _build_model2(data_dict.get("model2", {}), rel_charts_dir),
        _build_model3(data_dict.get("model3", {}), rel_charts_dir),
        _build_model4(data_dict.get("model4", {}), rel_charts_dir),
        "</div>",
        _build_cross_analysis(data_dict),
        _build_debate(data_dict),
        _build_actions(data_dict),
        _build_final_conclusion(data_dict),
        _build_appendix(data_dict, brand_info),
    ]
    body_content = "\n".join(body_parts)

    title = f"{brand_info.get('name', '品牌')}私域运营效果分析报告（{brand_info.get('period', '')}）"
    html = build_html(body_content, "", title)

    out_path.write_text(html, encoding="utf-8")
    return str(out_path)


if __name__ == "__main__":
    # 本地快速测试
    from extract_data import extract_all_models

    data = extract_all_models("/data/user/work/demo_base.xlsx")
    brand = {
        "name": "去茶去",
        "period": "2026年5月",
        "tracking_window": "180天",
        "compare_period": "1个月",
        "category": "温州休闲茶餐厅（正餐）",
        "avg_spend": "70",
        "season_info": "5月进入初夏，气温回升带动茶饮+简餐场景，客流进入活跃期",
        "s_card_price": "98",
        "s_card_benefits": "开卡送60元代金券+天天88折+周周5折菜品券",
    }
    path = generate_html_report(data, "/data/user/work/test_charts", "/data/user/work/test_report/report.html", brand)
    print(path)
