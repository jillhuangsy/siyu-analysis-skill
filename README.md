# 私域运营效果分析报告生成

基于品牌私域运营数据底表，通过4层递进分析模型，自动生成标准化的私域运营效果分析报告。

---

## 项目简介

本项目是一套独立的 Python 分析工具，用于自动化生成餐饮品牌私域运营效果分析报告。通过读取标准化的 Excel 数据底表，执行效果验证、对比验证、归因验证、放大验证四层分析，最终输出：

- **优先模式**：飞书在线文档（含静态图表图片，需安装飞书CLI）
- **回退模式**：本地 HTML 交互式报告（含 ECharts 图表，无需飞书CLI）
- 8 张 matplotlib 生成的 PNG 图表

分析核心问题：**私域运营是否真正提升了用户消费频次？提升的幅度和归因是否可靠？**

---

## 功能特性

### 四层递进分析模型

| 模型 | 名称 | 分析目的 |
|:---|:---|:---|
| 模型一 | 效果验证 | 存量老客户在私域运营后的频次变化 |
| 模型二 | 对比验证 | 私域组 vs 非私域对照组的大盘差异 |
| 模型三 | 归因验证 | 私域首单新客 vs 非私域首单新客的激活差异 |
| 模型四 | 放大验证 | 会员权益卡对私域用户的消费放大效应 |

### 报告结构（V2 MECE优化版）

1. **报告头部** — 品牌信息、数据时间、业务背景
2. **执行摘要** — 核心结论汇总表 + KPI看板 + 数据说明
3. **模型分析层** — 每模型：口径框 -> 图表 -> 表格 -> 核心发现 -> 口径注意
4. **交叉对比与归因** — 跨模型关联规律
5. **数据攻防推演** — 质疑与回应，增强可信度
6. **运营建议** — P0/P1优先级，自带时间属性
7. **最终结论** — 1-3句话核心总结
8. **附录** — 模型定义、口径说明、术语表、局限性

### 样式规范

- 暖色系调色板：`--bg:#F7F5F2`, `--accent:#B3875E`, `--accent2:#5E7C6B`
- Callout语义系统：positive(✅)、neutral(💡)、warning(⚠️)、risk(❌)
- 响应式布局，适配桌面与移动端

### 双模式输出

| 模式 | 条件 | 输出 |
|:---|:---|:---|
| **优先模式** | 已安装 `lark-cli` | 飞书在线文档（含静态图表图片） |
| **回退模式** | 未安装 `lark-cli` | 本地 HTML 交互式报告（含 ECharts 图表） |

---

## 安装与使用

### 环境要求

- Python 3.9+
- 可选：飞书CLI（用于生成飞书文档）
  - 安装指南：https://open.feishu.cn/document/no_class/mcp-archive/feishu-cli-installation-guide.md

### Python 依赖

```bash
pip install openpyxl pandas matplotlib numpy
```

### 数据底表格式

准备一个 Excel 文件（`.xlsx`），包含以下4个 sheet：

| Sheet 名称 | 内容 |
|:---|:---|
| `模型一` | 进入私域的用户消费数据 |
| `模型二` | 私域组 vs 非私域对照组消费数据 |
| `模型三` | 私域首单新客 vs 非私域首单新客数据 |
| `模型四` | 持卡私域用户 vs 非持卡私域用户数据 |

### 独立运行（Python脚本）

```python
from scripts.extract_data import extract_all_models
from scripts.generate_charts import generate_all_charts
from scripts.generate_report import generate_html_report

# 1. 提取数据
data = extract_all_models("/path/to/data.xlsx")

# 2. 生成图表
charts = generate_all_charts(data, "/path/to/output/charts")

# 3a. 有飞书CLI：生成飞书文档（通过 lark-cli）
# 见 scripts/create_feishu_doc.py

# 3b. 无飞书CLI：生成HTML报告
brand = {
    "name": "去茶去",
    "period": "2026年4月",
    "tracking_window": "180天",
    "compare_period": "2个月",
    "category": "温州休闲茶餐厅（正餐）",
    "avg_spend": "70",
    "season_info": "4月为春夏交替期...",
    "membership_card_info": "会员权益卡（按品牌实际情况填写，无则留空）",
}
generate_html_report(data, "/path/to/output/charts", "/path/to/output/report.html", brand)
```

### AI Agent 调用（可选）

在 AI 平台中，本 Skill 也可以通过对话调用：

