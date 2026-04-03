#!/usr/bin/env python3
"""Tavily API 웹 검색 (주제 리서치 + 팩트체크)"""

import os
import sys
import json
import time
import argparse


def search(query: str, mode: str = "factcheck", max_results: int = None) -> dict:
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key or api_key == "your_tavily_api_key_here":
        return {"success": False, "error": "TAVILY_API_KEY 환경 변수가 설정되지 않았습니다."}

    try:
        from tavily import TavilyClient
    except ImportError:
        return {"success": False, "error": "tavily-python not installed. Run: pip install tavily-python"}

    client = TavilyClient(api_key=api_key)

    if mode == "research":
        search_depth = "advanced"
        if max_results is None:
            max_results = 5
    else:
        search_depth = "basic"
        if max_results is None:
            max_results = 3

    for attempt in range(3):
        try:
            response = client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results,
                include_answer=True,
            )
            results = [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", "")[:500],
                    "score": r.get("score", 0),
                }
                for r in response.get("results", [])
            ]
            return {
                "success": True,
                "query": query,
                "mode": mode,
                "answer": response.get("answer", ""),
                "results": results,
            }
        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            return {"success": False, "error": str(e), "skipped": True}

    return {"success": False, "error": "max_retries_exceeded", "skipped": True}


def main():
    parser = argparse.ArgumentParser(description="Tavily 웹 검색 (주제 리서치 + 팩트체크)")
    parser.add_argument("--query", required=True, help="검색어")
    parser.add_argument("--mode", choices=["research", "factcheck"], default="factcheck",
                        help="검색 모드: research(심층) 또는 factcheck(기본)")
    parser.add_argument("--max_results", type=int, default=None, help="최대 결과 수")
    args = parser.parse_args()

    # .env 로드
    from pathlib import Path
    env_path = Path(__file__).resolve().parents[4] / ".env"
    if env_path.exists():
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())

    result = search(args.query, args.mode, args.max_results)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
