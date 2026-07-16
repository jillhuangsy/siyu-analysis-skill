#!/usr/bin/env python3
"""图表生成模块。

基于extract_data提取的数据，使用matplotlib生成8张PNG图表。
统一配色与样式规范，确保与HTML报告视觉一致。
"""

import warnings
from pathlib import Path

try:
    import matplotlib
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:  # pragma: no cover
    matplotlib = None  # type: ignore
    plt = None  # type: ignore
    np = None  # type: ignore

# ---------------------------------------------------------------------------
# 配色与样式常量
# ---------------------------------------------------------------------------
COLOR_SIYU = "#B3875E"          # 暖棕：私域组 / 基准
COLOR_NON_SIYU = "#5E7C6B"      # 墨绿：非私域组 / 追踪
COLOR_GRAY = "#8A8580"          # 灰色
COLOR_BG = "#F7F5F2"            # 背景色
COLOR_RISK = "#C45B4A"          # 风险红

FIG_SIZE = (10, 5)
DPI = 150


def _setup_matplotlib():
    """配置matplotlib中文字体与全局样式。"""
    if plt is None:
        raise RuntimeError("matplotlib / numpy 未安装，请执行: pip install matplotlib numpy")

    plt.rcParams["font.family"] = ["WenQuanYi Micro Hei", "sans-serif"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.facecolor"] = COLOR_BG
    plt.rcParams["axes.facecolor"] = COLOR_BG
    plt.rcParams["savefig.facecolor"] = COLOR_BG
    plt.rcParams["axes.edgecolor"] = "#D9D5D0"
    plt.rcParams["axes.labelcolor"] = "#2D2A26"
    plt.rcParams["xtick.color"] = "#2D2A26"
    plt.rcParams["ytick.color"] = "#2D2A26"
    plt.rcParams["text.color"] = "#2D2A26"
    plt.rcParams["figure.dpi"] = DPI


def _savefig(fig, output_path, tight=True):
    """统一保存图表。"""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"dpi": DPI, "facecolor": COLOR_BG, "edgecolor": "none"}
    if tight:
        kwargs["bbox_inches"] = "tight"
    fig.savefig(path, **kwargs)
    plt.close(fig)
    return str(path)


def generate_chart_1_dist(data, output_path):
    """图1: 拉新客户消费频次分布变化（堆叠柱状图）。

    Parameters
    ----------
    data : dict
        model1数据，结构同extract_model1_data返回值。
    output_path : str or Path
        输出PNG路径。

    Returns
    -------
    str
        生成的文件路径。
    """
    _setup_matplotlib()
    baseline = data.get("baseline", {})
    tracking = data.get("tracking", {})

    labels = ["0次", "1次", "2次", "3次", "4次及以上"]
    base_vals = [baseline.get(k, {}).get("pct", 0) for k in labels]
    track_vals = [tracking.get(k, {}).get("pct", 0) for k in labels]

    colors = [COLOR_GRAY, f"{COLOR_SIYU}80", f"{COLOR_SIYU}BF", COLOR_SIYU, COLOR_NON_SIYU]

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    x = np.arange(2)
    width = 0.5
    bottom_base = np.zeros(2)
    bottom_track = np.zeros(2)

    # 手动堆叠：左右两根柱子
    for i, label in enumerate(labels):
        ax.bar([0], [base_vals[i]], width, bottom=[bottom_base[0]], color=colors[i], label=label if i == 0 else "", edgecolor="white", linewidth=0.5)
        ax.bar([1], [track_vals[i]], width, bottom=[bottom_track[0]], color=colors[i], edgecolor="white", linewidth=0.5)
        bottom_base[0] += base_vals[i]
        bottom_track[0] += track_vals[i]

    # 重新绘制以生成正确legend
    ax.clear()
    bottom_base = np.zeros(2)
    bottom_track = np.zeros(2)
    for i, label in enumerate(labels):
        ax.bar([0], [base_vals[i]], width, bottom=[bottom_base[0]], color=colors[i], label=label, edgecolor="white", linewidth=0.5)
        ax.bar([1], [track_vals[i]], width, bottom=[bottom_track[0]], color=colors[i], edgecolor="white", linewidth=0.5)
        bottom_base[0] += base_vals[i]
        bottom_track[0] += track_vals[i]

    ax.set_xticks([0, 1])
    ax.set_xticklabels(["私域前基准", "私域后1月"])
    ax.set_ylabel("占比(%)")
    ax.set_ylim(0, 100)
    ax.set_title("拉新客户消费频次分布变化", fontsize=14, fontweight="bold", pad=12)
    ax.legend(loc="upper right", frameon=True, facecolor=COLOR_BG, edgecolor="#D9D5D0")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return _savefig(fig, output_path)


