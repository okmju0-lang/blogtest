#!/usr/bin/env python3
"""Gemini API (Nano Banana 2)를 사용한 AI 이미지 생성"""

import os
import sys
import json
import time
import base64
import argparse
from pathlib import Path


RESOLUTIONS = {
    "thumbnail": {"width": 1920, "height": 1080},
    "illustration": {"width": 1024, "height": 1024},
}


def generate_image(prompt: str, image_type: str, output_path: str) -> dict:
    api_key = os.environ.get("GOOGLE_AI_API_KEY")
    if not api_key:
        return {"success": False, "error": "GOOGLE_AI_API_KEY 환경 변수가 설정되지 않았습니다."}

    try:
        import google.generativeai as genai
    except ImportError:
        return {"success": False, "error": "google-genai not installed. Run: pip install google-genai"}

    genai.configure(api_key=api_key)
    res = RESOLUTIONS.get(image_type, RESOLUTIONS["illustration"])

    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    for attempt in range(3):
        try:
            model = genai.ImageGenerationModel("gemini-3.1-flash-image-preview")
            result = model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="16:9" if image_type == "thumbnail" else "1:1",
            )
            if not result.images:
                raise ValueError("이미지 생성 결과가 비어 있습니다.")

            image_data = result.images[0]._image_bytes
            out_p.write_bytes(image_data)

            file_size = out_p.stat().st_size
            if file_size < 10_000:
                raise ValueError(f"생성된 이미지 크기가 너무 작습니다: {file_size} bytes")

            return {
                "success": True,
                "file": str(out_p),
                "size_bytes": file_size,
                "resolution": f"{res['width']}x{res['height']}",
            }
        except Exception as e:
            if attempt < 2:
                time.sleep(3 * (attempt + 1))
                continue
            return {"success": False, "error": str(e)}

    return {"success": False, "error": "max_retries_exceeded"}


def main():
    parser = argparse.ArgumentParser(description="AI 이미지 생성기")
    parser.add_argument("--prompt", required=True, help="이미지 생성 프롬프트")
    parser.add_argument("--type", default="illustration", choices=["thumbnail", "illustration"], help="이미지 유형")
    parser.add_argument("--output", required=True, help="출력 파일 경로 (.png)")
    args = parser.parse_args()

    result = generate_image(args.prompt, args.type, args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
