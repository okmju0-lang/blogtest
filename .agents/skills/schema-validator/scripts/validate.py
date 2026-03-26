#!/usr/bin/env python3
"""산출물 파일 구조 검증기"""

import sys
import json
import re
import argparse
from pathlib import Path


SCHEMAS = {
    "summary": {
        "sections": ["요약", "인사이트"],
        "min_insights": 3,
        "requires_ax_tag": True,
        "min_chars": 100,
    },
    "story_idea": {
        "required_fields": ["제목", "앵글", "카테고리", "소스", "핵심 논점"],
    },
    "review": {
        "required_sections": ["기밀 필터링", "critical_count", "confidential_count", "팩트체크"],
    },
    "brand_feedback": {
        "required_text": ["가이드", "브랜드"],
    },
    "seo_feedback": {
        "required_sections": ["제목", "메타 디스크립션", "키워드", "헤딩"],
    },
    "draft": {
        "min_chars": 1500,
        "required_sections": ["메타 디스크립션", "카테고리", "소스"],
    },
}


def validate(file_path: str, schema_name: str) -> dict:
    p = Path(file_path)
    if not p.exists():
        return {"valid": False, "schema": schema_name, "file": file_path, "errors": [f"파일이 없습니다: {file_path}"]}

    content = p.read_text(encoding="utf-8")
    schema = SCHEMAS.get(schema_name)
    if not schema:
        return {"valid": False, "schema": schema_name, "file": file_path, "errors": [f"알 수 없는 스키마: {schema_name}"]}

    errors = []

    # 공통: 파일 크기 확인
    min_chars = schema.get("min_chars", 0)
    if len(content) < min_chars:
        errors.append(f"파일이 너무 짧습니다: {len(content)}자 (최소 {min_chars}자 필요)")

    # 섹션 존재 여부
    for section in schema.get("sections", []) + schema.get("required_sections", []):
        if section not in content:
            errors.append(f"필수 섹션이 없습니다: '{section}'")

    # 필수 필드
    for field in schema.get("required_fields", []):
        if field not in content:
            errors.append(f"필수 필드가 없습니다: '{field}'")

    # 필수 텍스트
    for text in schema.get("required_text", []):
        if text not in content:
            errors.append(f"필수 텍스트가 없습니다: '{text}'")

    # 인사이트 개수 (summary 스키마)
    if schema_name == "summary" and schema.get("min_insights"):
        # "인사이트" 항목 개수 추정 (번호 목록 또는 - 목록)
        insight_items = re.findall(r"^(?:\d+\.|[-*])\s+.+", content, re.MULTILINE)
        if len(insight_items) < schema["min_insights"]:
            errors.append(f"핵심 인사이트가 {len(insight_items)}개로 최소 {schema['min_insights']}개 미만입니다.")

    # AX 관련성 태그 (summary 스키마)
    if schema.get("requires_ax_tag") and "AX" not in content and "ax" not in content.lower():
        errors.append("AX 관련성 태그가 없습니다.")

    # critical_count, confidential_count 숫자 존재 여부 (review 스키마)
    if schema_name == "review":
        if not re.search(r"critical_count\s*:\s*\d+", content):
            errors.append("critical_count 값이 없습니다.")
        if not re.search(r"confidential_count\s*:\s*\d+", content):
            errors.append("confidential_count 값이 없습니다.")

    return {
        "valid": len(errors) == 0,
        "schema": schema_name,
        "file": file_path,
        "errors": errors,
    }


def main():
    parser = argparse.ArgumentParser(description="산출물 파일 구조 검증기")
    parser.add_argument("--file", required=True, help="검증할 파일 경로")
    parser.add_argument("--schema", required=True, choices=list(SCHEMAS.keys()), help="검증 스키마")
    args = parser.parse_args()

    result = validate(args.file, args.schema)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
