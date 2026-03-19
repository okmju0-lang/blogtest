#!/usr/bin/env python3
"""Mermaid 코드 검증 및 렌더링"""

import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path


def validate_mermaid_syntax(code: str) -> tuple[bool, str]:
    """기본 문법 검증 (키워드 존재 여부)"""
    valid_starts = [
        "graph", "flowchart", "sequenceDiagram", "classDiagram",
        "stateDiagram", "erDiagram", "gantt", "pie", "gitGraph",
        "journey", "quadrantChart", "xychart-beta", "block-beta",
        "timeline", "mindmap", "sankey-beta",
    ]
    code_stripped = code.strip()
    for kw in valid_starts:
        if code_stripped.lower().startswith(kw.lower()):
            return True, ""
    # %%로 시작하는 주석 이후 키워드 확인
    lines = [l.strip() for l in code_stripped.split("\n") if l.strip() and not l.strip().startswith("%%")]
    if lines:
        for kw in valid_starts:
            if lines[0].lower().startswith(kw.lower()):
                return True, ""
    return False, f"인식할 수 없는 Mermaid 다이어그램 유형입니다. 첫 줄: '{lines[0] if lines else ''}'"


def render_mermaid(input_path: str, output_path: str) -> dict:
    in_p = Path(input_path)
    out_p = Path(output_path)

    if not in_p.exists():
        return {"success": False, "error": f"입력 파일이 없습니다: {input_path}"}

    code = in_p.read_text(encoding="utf-8")

    # 문법 검증
    valid, err = validate_mermaid_syntax(code)
    if not valid:
        return {"success": False, "error": err, "mmd_file": str(in_p)}

    # mmdc (mermaid-cli) 사용 시도
    mmdc = shutil.which("mmdc") or shutil.which("mmdc.cmd")
    if mmdc:
        out_p.parent.mkdir(parents=True, exist_ok=True)
        try:
            result = subprocess.run(
                [mmdc, "-i", str(in_p), "-o", str(out_p), "-b", "transparent"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0 and out_p.exists():
                return {"success": True, "mmd_file": str(in_p), "png_file": str(out_p)}
            else:
                # PNG 렌더링 실패해도 .mmd는 유효
                return {
                    "success": True,
                    "mmd_file": str(in_p),
                    "png_file": None,
                    "warning": "PNG 렌더링 실패. .mmd 파일을 수동으로 렌더링하세요.",
                    "error": result.stderr,
                }
        except Exception as e:
            return {
                "success": True,
                "mmd_file": str(in_p),
                "png_file": None,
                "warning": f"mmdc 실행 오류: {e}. .mmd 파일을 수동으로 렌더링하세요.",
            }
    else:
        return {
            "success": True,
            "mmd_file": str(in_p),
            "png_file": None,
            "warning": "mmdc가 설치되어 있지 않습니다. 설치: npm install -g @mermaid-js/mermaid-cli",
        }


def main():
    parser = argparse.ArgumentParser(description="Mermaid 다이어그램 렌더러")
    parser.add_argument("--input", required=True, help="입력 .mmd 파일 경로")
    parser.add_argument("--output", required=True, help="출력 .png 파일 경로")
    args = parser.parse_args()

    result = render_mermaid(args.input, args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
