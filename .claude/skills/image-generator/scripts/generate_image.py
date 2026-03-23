#!/usr/bin/env python3
"""
Nano Banana 2 (gemini-3.1-flash-image-preview) 전용 이미지 생성기

블로그 포스트 최종본에서 핵심 내용 2가지에 어울리는 일러스트 + 썸네일 1장을 생성한다.
API 호출은 이미지 생성에만 사용하며, 텍스트 분석은 호출하는 Orchestrator/LLM이 수행한다.

사용법:
    # 개별 이미지 생성
    python generate_image.py single --prompt "..." --type illustration --output path.png

    # 블로그 포스트 전체 이미지 일괄 생성 (3장)
    python generate_image.py batch --post-dir output/drafts/post_20260323_1 \
        --thumbnail-prompt "..." \
        --illustration1-prompt "..." \
        --illustration2-prompt "..."

환경 변수:
    GOOGLE_AI_API_KEY — Google AI API 키 (필수)
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path


def generate_image(prompt: str, image_type: str, output_path: str) -> dict:
    """Nano Banana 2로 단일 이미지를 생성한다.

    Args:
        prompt: 영문 이미지 생성 프롬프트
        image_type: "thumbnail" | "illustration"
        output_path: 출력 파일 경로 (.png)

    Returns:
        dict: {"success": bool, "file": str, ...} 또는 {"success": False, "error": str}
    """
    api_key = os.environ.get("GOOGLE_AI_API_KEY")
    if not api_key or api_key == "your_google_ai_api_key_here":
        return {"success": False, "error": "GOOGLE_AI_API_KEY 환경 변수가 설정되지 않았습니다."}

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return {"success": False, "error": "google-genai 미설치. 실행: pip install google-genai"}

    client = genai.Client(api_key=api_key)

    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    # 이미지 타입별 비율 설정
    if image_type == "thumbnail":
        aspect = "16:9"
    else:  # illustration
        aspect = "4:3"

    for attempt in range(2):
        try:
            response = client.models.generate_content(
                model="gemini-3.1-flash-image-preview",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect,
                        image_size="2K",
                    ),
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
                raise ValueError(f"생성된 이미지가 너무 작습니다: {file_size} bytes")

            return {
                "success": True,
                "file": str(out_p),
                "size_bytes": file_size,
                "aspect_ratio": aspect,
                "image_type": image_type,
                "model": "gemini-3.1-flash-image-preview (Nano Banana 2)",
            }
        except Exception as e:
            if attempt < 1:
                time.sleep(5)
                continue
            return {"success": False, "error": str(e), "image_type": image_type}

    return {"success": False, "error": "max_retries_exceeded", "image_type": image_type}


def batch_generate(post_dir: str, thumbnail_prompt: str,
                   illustration1_prompt: str, illustration2_prompt: str) -> dict:
    """블로그 포스트용 이미지 3장을 일괄 생성한다.

    Args:
        post_dir: 포스트 drafts 디렉토리 (예: output/drafts/post_20260323_1)
        thumbnail_prompt: 썸네일 프롬프트 (영문)
        illustration1_prompt: 일러스트 1 프롬프트 (영문)
        illustration2_prompt: 일러스트 2 프롬프트 (영문)
    """
    images_dir = Path(post_dir) / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    results = {"total": 3, "success_count": 0, "images": []}

    tasks = [
        ("thumbnail", thumbnail_prompt, str(images_dir / "thumbnail.png")),
        ("illustration", illustration1_prompt, str(images_dir / "illustration_1.png")),
        ("illustration", illustration2_prompt, str(images_dir / "illustration_2.png")),
    ]

    for image_type, prompt, output_path in tasks:
        print(f"  [{image_type}] 생성 중...")
        result = generate_image(prompt, image_type, output_path)
        results["images"].append(result)
        if result.get("success"):
            results["success_count"] += 1
            print(f"  [{image_type}] 완료 ({result['size_bytes']} bytes)")
        else:
            print(f"  [{image_type}] 실패: {result.get('error', 'unknown')}")

    results["all_success"] = results["success_count"] == results["total"]
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Nano Banana 2 이미지 생성기 (일러스트 + 썸네일)"
    )
    subparsers = parser.add_subparsers(dest="mode")

    # 개별 이미지 생성
    single = subparsers.add_parser("single", help="단일 이미지 생성")
    single.add_argument("--prompt", required=True, help="이미지 생성 프롬프트 (영문)")
    single.add_argument(
        "--type", required=True, choices=["thumbnail", "illustration"],
        help="이미지 유형",
    )
    single.add_argument("--output", required=True, help="출력 파일 경로 (.png)")

    # 일괄 생성 (3장)
    batch = subparsers.add_parser("batch", help="블로그 포스트 이미지 일괄 생성 (3장)")
    batch.add_argument("--post-dir", required=True, help="포스트 디렉토리 경로")
    batch.add_argument("--thumbnail-prompt", required=True, help="썸네일 프롬프트")
    batch.add_argument("--illustration1-prompt", required=True, help="일러스트 1 프롬프트")
    batch.add_argument("--illustration2-prompt", required=True, help="일러스트 2 프롬프트")

    # 하위 명령 없이 --prompt 등으로도 사용 가능 (하위 호환)
    parser.add_argument("--prompt", help="이미지 생성 프롬프트 (영문)")
    parser.add_argument(
        "--type", choices=["thumbnail", "illustration"],
        help="이미지 유형",
    )
    parser.add_argument("--output", help="출력 파일 경로 (.png)")
    parser.add_argument("--batch", action="store_true", help="일괄 생성 모드")
    parser.add_argument("--post-dir", help="포스트 디렉토리 경로")
    parser.add_argument("--thumbnail-prompt", help="썸네일 프롬프트")
    parser.add_argument("--illustration1-prompt", help="일러스트 1 프롬프트")
    parser.add_argument("--illustration2-prompt", help="일러스트 2 프롬프트")

    args = parser.parse_args()

    # .env 로드
    env_path = Path(__file__).resolve().parents[3] / ".env"
    if env_path.exists():
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())

    if args.mode == "batch" or args.batch:
        post_dir = getattr(args, "post_dir", None)
        tp = getattr(args, "thumbnail_prompt", None)
        ip1 = getattr(args, "illustration1_prompt", None)
        ip2 = getattr(args, "illustration2_prompt", None)

        if not all([post_dir, tp, ip1, ip2]):
            print("[오류] --batch 모드에는 --post-dir, --thumbnail-prompt, "
                  "--illustration1-prompt, --illustration2-prompt 가 필요합니다.")
            sys.exit(1)

        print("[이미지 일괄 생성] 3장 (썸네일 1 + 일러스트 2)")
        result = batch_generate(post_dir, tp, ip1, ip2)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result["all_success"] else 1)

    elif args.mode == "single" or (args.prompt and args.type and args.output):
        prompt = args.prompt
        img_type = args.type
        output = args.output

        result = generate_image(prompt, img_type, output)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result.get("success") else 1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