```
使用私域运营效果分析报告生成 Skill，
品牌：去茶去，
数据时间：2026年4月，
追踪窗口：180天，
对比周期：1个月，
品类：中式正餐，
人均消费：85元，
淡旺季：夏季为旺季，冬季为淡季，
会员权益卡：（可选，按品牌实际情况填写），
数据文件：去茶去-2026年4月份数据底表.xlsx
```

---

## 快速开始示例

### 示例：为"去茶去"品牌生成报告

**1. 准备数据底表**

确保 Excel 文件包含 `模型一` 至 `模型四` 四个 sheet，每个 sheet 至少包含：
- 会员ID
- 消费时间
- 消费次数
- 是否私域（是/否）
- 是否持卡（是/否，模型四需要，如无会员权益卡体系可省略模型四）

**2. 执行 Skill**

在 TRAE 中输入：

```
使用私域运营效果分析报告生成 Skill，
品牌：去茶去，
数据时间：2026年4月，
追踪窗口：180天，
对比周期：1个月，
品类：中式正餐，
人均消费：85元，
淡旺季：夏季为旺季，冬季为淡季，
会员权益卡：（可选，按品牌实际情况填写），
数据文件：去茶去-2026年4月份数据底表.xlsx
```

**3. 查看产出物**

执行完成后，你将获得：

**有飞书CLI（优先模式）：**
- 飞书文档链接（在线查看和分享）
- 8张PNG图表：`output/charts/*.png`

**无飞书CLI（回退模式）：**
- HTML报告：`output/report.html`（浏览器打开）
- 8张PNG图表：`output/charts/*.png`

---

## 报告模板结构说明

### HTML报告文件结构

```
{brand}-report/
├── {brand}-report.html          # 主报告文件
├── _shared/
│   └── js/
│       └── echarts.min.js        # ECharts 5.x 库
└── assets/
    ├── charts.js                 # 图表配置与数据
    └── *.png                     # matplotlib生成的静态图表
```

### 模板占位符系统

HTML模板使用 `{{PLACEHOLDER}}` 语法，主要占位符分类：

**元数据占位符：**
- `{{BRAND_NAME}}` — 品牌名称
- `{{ANALYSIS_PERIOD}}` — 数据时间段
- `{{TRACKING_DAYS}}` — 追踪窗口天数
- `{{COMPARE_MONTHS}}` — 对比周期
- `{{CATEGORY}}` / `{{AVG_PRICE}}` / `{{SEASONALITY}}` — 业务背景

**模型占位符：**
- `{{MODEL_1_NAME}}` / `{{MODEL_1_SAMPLE_DEF}}` / `{{MODEL_1_FINDING}}` — 模型一各字段
- `{{MODEL_2_*}}` — 模型二各字段
- `{{MODEL_3_*}}` — 模型三各字段
- `{{MODEL_4_*}}` — 模型四各字段

**结论占位符：**
- `{{CONCLUSION_DIM_1~4}}` — 四个结论维度
- `{{CONCLUSION_JUDGE_1~4}}` — 判断结果
- `{{CONCLUSION_EVIDENCE_1~4}}` — 判断依据

**运营建议占位符：**
- `{{ACTION_1_PRIORITY}}` / `{{ACTION_1_TITLE}}` / `{{ACTION_1_BODY}}` — 建议内容

### 模板版本

- `template-report.html` — V1 基础版（3模型）
- `template-report-v2.html` — V2 MECE优化版（4模型，推荐）

---

## 核心原则

1. **结论客观** — 不硬找问题，也不硬写价值
2. **数据支撑** — 每个结论性表述必须有数据支撑
3. **推断有界** — 不做无数据支撑的跨季节推断和跨品牌对比
4. **口径统一** — "私域首单新客"和"非私域首单新客"分组口径全文一致

---

## 贡献指南

### 如何贡献

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -am 'Add some feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 Pull Request

### 报告问题

如发现数据口径问题、模板渲染错误或分析逻辑缺陷，请提交 Issue，并附上：
- 问题描述
- 复现步骤
- 期望行为 vs 实际行为
- 相关数据样本（脱敏后）

### 扩展方向

欢迎贡献以下方向的改进：
- 新增分析模型（如留存分析、LTV分析）
- 支持更多图表类型（如热力图、漏斗图）
- 支持更多输出格式（如 PDF、PPT）
- 多语言支持

---

## License

MIT License

Copyright (c) 2024 Trae Work

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
