#!/usr/bin/env python3
"""AI 이미지 생성 — Gemini API 또는 Pollinations.ai (무료 폴백)"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.parse
from pathlib import Path


def _get_dimensions(image_type: str, aspect_ratio: str = None):
    """aspect_ratio에 따른 픽셀 크기 반환."""
    ratio = aspect_ratio or ("16:9" if image_type == "thumbnail" else "1:1")
    dimensions = {
        "16:9": (1920, 1080),
        "4:3": (1024, 768),
        "1:1": (1024, 1024),
    }
    return ratio, dimensions.get(ratio, (1024, 1024))


def generate_with_pollinations(prompt: str, image_type: str, output_path: str, aspect_ratio: str = None) -> dict:
    """Pollinations.ai를 사용한 무료 이미지 생성 (API 키 불필요)."""
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    ratio, (width, height) = _get_dimensions(image_type, aspect_ratio)
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={int(time.time())}"

    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                image_bytes = resp.read()

            if len(image_bytes) < 5_000:
                raise ValueError(f"생성된 이미지 크기가 너무 작습니다: {len(image_bytes)} bytes")

            out_p.write_bytes(image_bytes)

            return {
                "success": True,
                "file": str(out_p),
                "size_bytes": len(image_bytes),
                "aspect_ratio": ratio,
                "model": "pollinations.ai (free, no API key)",
            }
        except Exception as e:
            if attempt < 2:
                time.sleep(3 * (attempt + 1))
                continue
            return {"success": False, "error": str(e)}

    return {"success": False, "error": "max_retries_exceeded"}


def generate_with_gemini(prompt: str, image_type: str, output_path: str, aspect_ratio: str = None) -> dict:
    """Gemini API를 사용한 이미지 생성."""
    api_key = os.environ.get("GOOGLE_AI_API_KEY")
    if not api_key:
        return {"success": False, "error": "GOOGLE_AI_API_KEY not set"}

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return {"success": False, "error": "google-genai not installed. Run: pip install google-genai"}

    client = genai.Client(api_key=api_key)

    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    ratio, _ = _get_dimensions(image_type, aspect_ratio)
    full_prompt = f"Generate an image with {ratio} aspect ratio. {prompt}"

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.1-flash-image-preview",
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
                "aspect_ratio": ratio,
                "model": "gemini-3.1-flash-image-preview (Nano Banana 2)",
            }
        except Exception as e:
            if attempt < 2:
                time.sleep(3 * (attempt + 1))
                continue
            return {"success": False, "error": str(e)}

    return {"success": False, "error": "max_retries_exceeded"}


def generate_image(prompt: str, image_type: str, output_path: str, aspect_ratio: str = None) -> dict:
    """Gemini API 우선, 실패 시 Pollinations.ai 폴백."""
    api_key = os.environ.get("GOOGLE_AI_API_KEY")
    if api_key and api_key != "your_google_ai_api_key_here":
        result = generate_with_gemini(prompt, image_type, output_path, aspect_ratio)
        if result.get("success"):
            return result

    return generate_with_pollinations(prompt, image_type, output_path, aspect_ratio)


def main():
    parser = argparse.ArgumentParser(description="AI 이미지 생성기 (Nano Banana 2)")
    parser.add_argument("--prompt", required=True, help="이미지 생성 프롬프트")
    parser.add_argument("--type", default="illustration", choices=["thumbnail", "illustration"], help="이미지 유형")
    parser.add_argument("--output", required=True, help="출력 파일 경로 (.png)")
    parser.add_argument("--aspect-ratio", default=None, help="종횡비 (예: 16:9, 1:1, 4:3)")
    args = parser.parse_args()

    result = generate_image(args.prompt, args.type, args.output, args.aspect_ratio)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