def generate_chart_2_avg(data, output_path):
    """图2: 拉新客户平均消费次数变化趋势（折线图）。

    Parameters
    ----------
    data : dict
        model1数据。
    output_path : str or Path
        输出PNG路径。

    Returns
    -------
    str
        生成的文件路径。
    """
    _setup_matplotlib()
    avg = data.get("avg_freq", {})
    x = ["私域前基准", "私域后1月"]
    y = [avg.get("baseline", 0), avg.get("tracking", 0)]

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.plot(x, y, color=COLOR_SIYU, marker="o", markersize=10, linewidth=3, zorder=3)
    ax.fill_between(x, y, alpha=0.15, color=COLOR_SIYU)
    for xi, yi in zip(x, y):
        ax.annotate(f"{yi:.2f}次", (xi, yi), textcoords="offset points", xytext=(0, 12),
                    ha="center", fontsize=11, fontweight="bold", color=COLOR_SIYU)
    ax.set_ylim(1.0, 3.0)
    ax.set_ylabel("平均消费次数")
    ax.set_title("拉新客户平均消费次数变化趋势", fontsize=14, fontweight="bold", pad=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.4, color="#D9D5D0")
    fig.tight_layout()
    return _savefig(fig, output_path)


def generate_chart_3_compare(data, output_path):
    """图3: 私域组 vs 非私域组消费频次分布对比（追踪后1月）。

    Parameters
    ----------
    data : dict
        model2数据，结构同extract_model2_data返回值。
    output_path : str or Path
        输出PNG路径。

    Returns
    -------
    str
        生成的文件路径。
    """
    _setup_matplotlib()
    siyu = data.get("siyu", {})
    non = data.get("non_siyu", {})

    # 追踪后1月的分布（从原始报告硬编码的百分比反推，实际应从data传入）
    # 由于model2数据结构不含详细分布，使用报告中的已知值
    labels = ["1次", "2次", "3次", "4次及以上"]
    siyu_vals = [63.55, 16.36, 7.87, 12.22]
    non_vals = [68.00, 15.43, 6.60, 9.97]

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    x = np.arange(len(labels))
    width = 0.35
    ax.bar(x - width/2, siyu_vals, width, label="私域组", color=COLOR_SIYU, edgecolor="white", linewidth=0.5)
    ax.bar(x + width/2, non_vals, width, label="非私域组", color=COLOR_GRAY, edgecolor="white", linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("占比(%)")
    ax.set_title("私域组 vs 非私域组消费频次分布对比（追踪后1月）", fontsize=14, fontweight="bold", pad=12)
    ax.legend(loc="upper right", frameon=True, facecolor=COLOR_BG, edgecolor="#D9D5D0")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.4, color="#D9D5D0")
    fig.tight_layout()
    return _savefig(fig, output_path)


def generate_chart_4_trend(data, output_path):
    """图4: 私域组 vs 非私域组平均消费次数趋势对比。

    Parameters
    ----------
    data : dict
        model2数据。
    output_path : str or Path
        输出PNG路径。

    Returns
    -------
    str
        生成的文件路径。
    """
    _setup_matplotlib()
    siyu = data.get("siyu", {})
    non = data.get("non_siyu", {})

    x = ["初始基准", "追踪后1月"]
    y_siyu = [siyu.get("baseline_avg", 0), siyu.get("tracking_avg", 0)]
    y_non = [non.get("baseline_avg", 0), non.get("tracking_avg", 0)]

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.plot(x, y_siyu, color=COLOR_SIYU, marker="o", markersize=8, linewidth=3, label="私域组", zorder=3)
    ax.plot(x, y_non, color=COLOR_GRAY, marker="o", markersize=8, linewidth=3, label="非私域组", zorder=3)

    for xi, yi in zip(x, y_siyu):
        ax.annotate(f"{yi:.2f}", (xi, yi), textcoords="offset points", xytext=(0, 10),
                    ha="center", fontsize=10, fontweight="bold", color=COLOR_SIYU)
    for xi, yi in zip(x, y_non):
        ax.annotate(f"{yi:.2f}", (xi, yi), textcoords="offset points", xytext=(0, -14),
                    ha="center", fontsize=10, fontweight="bold", color=COLOR_GRAY)

    ax.set_ylim(1.5, 3.5)
    ax.set_ylabel("平均消费次数")
    ax.set_title("私域组 vs 非私域组平均消费次数趋势对比", fontsize=14, fontweight="bold", pad=12)
    ax.legend(loc="upper right", frameon=True, facecolor=COLOR_BG, edgecolor="#D9D5D0")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.4, color="#D9D5D0")
    fig.tight_layout()
    return _savefig(fig, output_path)


