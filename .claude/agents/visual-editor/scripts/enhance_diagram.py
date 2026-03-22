#!/usr/bin/env python3
"""Mermaid 다이어그램 전문 스타일링 강화"""

import sys
import json
import re
import argparse
from pathlib import Path


# 카테고리별 프로페셔널 테마
THEMES = {
    "case-study": {
        "primary": "#1565C0",
        "primary_light": "#E3F2FD",
        "secondary": "#0D47A1",
        "accent": "#FF6F00",
        "text": "#1A1A2E",
        "bg": "#FFFFFF",
        "border": "#1565C0",
        "success": "#2E7D32",
        "node_radius": "8px",
    },
    "thought-leadership": {
        "primary": "#4A148C",
        "primary_light": "#F3E5F5",
        "secondary": "#6A1B9A",
        "accent": "#FFD600",
        "text": "#1A1A2E",
        "bg": "#FFFFFF",
        "border": "#4A148C",
        "success": "#2E7D32",
        "node_radius": "12px",
    },
    "company-news": {
        "primary": "#2E7D32",
        "primary_light": "#E8F5E9",
        "secondary": "#1B5E20",
        "accent": "#FF6F00",
        "text": "#1A1A2E",
        "bg": "#FFFFFF",
        "border": "#2E7D32",
        "success": "#1565C0",
        "node_radius": "8px",
    },
    "ai-trend": {
        "primary": "#00838F",
        "primary_light": "#E0F7FA",
        "secondary": "#006064",
        "accent": "#E040FB",
        "text": "#1A1A2E",
        "bg": "#FFFFFF",
        "border": "#00838F",
        "success": "#2E7D32",
        "node_radius": "10px",
    },
}

CATEGORY_MAP = {
    "Case Study": "case-study",
    "Thought Leadership": "thought-leadership",
    "Company News": "company-news",
    "AI Trend": "ai-trend",
}


def enhance_diagram(input_path: str, output_path: str, category: str) -> dict:
    in_p = Path(input_path)
    out_p = Path(output_path)

    if not in_p.exists():
        return {"success": False, "error": f"입력 파일이 없습니다: {input_path}"}

    code = in_p.read_text(encoding="utf-8")
    cat_key = CATEGORY_MAP.get(category, "ai-trend")
    theme = THEMES[cat_key]

    enhanced = _apply_professional_style(code, theme)

    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(enhanced, encoding="utf-8")

    return {
        "success": True,
        "input": str(in_p),
        "output": str(out_p),
        "category_theme": cat_key,
    }


def _apply_professional_style(code: str, theme: dict) -> str:
    """기존 Mermaid 코드의 인라인 스타일을 전문적 테마로 교체"""
    lines = code.strip().split("\n")
    cleaned = []
    style_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("style "):
            continue  # 기존 스타일 제거
        cleaned.append(line)

    # 노드 ID 추출
    node_ids = set()
    for line in cleaned:
        # graph/flowchart 노드 패턴: ID[...] 또는 ID{...} 또는 ID(...)
        matches = re.findall(r'(?:^|\s)(\w+)\s*[\[\{\(]', line)
        node_ids.update(matches)
        # subgraph ID
        sg = re.match(r'\s*subgraph\s+(\w+)', line)
        if sg:
            node_ids.add(sg.group(1))

    # 키워드 제거
    node_ids -= {"graph", "flowchart", "subgraph", "direction", "end",
                 "sequenceDiagram", "classDiagram", "stateDiagram",
                 "erDiagram", "gantt", "pie", "gitGraph", "TB", "LR",
                 "TD", "BT", "RL", "style", "click", "class", "participant"}

    # 전문적 스타일 생성
    node_list = sorted(node_ids)
    for i, node_id in enumerate(node_list):
        if i == 0:
            # 첫 노드 (보통 시작/메인) - 강조
            style_lines.append(
                f"    style {node_id} fill:{theme['primary']},stroke:{theme['border']},"
                f"color:#fff,stroke-width:2px"
            )
        elif i == len(node_list) - 1:
            # 마지막 노드 (결과) - 성공 색상
            style_lines.append(
                f"    style {node_id} fill:{theme['success']},stroke:{theme['success']},"
                f"color:#fff,stroke-width:2px"
            )
        elif i % 3 == 0:
            # 강조 노드
            style_lines.append(
                f"    style {node_id} fill:{theme['accent']},stroke:{theme['accent']},"
                f"color:#fff,stroke-width:2px"
            )
        elif i % 2 == 0:
            # 서브 노드
            style_lines.append(
                f"    style {node_id} fill:{theme['primary_light']},stroke:{theme['primary']},"
                f"color:{theme['text']},stroke-width:1.5px"
            )
        else:
            # 일반 노드
            style_lines.append(
                f"    style {node_id} fill:{theme['bg']},stroke:{theme['primary']},"
                f"color:{theme['text']},stroke-width:1.5px"
            )

    result = "\n".join(cleaned)
    if style_lines:
        result += "\n" + "\n".join(style_lines) + "\n"

    return result


def main():
    parser = argparse.ArgumentParser(description="Mermaid 다이어그램 전문 스타일링")
    parser.add_argument("--input", required=True, help="입력 .mmd 파일 경로")
    parser.add_argument("--output", required=True, help="출력 .mmd 파일 경로")
    parser.add_argument("--category", default="AI Trend",
                        choices=["Case Study", "Thought Leadership", "Company News", "AI Trend"],
                        help="카테고리")
    args = parser.parse_args()

    result = enhance_diagram(args.input, args.output, args.category)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
