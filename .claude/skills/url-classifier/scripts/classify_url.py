#!/usr/bin/env python3
"""URL 유형 분류기 — youtube 또는 web으로 분류"""

import re
import json
import hashlib
import argparse
from urllib.parse import urlparse, parse_qs


YOUTUBE_DOMAINS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}


def extract_video_id(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.netloc in ("youtu.be",):
        return parsed.path.lstrip("/").split("?")[0]
    qs = parse_qs(parsed.query)
    return qs.get("v", [None])[0]


def url_hash(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:10]


def classify(url: str) -> dict:
    url = url.strip()
    if not url:
        return {"url": url, "type": "error", "reason": "empty_url"}
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return {"url": url, "type": "error", "reason": "invalid_url"}
    except Exception:
        return {"url": url, "type": "error", "reason": "invalid_url"}

    domain = parsed.netloc.lower().lstrip("www.")
    if parsed.netloc.lower() in YOUTUBE_DOMAINS or domain in YOUTUBE_DOMAINS:
        video_id = extract_video_id(url)
        return {"url": url, "type": "youtube", "video_id": video_id or "unknown"}
    return {"url": url, "type": "web", "url_hash": url_hash(url)}


def main():
    parser = argparse.ArgumentParser(description="URL 유형 분류기")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--urls", help="쉼표로 구분된 URL 목록")
    group.add_argument("--file", help="URL 목록 파일 (한 줄에 하나)")
    args = parser.parse_args()

    if args.urls:
        urls = [u.strip() for u in args.urls.split(",") if u.strip()]
    else:
        with open(args.file, encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]

    results = [classify(url) for url in urls]
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
