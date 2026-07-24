#!/usr/bin/env python3
"""Fail closed when a siyu analysis report misses required structure."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REQUIRED_SECTIONS = [
    "执行摘要",
    "模型一",
    "模型二",
    "模型三",
    "模型四",
    "交叉对比与归因",
    "数据攻防推演",
    "运营建议",
    "最终结论",
    "附录",
]

MODEL_LABELS = {1: "模型一", 2: "模型二", 3: "模型三", 4: "模型四"}


def positions(text: str, labels: list[str]) -> dict[str, int]:
    headings = [
        (match.start(), re.sub(r"<[^>]+>", "", match.group(2)).strip())
        for match in re.finditer(r"<(h[1-6])\b[^>]*>(.*?)</\1>", text, flags=re.I | re.S)
    ]
    result = {}
    for label in labels:
        match = next((position for position, heading in headings if label in heading), None)
        if match is None:
            raise ValueError(f"缺少必需章节：{label}")
        result[label] = match
    return result


def validate(path: Path, available_models: set[int], expected_charts: int) -> None:
    text = path.read_text(encoding="utf-8")
    section_pos = positions(text, REQUIRED_SECTIONS)

    ordered = [section_pos[label] for label in REQUIRED_SECTIONS]
    if ordered != sorted(ordered):
        raise ValueError("必需章节顺序错误")

    chart_matches = list(re.finditer(r"<img\b", text, flags=re.I))
    if len(chart_matches) != expected_charts:
        raise ValueError(f"图表数量错误：期望 {expected_charts}，实际 {len(chart_matches)}")

    for model in available_models:
        label = MODEL_LABELS[model]
        start = section_pos[label]
        later = [position for name, position in section_pos.items() if position > start]
        end = min(later) if later else len(text)
        if not re.search(r"<img\b", text[start:end], flags=re.I):
            raise ValueError(f"{label}章节内没有图表")

    missing_models = set(MODEL_LABELS) - available_models
    for model in missing_models:
        label = MODEL_LABELS[model]
        start = section_pos[label]
        later = [position for name, position in section_pos.items() if position > start]
        end = min(later) if later else len(text)
        model_text = text[start:end]
        if "不可评估" not in model_text:
            raise ValueError(f"{label}缺失时必须标注“不可评估”")

    forbidden = ["Trae Work", "报告生成：", "数据来源：品牌私域运营后台"]
    found = [term for term in forbidden if term in text]
    if found:
        raise ValueError(f"发现禁止的示例或水印：{', '.join(found)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("--available-models", required=True)
    parser.add_argument("--expected-charts", required=True, type=int)
    args = parser.parse_args()

    models = {int(value) for value in args.available_models.split(",") if value.strip()}
    if not models <= set(MODEL_LABELS):
        raise SystemExit("available-models 只能包含 1,2,3,4")

    validate(args.report, models, args.expected_charts)
    print("报告结构校验通过")


if __name__ == "__main__":
    main()