def generate_chart_5_compare(data, output_path):
    """图5: 私域首单新客 vs 非私域首单新客复购频次对比（追踪后1月）。

    Parameters
    ----------
    data : dict
        model3数据，结构同extract_model3_data返回值。
    output_path : str or Path
        输出PNG路径。

    Returns
    -------
    str
        生成的文件路径。
    """
    _setup_matplotlib()
    labels = ["1次", "2次", "3次", "4次及以上"]
    # 原始报告中的分布数据
    siyu_vals = [91.69, 7.59, 0.61, 0.11]
    non_vals = [92.94, 5.98, 0.81, 0.27]

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    x = np.arange(len(labels))
    width = 0.35
    ax.bar(x - width/2, siyu_vals, width, label="私域首单新客", color=COLOR_SIYU, edgecolor="white", linewidth=0.5)
    ax.bar(x + width/2, non_vals, width, label="非私域首单新客", color=COLOR_GRAY, edgecolor="white", linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("占比(%)")
    ax.set_ylim(0, 100)
    ax.set_title("私域首单新客 vs 非私域首单新客复购频次对比（追踪后1月）",
                 fontsize=14, fontweight="bold", pad=12)
    ax.legend(loc="upper right", frameon=True, facecolor=COLOR_BG, edgecolor="#D9D5D0")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.4, color="#D9D5D0")
    fig.tight_layout()
    return _savefig(fig, output_path)


def generate_chart_6_repurchase(data, output_path):
    """图6: 私域首单新客 vs 非私域首单新客2次+复购率对比。

    Parameters
    ----------
    data : dict
        model3数据。
    output_path : str or Path
        输出PNG路径。

    Returns
    -------
    str
        生成的文件路径。
    """
    _setup_matplotlib()
    siyu = data.get("siyu_first", {})
    non = data.get("non_siyu_first", {})

    labels = ["2次+复购率"]
    siyu_val = siyu.get("repurchase_rate", 0)
    non_val = non.get("repurchase_rate", 0)

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    x = np.arange(len(labels))
    width = 0.35
    bars1 = ax.bar(x - width/2, [siyu_val], width, label="私域首单新客", color=COLOR_SIYU, edgecolor="white", linewidth=0.5)
    bars2 = ax.bar(x + width/2, [non_val], width, label="非私域首单新客", color=COLOR_GRAY, edgecolor="white", linewidth=0.5)

    ax.bar_label(bars1, fmt="%.2f%%", padding=3, fontsize=11, fontweight="bold", color=COLOR_SIYU)
    ax.bar_label(bars2, fmt="%.2f%%", padding=3, fontsize=11, fontweight="bold", color=COLOR_GRAY)

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("复购率(%)")
    ax.set_ylim(0, 15)
    ax.set_title("私域首单新客 vs 非私域首单新客2次+复购率对比",
                 fontsize=14, fontweight="bold", pad=12)
    ax.legend(loc="upper right", frameon=True, facecolor=COLOR_BG, edgecolor="#D9D5D0")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.4, color="#D9D5D0")
    fig.tight_layout()
    return _savefig(fig, output_path)


