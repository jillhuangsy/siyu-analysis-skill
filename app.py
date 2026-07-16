#!/usr/bin/env python3
"""私域数据分析工具台。

基于「私域运营效果分析报告生成 Skill」的交互式 Web 应用。
用户上传 Excel 数据底表、填写业务信息后，一键生成 HTML 分析报告与图表。
"""

import base64
import shutil
import sys
import time
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# 将 scripts 目录加入模块搜索路径
SCRIPT_DIR = Path(__file__).parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from extract_data import extract_all_models
from generate_charts import generate_all_charts
from generate_report import generate_html_report

# ---------------------------------------------------------------------------
# 页面配置
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="私域数据分析工具台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# 自定义样式
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .main-title { font-size: 2.2rem; font-weight: 700; color: #2D2A26; margin-bottom: 0.5rem; }
    .sub-title { font-size: 1rem; color: #8A8580; margin-bottom: 2rem; }
    .stButton>button { background-color: #B3875E; color: white; font-weight: 600; border: none; }
    .stButton>button:hover { background-color: #9a714d; color: white; }
    .metric-card { background: #F7F5F2; border-radius: 10px; padding: 16px; border: 1px solid #D9D5D0; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def save_uploaded_file(uploaded_file, dest_dir: Path) -> Path:
    """将上传的文件保存到本地目录。"""
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / uploaded_file.name
    dest_path.write_bytes(uploaded_file.getvalue())
    return dest_path


def detect_sheets(file_path: Path) -> list[str]:
    """检测 Excel 文件中的 sheet 名称。"""
    xl = pd.ExcelFile(file_path)
    return xl.sheet_names


def read_all_sheets(file_path: Path) -> dict[str, pd.DataFrame]:
    """读取所有 sheet 为 DataFrame 字典。"""
    return pd.read_excel(file_path, sheet_name=None)


def get_download_link(file_path: Path, link_text: str) -> str:
    """生成文件下载链接（HTML a 标签）。"""
    data = file_path.read_bytes()
    b64 = base64.b64encode(data).decode()
    mime = "application/octet-stream"
    if file_path.suffix == ".html":
        mime = "text/html"
    elif file_path.suffix == ".xlsx":
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif file_path.suffix == ".zip":
        mime = "application/zip"
    return f'<a href="data:{mime};base64,{b64}" download="{file_path.name}">{link_text}</a>'


def zip_report_folder(report_dir: Path) -> Path:
    """将报告目录打包为 zip。"""
    zip_path = report_dir.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in report_dir.rglob("*"):
            if file.is_file():
                zf.write(file, file.relative_to(report_dir.parent))
    return zip_path


def validate_inputs(params: dict) -> list[str]:
    """校验必填参数。"""
    errors = []
    required = ["brand_name", "analysis_period", "tracking_days", "compare_months",
                "category", "avg_price", "seasonality", "s_card_price"]
    for key in required:
        if not params.get(key):
            errors.append(f"「{key}」为必填项")
    if params.get("tracking_days", 0) <= 0:
        errors.append("追踪窗口天数必须大于 0")
    if params.get("avg_price", 0) <= 0:
        errors.append("人均消费金额必须大于 0")
    if params.get("s_card_price", 0) < 0:
        errors.append("S卡年费价格不能为负数")
    return errors


# ---------------------------------------------------------------------------
# 侧边栏：数据上传与参数输入
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 1. 上传数据底表")
    uploaded_file = st.file_uploader(
        "上传 Excel 数据底表（需包含 模型一 ~ 模型四 四个 sheet）",
        type=["xlsx", "xls"],
        help="Excel 中需包含命名为「模型一」「模型二」「模型三」「模型四」的四个 sheet",
    )

    st.markdown("---")
    st.markdown("### 2. 必要信息")

    brand_name = st.text_input("品牌名称", placeholder="如：去茶去", value="")
    analysis_period = st.text_input("数据时间段", placeholder="如：2026年5月", value="")
    tracking_days = st.number_input("追踪窗口天数", min_value=1, max_value=365, value=180, step=30)
    compare_months = st.text_input("对比周期描述", placeholder="如：1个月", value="1个月")
    category = st.text_input("品类", placeholder="如：中式正餐", value="")
    avg_price = st.number_input("人均消费金额（元）", min_value=0.0, value=0.0, step=5.0)
    seasonality = st.text_area("淡旺季规律", placeholder="如：夏季为旺季，冬季为淡季", value="", height=60)
    s_card_price = st.number_input("S卡年费价格（元）", min_value=0.0, value=0.0, step=10.0)

    st.markdown("---")
    st.markdown("### 3. 可选信息")

    s_card_benefits = st.text_area(
        "S卡权益说明",
        placeholder="如：开卡送60元代金券+天天88折+周周5折菜品券",
        value="",
        height=60,
    )
    output_dir = st.text_input("报告输出目录", placeholder="如：reports", value="reports")

    st.markdown("---")
    st.markdown("<div style='font-size:0.8rem;color:#8A8580'>v2.0 · 私域运营效果分析报告生成 Skill</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 主区域
# ---------------------------------------------------------------------------
st.markdown('<div class="main-title">📊 私域数据分析工具台</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">上传数据底表 → 填写业务信息 → 一键生成标准化私域运营效果分析报告</div>',
    unsafe_allow_html=True,
)

# 数据预览区
if uploaded_file is not None:
    work_dir = Path("workspace_tmp")
    file_path = save_uploaded_file(uploaded_file, work_dir / "uploads")

    with st.expander("📁 数据底表预览", expanded=True):
        try:
            sheets = read_all_sheets(file_path)
            sheet_names = list(sheets.keys())
            missing = [s for s in ["模型一", "模型二", "模型三", "模型四"] if s not in sheet_names]

            if missing:
                st.error(f"缺少必要的 sheet：{', '.join(missing)}")
            else:
                st.success(f"已检测到 4 个分析模型 sheet：{', '.join(sheet_names[:4])}")

            tabs = st.tabs(sheet_names)
            for tab, (name, df) in zip(tabs, sheets.items()):
                with tab:
                    st.dataframe(df.head(20), use_container_width=True)
                    st.caption(f"{name}：共 {len(df)} 行 × {len(df.columns)} 列")
        except Exception as e:
            st.error(f"读取 Excel 失败：{e}")
else:
    st.info("请在左侧侧边栏上传数据底表并填写业务信息。")

# 参数校验与报告生成
if uploaded_file is not None:
    params = {
        "brand_name": brand_name.strip(),
        "analysis_period": analysis_period.strip(),
        "tracking_days": int(tracking_days),
        "compare_months": compare_months.strip(),
        "category": category.strip(),
        "avg_price": float(avg_price),
        "seasonality": seasonality.strip(),
        "s_card_price": float(s_card_price),
        "s_card_benefits": s_card_benefits.strip(),
    }

    st.markdown("---")
    col_btn, _ = st.columns([1, 3])
    with col_btn:
        generate_clicked = st.button("🚀 生成分析报告", use_container_width=True)

    if generate_clicked:
        errors = validate_inputs(params)
        if errors:
            for err in errors:
                st.error(err)
        else:
            progress_bar = st.progress(0, text="准备生成报告...")
            log_container = st.empty()

            try:
                # 构建输出目录
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_brand = params["brand_name"].replace(" ", "_")
                report_dir = Path(output_dir.strip() or "reports") / f"{safe_brand}-report-{timestamp}"
                charts_dir = report_dir / "assets"
                html_path = report_dir / f"{safe_brand}-report.html"

                def log(msg: str):
                    log_container.info(msg)

                # Step 1: 提取数据
                log("正在提取 4 个模型数据...")
                data_dict = extract_all_models(file_path)
                progress_bar.progress(25, text="数据提取完成")
                time.sleep(0.2)

                # Step 2: 生成图表
                log("正在生成 8 张分析图表...")
                chart_paths = generate_all_charts(data_dict, charts_dir)
                progress_bar.progress(60, text="图表生成完成")
                time.sleep(0.2)

                # Step 3: 生成 HTML 报告
                log("正在组装 HTML 报告...")
                brand_info = {
                    "name": params["brand_name"],
                    "period": params["analysis_period"],
                    "tracking_window": f"{params['tracking_days']}天",
                    "compare_period": params["compare_months"],
                    "category": params["category"],
                    "avg_spend": str(int(params["avg_price"])),
                    "season_info": params["seasonality"],
                    "s_card_price": str(int(params["s_card_price"])),
                    "s_card_benefits": params["s_card_benefits"] or "详见品牌会员权益说明",
                }
                generate_html_report(data_dict, charts_dir, html_path, brand_info)
                progress_bar.progress(90, text="HTML 报告生成完成")
                time.sleep(0.2)

                # Step 4: 打包
                log("正在打包报告...")
                zip_path = zip_report_folder(report_dir)
                progress_bar.progress(100, text="报告生成完毕")

                # 保存结果到 session_state
                st.session_state["report_dir"] = report_dir
                st.session_state["html_path"] = html_path
                st.session_state["zip_path"] = zip_path
                st.session_state["chart_paths"] = chart_paths
                st.session_state["brand_info"] = brand_info
                st.session_state["data_dict"] = data_dict

                st.success(f"报告已生成：{html_path}")

            except Exception as e:
                st.error(f"报告生成失败：{e}")
                st.exception(e)

# 结果展示区
if "html_path" in st.session_state:
    report_dir = st.session_state["report_dir"]
    html_path = st.session_state["html_path"]
    zip_path = st.session_state["zip_path"]
    chart_paths = st.session_state["chart_paths"]
    brand_info = st.session_state["brand_info"]
    data_dict = st.session_state["data_dict"]

    st.markdown("---")
    st.markdown("## 📑 分析结果")

    # 下载区
    dl_col1, dl_col2, dl_col3 = st.columns(3)
    with dl_col1:
        st.markdown(get_download_link(html_path, "⬇️ 下载 HTML 报告"), unsafe_allow_html=True)
    with dl_col2:
        st.markdown(get_download_link(zip_path, "⬇️ 下载报告包（含图表）"), unsafe_allow_html=True)
    with dl_col3:
        # 复制报告目录路径
        st.code(str(report_dir.resolve()), language="text")

    # 执行摘要卡片
    m1 = data_dict.get("model1", {})
    m2 = data_dict.get("model2", {})
    m3 = data_dict.get("model3", {})
    m4 = data_dict.get("model4", {})

    m1_base = m1.get("avg_freq", {}).get("baseline", 0)
    m1_track = m1.get("avg_freq", {}).get("tracking", 0)
    m1_change = (m1_track / m1_base - 1) * 100 if m1_base else 0

    m2_siyu = m2.get("siyu", {}).get("tracking_avg", 0)
    m2_non = m2.get("non_siyu", {}).get("tracking_avg", 0)
    m2_diff = (m2_siyu / m2_non - 1) * 100 if m2_non else 0

    m3_siyu_rep = m3.get("siyu_first", {}).get("repurchase_rate", 0)
    m3_non_rep = m3.get("non_siyu_first", {}).get("repurchase_rate", 0)

    m4_siyu_s = m4.get("siyu_s", {}).get("tracking_avg", 0)

    st.markdown("### 核心指标速览")
    kpi_cols = st.columns(4)
    metrics = [
        ("拉新客户平均消费次数", f"{m1_track:.2f}", f"较基准 {'+' if m1_change >= 0 else ''}{m1_change:.1f}%"),
        ("私域 vs 非私域频次优势", f"{m2_diff:.1f}%", "追踪后1月"),
        ("私域首单新客复购率", f"{m3_siyu_rep:.2f}%", f"高于非私域 {m3_siyu_rep - m3_non_rep:.2f}pp"),
        ("私域买S卡客户频次", f"{m4_siyu_s:.2f}", "四类客户中最高"),
    ]
    for col, (label, value, change) in zip(kpi_cols, metrics):
        with col:
            st.markdown(
                f'<div class="metric-card"><div style="font-size:1.6rem;font-weight:700;color:#B3875E">{value}</div>'
                f'<div style="font-size:0.85rem;color:#8A8580;margin-top:4px">{label}</div>'
                f'<div style="font-size:0.8rem;color:#5E7C6B;margin-top:4px;font-weight:600">{change}</div></div>',
                unsafe_allow_html=True,
            )

    # HTML 报告预览
    st.markdown("### HTML 报告预览")
    html_content = html_path.read_text(encoding="utf-8")
    # 将图表相对路径转换为绝对路径，便于 Streamlit 内嵌预览
    report_rel = str(report_dir).replace("\\", "/")
    html_content = html_content.replace('src="assets/', f'src="{report_rel}/assets/')
    st.components.v1.html(html_content, height=800, scrolling=True)

    # 图表画廊
    st.markdown("### 图表画廊")
    gallery_cols = st.columns(2)
    for idx, chart_path in enumerate(chart_paths):
        with gallery_cols[idx % 2]:
            st.image(str(chart_path), caption=chart_path.name, use_container_width=True)

# ---------------------------------------------------------------------------
# 使用说明
# ---------------------------------------------------------------------------
with st.expander("❓ 使用说明与数据格式"):
    st.markdown("""
    **数据底表要求：**
    - 文件格式：`.xlsx` 或 `.xls`
    - 必须包含 4 个 sheet，命名为：`模型一`、`模型二`、`模型三`、`模型四`
    - 各 sheet 列名支持中英文别名，系统会自动推断

    **四个分析模型：**
    | 模型 | 名称 | 目的 |
    |:---|:---|:---|
    | 模型一 | 效果验证 | 存量老客户进入私域后的频次变化 |
    | 模型二 | 对比验证 | 私域组 vs 非私域对照组的大盘差异 |
    | 模型三 | 归因验证 | 私域首单新客 vs 非私域首单新客的激活差异 |
    | 模型四 | 放大验证 | S卡权益对私域用户的消费放大效应 |

    **产出物：**
    - 本地 HTML 交互式报告（浏览器打开即可查看）
    - 8 张 PNG 分析图表
    - 报告压缩包（含 HTML + 图表）
    """)
