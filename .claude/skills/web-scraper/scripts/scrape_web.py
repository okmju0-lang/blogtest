#!/usr/bin/env python3
"""웹 페이지 본문 추출기"""

import sys
import time
import json
import hashlib
import argparse
from datetime import datetime
from pathlib import Path


def url_hash(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:10]


def scrape(url: str, url_hash_val: str, output_dir: str) -> dict:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    out_file = output_path / f"web_{url_hash_val}.md"
    skip_log = output_path / "_skip_log.md"

    for attempt in range(3):
        try:
            import requests
            headers = {"User-Agent": "Mozilla/5.0 (compatible; AXBlogBot/1.0)"}
            resp = requests.get(url, headers=headers, timeout=15)

            if resp.status_code in (401, 403, 407, 429):
                _log_skip(skip_log, f"web_{url_hash_val}", f"HTTP_{resp.status_code}", url)
                return {"success": False, "skipped": True, "reason": f"HTTP {resp.status_code}"}

            if resp.status_code >= 400:
                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                _log_skip(skip_log, f"web_{url_hash_val}", f"HTTP_{resp.status_code}", url)
                return {"success": False, "skipped": True, "reason": f"HTTP {resp.status_code}"}

            resp.raise_for_status()

            text, title = _extract_text(resp.text, url)
            if not text or len(text) < 100:
                _log_skip(skip_log, f"web_{url_hash_val}", "TooShort", url)
                return {"success": False, "skipped": True, "reason": "extracted text too short"}

            content = f"""---
source_id: web_{url_hash_val}
source_type: web
url: {url}
title: {title}
extracted_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
---

# {title}

{text}
"""
            out_file.write_text(content, encoding="utf-8")
            return {"success": True, "file": str(out_file), "chars": len(text)}

        except requests.exceptions.Timeout:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            _log_skip(skip_log, f"web_{url_hash_val}", "Timeout", url)
            return {"success": False, "skipped": True, "reason": "timeout"}
        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            _log_skip(skip_log, f"web_{url_hash_val}", f"Error:{type(e).__name__}", url)
            return {"success": False, "skipped": True, "reason": str(e)}

    return {"success": False, "reason": "max_retries_exceeded"}


def _extract_text(html: str, url: str) -> tuple[str, str]:
    title = ""
    text = ""

    # 1순위: trafilatura
    try:
        import trafilatura
        text = trafilatura.extract(html) or ""
        # 제목 추출
        from trafilatura.metadata import extract_metadata
        meta = extract_metadata(html)
        if meta:
            title = meta.title or ""
    except ImportError:
        pass

    # 2순위: BeautifulSoup
    if not text or len(text) < 100:
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            if not title:
                t = soup.find("title")
                title = t.get_text(strip=True) if t else url

            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()

            main = soup.find("article") or soup.find("main") or soup.find("body")
            if main:
                text = "\n\n".join(p.get_text(strip=True) for p in main.find_all(["p", "h1", "h2", "h3", "h4", "li"]) if p.get_text(strip=True))
        except ImportError:
            pass

    return text.strip(), title or url


def _log_skip(log_file: Path, source_id: str, reason: str, url: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    line = f"- {ts} | {source_id} | {reason} | {url}\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line)


def main():
    parser = argparse.ArgumentParser(description="웹 페이지 본문 추출기")
    parser.add_argument("--url", required=True, help="추출할 웹 URL")
    parser.add_argument("--url_hash", help="URL 해시 (없으면 자동 생성)")
    parser.add_argument("--output_dir", default="output/sources", help="출력 디렉토리")
    args = parser.parse_args()

    h = args.url_hash or url_hash(args.url)
    result = scrape(args.url, h, args.output_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("success") or result.get("skipped") else 1)


if __name__ == "__main__":
    main()