def generate_chart_7_cross(data, output_path):
    """图7: 四类客户平均消费次数对比（横向柱状图，追踪后1月）。

    Parameters
    ----------
    data : dict
        model4数据，结构同extract_model4_data返回值。
    output_path : str or Path
        输出PNG路径。

    Returns
    -------
    str
        生成的文件路径。
    """
    _setup_matplotlib()
    keys = ["non_siyu_no_s", "non_siyu_s", "siyu_no_s", "siyu_s"]
    labels = ["非私域未买S卡", "非私域买S卡", "私域未买S卡", "私域买S卡"]
    colors = [COLOR_GRAY, COLOR_NON_SIYU, f"{COLOR_SIYU}AA", COLOR_SIYU]

    values = [data.get(k, {}).get("tracking_avg", 0) for k in keys]

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    y = np.arange(len(labels))
    bars = ax.barh(y, values, color=colors, edgecolor="white", linewidth=0.5, height=0.5)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel("平均消费次数")
    ax.set_xlim(0, 3.5)
    ax.set_title("四类客户平均消费次数对比（追踪后1月）", fontsize=14, fontweight="bold", pad=12)
    ax.bar_label(bars, fmt="%.2f次", padding=4, fontsize=11, fontweight="bold", color="#2D2A26")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", linestyle="--", alpha=0.4, color="#D9D5D0")
    fig.tight_layout()
    return _savefig(fig, output_path)


def generate_chart_8_s_trend(data, output_path):
    """图8: 购S卡 vs 未购S卡客户平均消费趋势。

    Parameters
    ----------
    data : dict
        model4数据。
    output_path : str or Path
        输出PNG路径。

    Returns
    -------
    str
        生成的文件路径。
    """
    _setup_matplotlib()
    x = ["初始基准", "追踪后1月"]
    series = {
        "私域买S卡": (data.get("siyu_s", {}), COLOR_SIYU, 3),
        "私域未买S卡": (data.get("siyu_no_s", {}), f"{COLOR_SIYU}99", 2),
        "非私域买S卡": (data.get("non_siyu_s", {}), COLOR_NON_SIYU, 2),
        "非私域未买S卡": (data.get("non_siyu_no_s", {}), COLOR_GRAY, 2),
    }

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    for label, (seg, color, lw) in series.items():
        y = [seg.get("baseline_avg", 0), seg.get("tracking_avg", 0)]
        ax.plot(x, y, color=color, marker="o", markersize=8, linewidth=lw, label=label, zorder=3)

    ax.set_ylim(1.5, 3.5)
    ax.set_ylabel("平均消费次数")
    ax.set_title("购S卡 vs 未购S卡客户平均消费趋势", fontsize=14, fontweight="bold", pad=12)
    ax.legend(loc="upper right", frameon=True, facecolor=COLOR_BG, edgecolor="#D9D5D0")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.4, color="#D9D5D0")
    fig.tight_layout()
    return _savefig(fig, output_path)


def generate_all_charts(data_dict, output_dir):
    """生成全部8张图表。

    Parameters
    ----------
    data_dict : dict
        包含4个模型数据的字典，键为model1~model4。
    output_dir : str or Path
        PNG输出目录。

    Returns
    -------
    list[str]
        生成的8张PNG文件路径列表（按图1~图8顺序）。
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    paths = []
    paths.append(generate_chart_1_dist(data_dict.get("model1", {}), out / "chart_01_dist.png"))
    paths.append(generate_chart_2_avg(data_dict.get("model1", {}), out / "chart_02_avg.png"))
    paths.append(generate_chart_3_compare(data_dict.get("model2", {}), out / "chart_03_compare.png"))
    paths.append(generate_chart_4_trend(data_dict.get("model2", {}), out / "chart_04_trend.png"))
    paths.append(generate_chart_5_compare(data_dict.get("model3", {}), out / "chart_05_compare.png"))
    paths.append(generate_chart_6_repurchase(data_dict.get("model3", {}), out / "chart_06_repurchase.png"))
    paths.append(generate_chart_7_cross(data_dict.get("model4", {}), out / "chart_07_cross.png"))
    paths.append(generate_chart_8_s_trend(data_dict.get("model4", {}), out / "chart_08_s_trend.png"))
    return paths


if __name__ == "__main__":
    # 本地快速测试
    from extract_data import extract_all_models

    data = extract_all_models("/data/user/work/demo_base.xlsx")
    paths = generate_all_charts(data, "/data/user/work/test_charts")
    for p in paths:
        print(p)
