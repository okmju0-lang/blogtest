#!/usr/bin/env python3
"""Mermaid 코드 검증 및 렌더링."""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


KOREAN_FONT_FAMILY = (
    "Pretendard, 'Noto Sans KR', 'Apple SD Gothic Neo', "
    "'Malgun Gothic', 'Nanum Gothic', sans-serif"
)

ALLOWED_ACRONYM_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9&/+\-]{1,7}$")


def validate_mermaid_syntax(code: str) -> tuple[bool, str]:
    """기본 Mermaid 문법 헤더를 검증한다."""
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

    lines = [
        line.strip()
        for line in code_stripped.splitlines()
        if line.strip() and not line.strip().startswith("%%")
    ]
    if lines:
        for kw in valid_starts:
            if lines[0].lower().startswith(kw.lower()):
                return True, ""

    first_line = lines[0] if lines else ""
    return False, f"인식할 수 없는 Mermaid 다이어그램 유형입니다. 첫 줄: '{first_line}'"


def find_english_only_labels(code: str) -> list[str]:
    """한글 없이 영문으로만 작성된 라벨을 찾는다."""
    candidates = []
    patterns = [
        r"\[(.*?)\]",
        r"\((.*?)\)",
        r"\{(.*?)\}",
        r'"([^"]+)"',
        r"subgraph\s+([^\n]+)",
        r"participant\s+\w+\s+as\s+([^\n]+)",
    ]

    for pattern in patterns:
        candidates.extend(re.findall(pattern, code, flags=re.MULTILINE))

    violations = []
    seen = set()
    for raw in candidates:
        label = re.sub(r"<br\s*/?>", " ", raw, flags=re.IGNORECASE).strip().strip("\"'")
        label = re.sub(r"\s+", " ", label)
        if not label or label in seen:
            continue
        seen.add(label)

        if re.search(r"[가-힣]", label):
            continue

        english_chunks = re.findall(r"[A-Za-z][A-Za-z0-9&/+\-]*", label)
        if not english_chunks:
            continue

        if all(ALLOWED_ACRONYM_PATTERN.fullmatch(chunk) for chunk in english_chunks):
            continue

        violations.append(label)

    return violations


def build_mermaid_config() -> dict:
    """한글 렌더링을 위한 Mermaid 설정을 만든다."""
    return {
        "theme": "base",
        "themeVariables": {
            "fontFamily": KOREAN_FONT_FAMILY,
        },
    }


def render_mermaid(input_path: str, output_path: str) -> dict:
    in_p = Path(input_path)
    out_p = Path(output_path)

    if not in_p.exists():
        return {"success": False, "error": f"입력 파일이 없습니다: {input_path}"}

    code = in_p.read_text(encoding="utf-8")

    valid, err = validate_mermaid_syntax(code)
    if not valid:
        return {"success": False, "error": err, "mmd_file": str(in_p)}

    english_labels = find_english_only_labels(code)

    mmdc = shutil.which("mmdc") or shutil.which("mmdc.cmd")
    if not mmdc:
        return {
            "success": True,
            "mmd_file": str(in_p),
            "png_file": None,
            "warning": "mmdc가 설치되어 있지 않습니다. 설치: npm install -g @mermaid-js/mermaid-cli",
        }

    out_p.parent.mkdir(parents=True, exist_ok=True)
    config_path = None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(build_mermaid_config(), f, ensure_ascii=False)
            config_path = f.name

        result = subprocess.run(
            [mmdc, "-i", str(in_p), "-o", str(out_p), "-b", "transparent", "-c", config_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and out_p.exists():
            response = {
                "success": True,
                "mmd_file": str(in_p),
                "png_file": str(out_p),
                "font_family": KOREAN_FONT_FAMILY,
                "text_language_priority": "ko-first",
            }
            if english_labels:
                joined = ", ".join(english_labels[:3])
                response["warning"] = (
                    "다이어그램 텍스트는 한글 우선이 권장됩니다. "
                    f"영문 라벨 감지: {joined}"
                )
            return response

        return {
            "success": True,
            "mmd_file": str(in_p),
            "png_file": None,
            "warning": "PNG 렌더링에 실패했습니다. .mmd 파일은 유지됩니다.",
            "error": result.stderr,
            "text_language_priority": "ko-first",
        }
    except Exception as e:
        return {
            "success": True,
            "mmd_file": str(in_p),
            "png_file": None,
            "warning": f"mmdc 실행 오류: {e}. .mmd 파일은 유지됩니다.",
            "text_language_priority": "ko-first",
        }
    finally:
        if config_path:
            Path(config_path).unlink(missing_ok=True)


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
