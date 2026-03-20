#!/usr/bin/env python3
"""Nano Banana Pro (gemini-3-pro-image-preview)를 사용한 고품질 일러스트레이션 생성"""

import os
import sys
import json
import time
import argparse
from pathlib import Path


def generate_illustration(prompt: str, output_path: str, aspect_ratio: str = "4:3") -> dict:
    api_key = os.environ.get("GOOGLE_AI_API_KEY")
    if not api_key:
        return {"success": False, "error": "GOOGLE_AI_API_KEY 환경 변수가 설정되지 않았습니다."}

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return {"success": False, "error": "google-genai not installed. Run: pip install google-genai"}

    client = genai.Client(api_key=api_key)

    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    full_prompt = f"Generate a high-quality editorial illustration with {aspect_ratio} aspect ratio. {prompt}"

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                ),
            )

            image_part = None
            if response.candidates:
                for part in response.candidates[0].content.parts:
                    if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                        image_part = part
                        break

            if not image_part:
                raise ValueError("이미지 생성 결과가 비어 있습니다.")

            image_bytes = image_part.inline_data.data
            out_p.write_bytes(image_bytes)

            file_size = out_p.stat().st_size
            if file_size < 10_000:
                raise ValueError(f"생성된 이미지 크기가 너무 작습니다: {file_size} bytes")

            return {
                "success": True,
                "file": str(out_p),
                "size_bytes": file_size,
                "aspect_ratio": aspect_ratio,
                "model": "gemini-3-pro-image-preview (Nano Banana Pro)",
            }
        except Exception as e:
            if attempt < 2:
                time.sleep(3 * (attempt + 1))
                continue
            return {"success": False, "error": str(e)}

    return {"success": False, "error": "max_retries_exceeded"}


def main():
    parser = argparse.ArgumentParser(description="Nano Banana Pro 일러스트레이션 생성기")
    parser.add_argument("--prompt", required=True, help="이미지 생성 프롬프트 (영문)")
    parser.add_argument("--output", required=True, help="출력 파일 경로 (.png)")
    parser.add_argument("--aspect-ratio", default="4:3", help="종횡비 (예: 16:9, 1:1, 4:3)")
    args = parser.parse_args()

    result = generate_illustration(args.prompt, args.output, args.aspect_ratio)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
