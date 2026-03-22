#!/usr/bin/env python3
"""개인정보(PII) 패턴 탐지기"""

import re
import sys
import json
import argparse
from pathlib import Path


PATTERNS = {
    "email": r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    "phone_kr": r"0\d{1,2}[\-\s]\d{3,4}[\-\s]\d{4}",
    "rrn": r"\d{6}[\-\s][1-4]\d{6}",
    "business_reg": r"\d{3}[\-]\d{2}[\-]\d{5}",
    "credit_card": r"\d{4}[\s\-]\d{4}[\s\-]\d{4}[\s\-]\d{4}",
}


def detect(text: str) -> dict:
    findings = []
    for pii_type, pattern in PATTERNS.items():
        for m in re.finditer(pattern, text):
            # 문단/문장 위치 추정
            start = m.start()
            lines_before = text[:start].count("\n")
            findings.append({
                "type": pii_type,
                "value": m.group(),
                "position": f"라인 {lines_before + 1} 근처",
            })

    return {
        "has_pii": len(findings) > 0,
        "findings": findings,
    }


def main():
    parser = argparse.ArgumentParser(description="PII 탐지기")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="검사할 파일 경로")
    group.add_argument("--text", help="검사할 텍스트")
    args = parser.parse_args()

    if args.file:
        p = Path(args.file)
        if not p.exists():
            print(json.dumps({"success": False, "error": f"File not found: {args.file}"}))
            sys.exit(1)
        text = p.read_text(encoding="utf-8")
    else:
        text = args.text

    result = detect(text)
    result["success"] = True
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
