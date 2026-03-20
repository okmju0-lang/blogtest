#!/usr/bin/env python3
"""웹 페이지 스크린샷 캡처 (Playwright 기반)"""

import sys
import json
import asyncio
import argparse
from pathlib import Path


async def capture(url: str, output_path: str, full_page: bool = False,
                  width: int = 1280, height: int = 720,
                  wait_seconds: int = 3) -> dict:
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        return {"success": False, "error": "playwright not installed. Run: pip install playwright && python -m playwright install chromium"}

    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": width, "height": height},
                locale="ko-KR",
            )
            page = await context.new_page()

            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(wait_seconds * 1000)

            # 쿠키/팝업 닫기 시도
            for selector in [
                "button:has-text('Accept')", "button:has-text('동의')",
                "button:has-text('OK')", "button:has-text('Close')",
                "[aria-label='Close']", ".cookie-banner button",
            ]:
                try:
                    btn = page.locator(selector).first
                    if await btn.is_visible(timeout=1000):
                        await btn.click()
                        await page.wait_for_timeout(500)
                except Exception:
                    pass

            await page.screenshot(path=str(out_p), full_page=full_page, type="png")
            title = await page.title()

            await browser.close()

        file_size = out_p.stat().st_size
        return {
            "success": True,
            "file": str(out_p),
            "size_bytes": file_size,
            "url": url,
            "page_title": title,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "url": url}


def main():
    parser = argparse.ArgumentParser(description="웹 페이지 스크린샷 캡처")
    parser.add_argument("--url", required=True, help="캡처할 URL")
    parser.add_argument("--output", required=True, help="출력 파일 경로 (.png)")
    parser.add_argument("--full-page", action="store_true", help="전체 페이지 캡처")
    parser.add_argument("--width", type=int, default=1280, help="뷰포트 너비")
    parser.add_argument("--height", type=int, default=720, help="뷰포트 높이")
    parser.add_argument("--wait", type=int, default=3, help="페이지 로딩 대기 시간(초)")
    args = parser.parse_args()

    result = asyncio.run(capture(args.url, args.output, args.full_page,
                                 args.width, args.height, args.wait))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
