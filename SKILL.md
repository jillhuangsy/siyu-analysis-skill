---
name: siyu-analysis
description: Generate an evidence-based Chinese private-domain (私域) operations effectiveness report from a standardized Excel workbook. Use when asked to analyze a brand's private-domain customer-consumption data, compare private-domain and control cohorts, assess first-order customer activation or membership-card effects, and deliver an HTML report with charts.
---

# 私域运营效果分析

Generate a report only from the supplied workbook. State what the data supports, distinguish association from causation, and retain limitations in the final report.

## Required input

Ask for a `.xlsx` workbook and report context if either is absent:

- Brand name and data period.
- Tracking-window and comparison-period labels.
- Category, average spend, and seasonality information.
- Membership-card price and benefits when model four is in scope.

Expect exactly four worksheets named `模型一` through `模型四`. The production workbook is a summarized, one-row-per-window/per-cohort/per-frequency-tier table beginning on row 3:

| Sheet | Columns after the leading blank/index column |
| --- | --- |
| 模型一 | window, frequency tier, count, total, percentage, average frequency |
| 模型二–四 | window, cohort, frequency tier, count, total, percentage, average frequency |

Use the workbook's cohort labels and values; do not substitute example values. Validate that every needed window, cohort, and frequency tier is present before calculating. If the schema differs, report the missing or unexpected fields and request a mapping rather than guessing.

## Analysis rules

Apply the four models in this order:

1. **效果验证（模型一）**: Describe the private-domain cohort's baseline versus tracking-period frequency and high-frequency (`4次及以上`) share.
2. **对比验证（模型二）**: Compare private-domain and non-private-domain cohorts only within tracking periods. Do not interpret an initial baseline containing 0→1 new customers as a before/after result.
3. **归因验证（模型三）**: Compare first-order private-domain new customers with non-private-domain new customers. Calculate the `2次及以上` repurchase rate by summing the 2-, 3-, and 4+-purchase shares.
4. **放大验证（模型四）**: Compare card and non-card cohorts. Treat purchase of a card as self-selection unless an experimental or matched design is provided.

For every cohort comparison, report sample size, period, absolute values, relative difference or percentage-point difference, and the relevant caveat. Do not claim causal lift, incremental revenue, or ROI without a defensible design and the required revenue/cost inputs. Do not seasonally adjust data unless the user provides a valid adjustment method.

## Generate the deliverables

Use the bundled Python modules for the legacy fixed-format workbook only after schema validation:

```python
from scripts.extract_data import extract_all_models
from scripts.generate_charts import generate_all_charts
from scripts.generate_report import generate_html_report

data = extract_all_models(workbook_path)
chart_paths = generate_all_charts(data, output_dir / "charts")
report_path = generate_html_report(data, "charts", output_dir / "report.html", brand_info)
```

Before releasing output, inspect the generated report and all eight charts. Verify labels, cohort order, periods, chart values, chart filenames, and that no defaults or example-specific values appeared in the output. If the bundled modules do not match the workbook schema or contain fixed sample values, repair or replace the affected calculation before producing the report.

Structure the HTML report as:

1. Header with data period, business context, and measurement scope.
2. Executive summary with evidence and interpretation boundaries.
3. Four model sections: cohort definition, tables, charts, findings, and limitations.
4. Cross-model synthesis and prioritized actions.
5. Methodology, data limitations, and definitions.

Write in concise Chinese. Keep observations, inferences, and recommendations separate. Provide the report path and chart directory in the final response.
